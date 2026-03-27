# -*- coding: utf-8 -*-
"""
BBCode PyQt6 配置系统
替代原版的 config.py
"""

import os
import json
import sys
from pathlib import Path
from typing import Any, Optional, Dict, Callable, List
from PyQt6.QtCore import QSettings, QObject, pyqtSignal


class ConfigManager(QObject):
    """配置管理器 - 替代原版的 Configuration"""
    
    # 信号
    config_changed = pyqtSignal(str, object)  # key, value
    
    def __init__(self):
        super().__init__()
        
        # 使用 QSettings 存储配置
        self._settings = QSettings("BBCode", "PyQt6Edition")
        
        # 内存中的缓存
        self._cache: Dict[str, Any] = {}
        
        # 变更监听器
        self._listeners: Dict[str, List[Callable]] = {}
        
        # 加载默认配置
        self._init_defaults()
    
    def _init_defaults(self):
        """初始化默认配置"""
        defaults = {
            # 编辑器设置
            "view.editor_font_family": "Consolas",
            "view.editor_font_size": 12,
            "view.io_font_family": "Consolas",
            "view.io_font_size": 11,
            "view.syntax_coloring": True,
            "view.line_numbers": True,
            "view.highlight_current_line": True,
            "view.show_line_endings": False,
            
            # UI 设置
            "view.ui_theme": "dark",
            "view.full_screen": False,
            "view.maximize_view": False,
            
            # 运行设置
            "run.working_directory": str(Path.home()),
            "run.backend_name": "LocalCPython",
            "run.auto_save": True,
            
            # Shell 设置
            "shell.clear_before_run": False,
            "shell.max_lines": 1000,
            
            # 编辑器行为
            "edit.indent_with_tabs": False,
            "edit.tab_size": 4,
            "edit.auto_complete": True,
            "edit.auto_complete_in_strings": True,
            "edit.auto_complete_in_comments": False,
            
            # 通用设置
            "general.language": "zh_CN",
            "general.single_instance": True,
            "general.event_logging": False,
            "general.debug_mode": False,
        }
        
        # 只设置不存在的默认值
        for key, value in defaults.items():
            if not self._settings.contains(key):
                self._settings.setValue(key, value)
    
    def get_option(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        # 先检查缓存
        if key in self._cache:
            return self._cache[key]
        
        # 从 QSettings 读取
        value = self._settings.value(key, default)
        
        # 缓存值
        self._cache[key] = value
        
        return value
    
    def set_option(self, key: str, value: Any, save: bool = True):
        """设置配置项"""
        old_value = self.get_option(key)
        
        # 更新缓存
        self._cache[key] = value
        
        # 保存到 QSettings
        if save:
            self._settings.setValue(key, value)
        
        # 发送信号
        if old_value != value:
            self.config_changed.emit(key, value)
            
            # 通知监听器
            if key in self._listeners:
                for callback in self._listeners[key]:
                    try:
                        callback(value)
                    except Exception as e:
                        print(f"Error in config listener: {e}")
    
    def has_option(self, key: str) -> bool:
        """检查配置项是否存在"""
        return self._settings.contains(key)
    
    def remove_option(self, key: str):
        """删除配置项"""
        self._settings.remove(key)
        if key in self._cache:
            del self._cache[key]
    
    def add_change_listener(self, key: str, callback: Callable):
        """添加配置变更监听器"""
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(callback)
    
    def remove_change_listener(self, key: str, callback: Callable):
        """移除配置变更监听器"""
        if key in self._listeners and callback in self._listeners[key]:
            self._listeners[key].remove(callback)
    
    def save(self):
        """保存所有配置"""
        self._settings.sync()
    
    def export_to_file(self, filepath: str):
        """导出配置到文件"""
        config = {}
        for key in self._settings.allKeys():
            config[key] = self._settings.value(key)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def import_from_file(self, filepath: str):
        """从文件导入配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for key, value in config.items():
            self.set_option(key, value)
        
        self.save()
    
    def get_all_keys(self) -> List[str]:
        """获取所有配置键"""
        return list(self._settings.allKeys())


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_option(key: str, default: Any = None) -> Any:
    """便捷函数：获取配置项"""
    return get_config_manager().get_option(key, default)


def set_option(key: str, value: Any):
    """便捷函数：设置配置项"""
    get_config_manager().set_option(key, value)


def has_option(key: str) -> bool:
    """便捷函数：检查配置项是否存在"""
    return get_config_manager().has_option(key)


# 为了兼容性，提供与原版的别名
class Configuration:
    """兼容原版的 Configuration 类"""
    
    def get_option(self, key: str, default: Any = None) -> Any:
        return get_option(key, default)
    
    def set_option(self, key: str, value: Any):
        set_option(key, value)
    
    def has_option(self, key: str) -> bool:
        return has_option(key)


def try_load_configuration():
    """兼容原版的配置加载函数"""
    return Configuration()
