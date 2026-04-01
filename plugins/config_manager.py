"""
统一配置管理模块
确保系统中所有功能模块的运行参数严格遵循用户在设置界面中配置的参数值
实现参数统一管理机制，防止硬编码参数或默认参数覆盖用户自定义设置
"""

import os
import json
from typing import Any, Dict, Optional, List, Callable, TypeVar, Generic, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import threading

T = TypeVar('T')


@dataclass
class ConfigSchema:
    """配置项架构定义"""
    key: str
    default: Any
    value_type: type
    description: str
    validator: Optional[Callable[[Any], bool]] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    options: Optional[List[Any]] = None  # 可选值列表


class ConfigValidator:
    """配置验证器"""

    @staticmethod
    def validate_type(value: Any, expected_type: type) -> bool:
        """验证类型"""
        if expected_type == int:
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == float:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == bool:
            return isinstance(value, bool)
        elif expected_type == str:
            return isinstance(value, str)
        elif expected_type == list:
            return isinstance(value, list)
        elif expected_type == dict:
            return isinstance(value, dict)
        return isinstance(value, expected_type)

    @staticmethod
    def validate_range(value: Any, min_val: Any, max_val: Any) -> bool:
        """验证范围"""
        try:
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True
        except TypeError:
            return False

    @staticmethod
    def validate_options(value: Any, options: List[Any]) -> bool:
        """验证是否在可选值列表中"""
        return value in options


class UnifiedConfigManager:
    """统一配置管理器
    
    管理所有模块的配置参数，确保：
    1. 所有配置都有默认值
    2. 用户配置优先于默认配置
    3. 配置变更时通知所有监听器
    4. 配置持久化到文件
    """

    _instance: Optional['UnifiedConfigManager'] = None
    _lock = threading.Lock()

    # 配置架构定义
    CONFIG_SCHEMAS: Dict[str, ConfigSchema] = {
        # Ollama 配置
        "ollama.host": ConfigSchema(
            key="ollama.host",
            default="127.0.0.1",
            value_type=str,
            description="Ollama服务器主机地址"
        ),
        "ollama.port": ConfigSchema(
            key="ollama.port",
            default=11434,
            value_type=int,
            description="Ollama服务器端口",
            min_value=1,
            max_value=65535
        ),
        "ollama.model": ConfigSchema(
            key="ollama.model",
            default="gemma3:1b",
            value_type=str,
            description="默认Ollama模型"
        ),
        "ollama.timeout": ConfigSchema(
            key="ollama.timeout",
            default=120,
            value_type=int,
            description="Ollama请求超时时间(秒)",
            min_value=10,
            max_value=600
        ),
        "ollama.use_knowledge": ConfigSchema(
            key="ollama.use_knowledge",
            default=True,
            value_type=bool,
            description="是否启用知识库"
        ),
        
        # 编辑器配置
        "editor.font_family": ConfigSchema(
            key="editor.font_family",
            default="Consolas",
            value_type=str,
            description="编辑器字体"
        ),
        "editor.font_size": ConfigSchema(
            key="editor.font_size",
            default=12,
            value_type=int,
            description="编辑器字体大小",
            min_value=8,
            max_value=32
        ),
        "editor.tab_size": ConfigSchema(
            key="editor.tab_size",
            default=4,
            value_type=int,
            description="Tab宽度",
            min_value=2,
            max_value=8
        ),
        "editor.word_wrap": ConfigSchema(
            key="editor.word_wrap",
            default=False,
            value_type=bool,
            description="自动换行"
        ),
        "editor.show_line_numbers": ConfigSchema(
            key="editor.show_line_numbers",
            default=True,
            value_type=bool,
            description="显示行号"
        ),
        "editor.auto_save": ConfigSchema(
            key="editor.auto_save",
            default=True,
            value_type=bool,
            description="自动保存"
        ),
        "editor.auto_save_interval": ConfigSchema(
            key="editor.auto_save_interval",
            default=5,
            value_type=int,
            description="自动保存间隔(分钟)",
            min_value=1,
            max_value=60
        ),
        
        # UI 配置
        "ui.theme": ConfigSchema(
            key="ui.theme",
            default="Modern Light",
            value_type=str,
            description="UI主题"
        ),
        "ui.syntax_theme": ConfigSchema(
            key="ui.syntax_theme",
            default="Default Light",
            value_type=str,
            description="语法高亮主题"
        ),
        "ui.language": ConfigSchema(
            key="ui.language",
            default="zh_CN",
            value_type=str,
            description="界面语言",
            options=["zh_CN", "en_US"]
        ),
        
        # 终端配置
        "terminal.font_size": ConfigSchema(
            key="terminal.font_size",
            default=11,
            value_type=int,
            description="终端字体大小",
            min_value=8,
            max_value=24
        ),
        "terminal.max_lines": ConfigSchema(
            key="terminal.max_lines",
            default=1000,
            value_type=int,
            description="终端最大行数",
            min_value=100,
            max_value=10000
        ),
        
        # 知识库配置
        "knowledge_base.similarity_threshold": ConfigSchema(
            key="knowledge_base.similarity_threshold",
            default=0.85,
            value_type=float,
            description="知识库相似度阈值",
            min_value=0.5,
            max_value=1.0
        ),
        "knowledge_base.auto_dedup": ConfigSchema(
            key="knowledge_base.auto_dedup",
            default=True,
            value_type=bool,
            description="自动去重"
        ),
        
        # 云同步配置
        "cloud_kb.server_url": ConfigSchema(
            key="cloud_kb.server_url",
            default="",
            value_type=str,
            description="云知识库服务器地址"
        ),
        "cloud_kb.api_key": ConfigSchema(
            key="cloud_kb.api_key",
            default="",
            value_type=str,
            description="云知识库API密钥"
        ),
        "cloud_kb.sync_enabled": ConfigSchema(
            key="cloud_kb.sync_enabled",
            default=False,
            value_type=bool,
            description="启用云同步"
        ),
    }

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._config: Dict[str, Any] = {}
        self._listeners: Dict[str, List[Callable[[str, Any], None]]] = {}
        self._lock = threading.RLock()
        
        # 配置文件路径
        self._config_file = self._get_config_file_path()
        
        # 初始化默认配置
        self._init_defaults()
        
        # 加载用户配置
        self._load_user_config()

    def _get_config_file_path(self) -> str:
        """获取配置文件路径"""
        # 优先使用应用目录
        app_dir = Path.home() / ".bbcode"
        app_dir.mkdir(exist_ok=True)
        return str(app_dir / "config.json")

    def _init_defaults(self):
        """初始化默认配置"""
        with self._lock:
            for schema in self.CONFIG_SCHEMAS.values():
                self._config[schema.key] = schema.default

    def _load_user_config(self):
        """加载用户配置"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 验证并应用用户配置
                for key, value in user_config.items():
                    if key in self.CONFIG_SCHEMAS:
                        schema = self.CONFIG_SCHEMAS[key]
                        if self._validate_value(value, schema):
                            self._config[key] = value
                        else:
                            print(f"配置验证失败: {key}={value}，使用默认值")
        except Exception as e:
            print(f"加载用户配置失败: {e}")

    def _validate_value(self, value: Any, schema: ConfigSchema) -> bool:
        """验证配置值"""
        # 类型验证
        if not ConfigValidator.validate_type(value, schema.value_type):
            return False
        
        # 范围验证
        if schema.min_value is not None or schema.max_value is not None:
            if not ConfigValidator.validate_range(value, schema.min_value, schema.max_value):
                return False
        
        # 选项验证
        if schema.options is not None:
            if not ConfigValidator.validate_options(value, schema.options):
                return False
        
        # 自定义验证器
        if schema.validator is not None:
            if not schema.validator(value):
                return False
        
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键
            default: 默认值（如果配置不存在）
        
        Returns:
            配置值
        """
        with self._lock:
            if key in self._config:
                return self._config[key]
            
            # 如果不在当前配置中，检查架构定义
            if key in self.CONFIG_SCHEMAS:
                return self.CONFIG_SCHEMAS[key].default
            
            return default

    def set(self, key: str, value: Any, validate: bool = True) -> bool:
        """设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            validate: 是否验证值
        
        Returns:
            是否设置成功
        """
        with self._lock:
            # 验证值
            if validate and key in self.CONFIG_SCHEMAS:
                schema = self.CONFIG_SCHEMAS[key]
                if not self._validate_value(value, schema):
                    print(f"配置值验证失败: {key}={value}")
                    return False
            
            old_value = self._config.get(key)
            self._config[key] = value
            
            # 通知监听器
            if old_value != value:
                self._notify_listeners(key, value)
            
            return True

    def reset_to_default(self, key: str) -> bool:
        """重置配置为默认值"""
        with self._lock:
            if key in self.CONFIG_SCHEMAS:
                schema = self.CONFIG_SCHEMAS[key]
                return self.set(key, schema.default)
            return False

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        with self._lock:
            return self._config.copy()

    def save(self) -> bool:
        """保存配置到文件"""
        try:
            with self._lock:
                with open(self._config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def add_listener(self, key: str, callback: Callable[[str, Any], None]):
        """添加配置变更监听器
        
        Args:
            key: 配置键，支持通配符 "*" 监听所有配置
            callback: 回调函数，接收 (key, value) 参数
        """
        with self._lock:
            if key not in self._listeners:
                self._listeners[key] = []
            self._listeners[key].append(callback)

    def remove_listener(self, key: str, callback: Callable[[str, Any], None]):
        """移除配置变更监听器"""
        with self._lock:
            if key in self._listeners and callback in self._listeners[key]:
                self._listeners[key].remove(callback)

    def _notify_listeners(self, key: str, value: Any):
        """通知监听器配置变更"""
        # 通知特定键的监听器
        if key in self._listeners:
            for callback in self._listeners[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    print(f"配置监听器错误: {e}")
        
        # 通知通配符监听器
        if "*" in self._listeners:
            for callback in self._listeners["*"]:
                try:
                    callback(key, value)
                except Exception as e:
                    print(f"配置监听器错误: {e}")

    def get_schema(self, key: str) -> Optional[ConfigSchema]:
        """获取配置架构"""
        return self.CONFIG_SCHEMAS.get(key)

    def get_all_schemas(self) -> Dict[str, ConfigSchema]:
        """获取所有配置架构"""
        return self.CONFIG_SCHEMAS.copy()

    def import_from_dict(self, config_dict: Dict[str, Any]) -> Tuple[int, int]:
        """从字典导入配置
        
        Returns:
            (成功数量, 失败数量) 元组
        """
        success = 0
        failed = 0
        
        for key, value in config_dict.items():
            if self.set(key, value):
                success += 1
            else:
                failed += 1
        
        return success, failed

    def export_to_dict(self) -> Dict[str, Any]:
        """导出配置为字典"""
        return self.get_all()


# 全局配置管理器实例
def get_config_manager() -> UnifiedConfigManager:
    """获取配置管理器实例"""
    return UnifiedConfigManager()


# 便捷函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置值"""
    return get_config_manager().get(key, default)


def set_config(key: str, value: Any, validate: bool = True) -> bool:
    """设置配置值"""
    return get_config_manager().set(key, value, validate)


def save_config() -> bool:
    """保存配置"""
    return get_config_manager().save()


def add_config_listener(key: str, callback: Callable[[str, Any], None]):
    """添加配置变更监听器"""
    get_config_manager().add_listener(key, callback)


def remove_config_listener(key: str, callback: Callable[[str, Any], None]):
    """移除配置变更监听器"""
    get_config_manager().remove_listener(key, callback)


# 模块配置适配器
class ModuleConfigAdapter:
    """模块配置适配器
    
    为特定模块提供配置访问接口，确保模块使用统一的配置管理
    """
    
    def __init__(self, module_prefix: str):
        self.module_prefix = module_prefix
        self._manager = get_config_manager()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        full_key = f"{self.module_prefix}.{key}"
        return self._manager.get(full_key, default)
    
    def set(self, key: str, value: Any, validate: bool = True) -> bool:
        """设置配置值"""
        full_key = f"{self.module_prefix}.{key}"
        return self._manager.set(full_key, value, validate)
    
    def add_listener(self, key: str, callback: Callable[[str, Any], None]):
        """添加监听器"""
        full_key = f"{self.module_prefix}.{key}"
        self._manager.add_listener(full_key, callback)


# 特定模块的配置适配器
def get_ollama_config() -> ModuleConfigAdapter:
    """获取Ollama模块配置适配器"""
    return ModuleConfigAdapter("ollama")


def get_editor_config() -> ModuleConfigAdapter:
    """获取编辑器模块配置适配器"""
    return ModuleConfigAdapter("editor")


def get_ui_config() -> ModuleConfigAdapter:
    """获取UI模块配置适配器"""
    return ModuleConfigAdapter("ui")


def get_terminal_config() -> ModuleConfigAdapter:
    """获取终端模块配置适配器"""
    return ModuleConfigAdapter("terminal")


def get_kb_config() -> ModuleConfigAdapter:
    """获取知识库模块配置适配器"""
    return ModuleConfigAdapter("knowledge_base")


# 配置迁移工具
class ConfigMigration:
    """配置迁移工具
    
    用于从旧版配置系统迁移到新版统一配置系统
    """
    
    @staticmethod
    def migrate_from_thonny_workbench():
        """从Thonny Workbench迁移配置"""
        try:
            from thonny import get_workbench
            wb = get_workbench()
            manager = get_config_manager()
            
            # 映射旧配置键到新配置键
            migration_map = {
                "assistance.ollama_host": "ollama.host",
                "assistance.ollama_port": "ollama.port",
                "assistance.ollama_model": "ollama.model",
                "assistance.ollama_timeout": "ollama.timeout",
                "assistance.use_knowledge": "ollama.use_knowledge",
                "view.ui_theme": "ui.theme",
                "view.syntax_theme": "ui.syntax_theme",
                "view.editor_font_family": "editor.font_family",
                "view.editor_font_size": "editor.font_size",
                "edit.tab_size": "editor.tab_size",
                "general.language": "ui.language",
            }
            
            for old_key, new_key in migration_map.items():
                try:
                    old_value = wb.get_option(old_key)
                    if old_value is not None:
                        manager.set(new_key, old_value)
                except:
                    pass
            
            manager.save()
            print("配置迁移完成")
            
        except Exception as e:
            print(f"配置迁移失败: {e}")


# 初始化函数
def initialize_config_system():
    """初始化配置系统"""
    manager = get_config_manager()
    
    # 尝试从旧系统迁移配置
    ConfigMigration.migrate_from_thonny_workbench()
    
    return manager


if __name__ == "__main__":
    # 测试代码
    manager = initialize_config_system()
    
    print("当前配置:")
    for key, value in manager.get_all().items():
        print(f"  {key}: {value}")
    
    # 测试配置变更
    print("\n测试配置变更:")
    manager.set("ollama.model", "test-model")
    print(f"  ollama.model = {manager.get('ollama.model')}")
    
    # 测试监听器
    def on_config_change(key: str, value: Any):
        print(f"  配置变更: {key} = {value}")
    
    manager.add_listener("ollama.model", on_config_change)
    manager.set("ollama.model", "new-model")
