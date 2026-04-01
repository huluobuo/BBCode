# -*- coding: utf-8 -*-
"""
BBCode Ollama API 客户端
用于集成本地或远程 Ollama AI 模型
"""

import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Callable, Generator
from dataclasses import dataclass
import threading

# 导入配置系统 - 使用Thonny的配置系统
try:
    from thonny import get_workbench
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


def get_option(key: str, default=None):
    """获取配置选项"""
    if CONFIG_AVAILABLE:
        try:
            return get_workbench().get_option(key, default)
        except:
            pass
    return default


def set_option(key: str, value):
    """设置配置选项"""
    if CONFIG_AVAILABLE:
        try:
            get_workbench().set_option(key, value)
        except:
            pass


@dataclass
class OllamaMessage:
    """Ollama 消息"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class OllamaOptions:
    """Ollama 生成选项"""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    num_predict: int = 2048
    stop: Optional[List[str]] = None


class OllamaAPI:
    """Ollama API 客户端 - 支持远程服务器连接"""
    
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 11434
    CONFIG_KEY_HOST = "assistance.ollama_host"
    CONFIG_KEY_PORT = "assistance.ollama_port"
    CONFIG_KEY_MODEL = "assistance.ollama_model"
    
    def __init__(self, host: str = None, port: int = None, model: str = None):
        """
        初始化Ollama API客户端
        
        Args:
            host: 服务器主机地址，优先使用传入值，其次配置，最后默认值
            port: 服务器端口，优先使用传入值，其次配置，最后默认值
            model: 模型名称，优先使用传入值，其次配置，最后默认值
        """
        # 先设置默认端口
        self.port = self.DEFAULT_PORT
        
        # 解析主机地址（可能包含端口）
        if host:
            self.host, extracted_port = self._normalize_host(host)
            if extracted_port is not None:
                self.port = extracted_port
        elif get_option(self.CONFIG_KEY_HOST):
            self.host, extracted_port = self._normalize_host(get_option(self.CONFIG_KEY_HOST))
            if extracted_port is not None:
                self.port = extracted_port
        else:
            self.host = self.DEFAULT_HOST
        
        # 解析端口（传入的参数优先级最高）
        if port is not None:
            # 验证端口范围
            if isinstance(port, int) and 1 <= port <= 65535:
                self.port = port
            else:
                self.port = self.DEFAULT_PORT
        else:
            port_val = get_option(self.CONFIG_KEY_PORT)
            if port_val:
                try:
                    port_int = int(port_val)
                    if 1 <= port_int <= 65535:
                        self.port = port_int
                except (ValueError, TypeError):
                    pass  # 保持默认端口
        
        # 构建完整的基础URL
        self.base_url = self._build_base_url()
        
        # 设置模型
        if model:
            self.model = model
        elif get_option(self.CONFIG_KEY_MODEL):
            self.model = get_option(self.CONFIG_KEY_MODEL)
        else:
            self.model = "gemma3:1b"
    
    def _normalize_host(self, host: str) -> tuple[str, Optional[int]]:
        """规范化主机地址，返回(主机, 端口)元组"""
        host = host.strip()
        extracted_port = None
        
        # 移除协议前缀（如果存在）
        if host.startswith('http://'):
            host = host[7:]
        elif host.startswith('https://'):
            host = host[8:]
        
        # 移除末尾的斜杠
        host = host.rstrip('/')
        
        # 分离主机和端口
        if ':' in host:
            parts = host.split(':')
            if len(parts) == 2:
                host = parts[0]
                try:
                    port = int(parts[1])
                    if 1 <= port <= 65535:
                        extracted_port = port
                except ValueError:
                    pass
        
        return host, extracted_port
    
    def _build_base_url(self) -> str:
        """构建基础URL"""
        return f"http://{self.host}:{self.port}"
    
    def set_host(self, host: str, port: int = None):
        """设置主机地址并保存到配置"""
        self.host = self._normalize_host(host)
        if port is not None:
            self.port = port
        self.base_url = self._build_base_url()
        
        set_option(self.CONFIG_KEY_HOST, self.host)
        set_option(self.CONFIG_KEY_PORT, self.port)
    
    def get_host(self) -> str:
        """获取当前主机地址"""
        return self.host
    
    def get_port(self) -> int:
        """获取当前端口"""
        return self.port
    
    def get_base_url(self) -> str:
        """获取完整的基础URL"""
        return self.base_url
    
    def set_model(self, model: str):
        """设置模型"""
        self.model = model
        set_option(self.CONFIG_KEY_MODEL, model)
    
    def get_model(self) -> str:
        """获取当前模型"""
        return self.model
    
    def list_models(self) -> List[Dict]:
        """获取可用模型列表"""
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url, method='GET')
            req.add_header('Accept', 'application/json')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('models', [])
        except urllib.error.URLError as e:
            print(f"连接错误: 无法连接到 {self.base_url} - {e}")
            return []
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []
    
    def generate(self, prompt: str, system: str = None, options: OllamaOptions = None) -> str:
        """生成文本（同步）"""
        url = f"{self.base_url}/api/generate"
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            data["system"] = system
        
        if options:
            data["options"] = {
                "temperature": options.temperature,
                "top_p": options.top_p,
                "top_k": options.top_k,
                "num_predict": options.num_predict,
            }
            if options.stop:
                data["options"]["stop"] = options.stop
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"HTTP Error {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"连接失败: 无法连接到 {self.base_url} - {e}")
        except Exception as e:
            raise Exception(f"请求失败: {e}")
    
    def generate_stream(self, prompt: str, system: str = None, options: OllamaOptions = None) -> Generator[str, None, None]:
        """生成文本（流式）"""
        url = f"{self.base_url}/api/generate"
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        
        if system:
            data["system"] = system
        
        if options:
            data["options"] = {
                "temperature": options.temperature,
                "top_p": options.top_p,
                "top_k": options.top_k,
                "num_predict": options.num_predict,
            }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                for line in response:
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                yield chunk['response']
                            if chunk.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
        except urllib.error.URLError as e:
            raise Exception(f"连接失败: 无法连接到 {self.base_url} - {e}")
        except Exception as e:
            raise Exception(f"流式请求失败: {e}")
    
    def chat(self, messages: List[OllamaMessage], options: OllamaOptions = None) -> str:
        """对话模式（同步）"""
        url = f"{self.base_url}/api/chat"
        
        data = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False
        }
        
        if options:
            data["options"] = {
                "temperature": options.temperature,
                "top_p": options.top_p,
                "top_k": options.top_k,
                "num_predict": options.num_predict,
            }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('message', {}).get('content', '')
        except urllib.error.URLError as e:
            raise Exception(f"连接失败: 无法连接到 {self.base_url} - {e}")
        except Exception as e:
            raise Exception(f"对话请求失败: {e}")
    
    def is_available(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except:
            return False
    
    def get_connection_info(self) -> Dict[str, any]:
        """获取连接信息"""
        return {
            "host": self.host,
            "port": self.port,
            "base_url": self.base_url,
            "model": self.model,
            "available": self.is_available()
        }


class OllamaWorker:
    """Ollama 后台工作线程 - 使用threading替代PyQt6"""
    
    def __init__(self, api: OllamaAPI):
        self.api = api
        self.prompt = ""
        self.system = ""
        self.use_stream = True
        self._running = False
        self._thread = None
        self._callbacks = {
            'chunk': [],
            'error': [],
            'finished': []
        }
    
    def set_prompt(self, prompt: str, system: str = ""):
        """设置提示词"""
        self.prompt = prompt
        self.system = system
    
    def connect_chunk(self, callback):
        """连接chunk信号"""
        self._callbacks['chunk'].append(callback)
    
    def connect_error(self, callback):
        """连接error信号"""
        self._callbacks['error'].append(callback)
    
    def connect_finished(self, callback):
        """连接finished信号"""
        self._callbacks['finished'].append(callback)
    
    def _emit_chunk(self, chunk: str):
        """发射chunk信号"""
        for callback in self._callbacks['chunk']:
            try:
                callback(chunk)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _emit_error(self, error: str):
        """发射error信号"""
        for callback in self._callbacks['error']:
            try:
                callback(error)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _emit_finished(self):
        """发射finished信号"""
        for callback in self._callbacks['finished']:
            try:
                callback()
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _run(self):
        """运行生成"""
        self._running = True
        
        try:
            if self.use_stream:
                # 流式生成
                for chunk in self.api.generate_stream(self.prompt, self.system):
                    if not self._running:
                        break
                    self._emit_chunk(chunk)
            else:
                # 同步生成
                response = self.api.generate(self.prompt, self.system)
                self._emit_chunk(response)
        except Exception as e:
            self._emit_error(str(e))
        finally:
            self._emit_finished()
            self._running = False
    
    def start(self):
        """启动线程"""
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self):
        """停止生成"""
        self._running = False
    
    def isRunning(self) -> bool:
        """检查是否正在运行"""
        return self._running and self._thread and self._thread.is_alive()
    
    def wait(self, timeout: float = None) -> bool:
        """等待线程完成"""
        if self._thread:
            self._thread.join(timeout)
            return not self._thread.is_alive()
        return True


class OllamaChatManager:
    """Ollama 聊天管理器 - 不使用PyQt6"""
    
    def __init__(self, host: str = None, port: int = None, model: str = None):
        self.api = OllamaAPI(host=host, port=port, model=model)
        self.worker: Optional[OllamaWorker] = None
        self.conversation_history: List[OllamaMessage] = []
        self.system_prompt = """你是一个专业的AI编程助手，集成在BBCode Python IDE中。

重要规则：
1. 必须使用中文回答所有问题
2. 提供清晰、简洁的解释
3. 使用代码示例时，必须用 ```python 格式
4. 保持友好和鼓励的态度
5. 解释代码时要详细说明每一部分的功能
6. 如果代码有错误，指出错误原因并给出修正方案

当前环境：BBCode Python IDE，用户正在编写Python代码。

回答格式：
- 先给出总体说明
- 然后提供代码示例（如有必要）
- 最后解释关键点"""
        self._callbacks = {
            'message_chunk': [],
            'error': []
        }
    
    def connect_message_chunk(self, callback):
        """连接message_chunk信号"""
        self._callbacks['message_chunk'].append(callback)
    
    def connect_error(self, callback):
        """连接error信号"""
        self._callbacks['error'].append(callback)
    
    def set_host(self, host: str, port: int = None):
        """设置服务器地址"""
        self.api.set_host(host, port)
    
    def get_host(self) -> str:
        """获取当前主机地址"""
        return self.api.get_host()
    
    def get_port(self) -> int:
        """获取当前端口"""
        return self.api.get_port()
    
    def set_model(self, model: str):
        """设置模型"""
        self.api.set_model(model)
    
    def get_model(self) -> str:
        """获取当前模型"""
        return self.api.get_model()
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        models = self.api.list_models()
        return [m.get('name', '') for m in models]
    
    def is_available(self) -> bool:
        """检查 Ollama 是否可用"""
        return self.api.is_available()
    
    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = prompt
    
    def get_system_prompt(self) -> str:
        """获取当前系统提示词"""
        return self.system_prompt
    
    def send_message(self, message: str, code_context: str = ""):
        """发送消息"""
        # 构建提示词
        prompt = message
        if code_context:
            prompt = f"用户问题：{message}\n\n相关代码：\n```python\n{code_context}\n```"
        
        # 创建后台线程
        self.worker = OllamaWorker(self.api)
        self.worker.set_prompt(prompt, self.system_prompt)
        self.worker.use_stream = True
        
        # 连接信号
        self.worker.connect_chunk(self._on_chunk)
        self.worker.connect_error(self._on_error)
        self.worker.connect_finished(self._on_finished)
        
        # 启动线程
        self.worker.start()
    
    def _on_chunk(self, chunk: str):
        """接收流式响应块"""
        for callback in self._callbacks['message_chunk']:
            try:
                callback(chunk)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _on_error(self, error: str):
        """处理错误"""
        for callback in self._callbacks['error']:
            try:
                callback(error)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _on_finished(self):
        """生成完成"""
        pass
    
    def stop_generation(self):
        """停止生成"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)


# 便捷函数
def create_ollama_client(host: str = None, port: int = None, model: str = None) -> OllamaAPI:
    """创建 Ollama 客户端"""
    return OllamaAPI(host=host, port=port, model=model)


def check_ollama_status(host: str = None, port: int = None) -> Dict[str, any]:
    """检查 Ollama 状态"""
    api = OllamaAPI(host=host, port=port)
    return {
        "available": api.is_available(),
        "connection_info": api.get_connection_info(),
        "models": api.list_models() if api.is_available() else []
    }


def test_remote_connection(host: str, port: int = 11434) -> tuple[bool, str]:
    """测试远程连接
    
    Returns:
        (success, message) 元组
    """
    try:
        api = OllamaAPI(host=host, port=port)
        if api.is_available():
            models = api.list_models()
            model_names = [m.get('name', '') for m in models[:5]]
            return True, f"连接成功！可用模型: {', '.join(model_names) if model_names else '无'}"
        else:
            return False, f"无法连接到 {host}:{port}"
    except Exception as e:
        return False, f"连接失败: {str(e)}"


if __name__ == "__main__":
    # 测试代码
    print("Checking Ollama status...")
    status = check_ollama_status()
    print(f"Connection Info: {status['connection_info']}")
    print(f"Available: {status['available']}")
    print(f"Models: {status['models']}")
    
    if status['available']:
        print("\nTesting generate...")
        api = OllamaAPI()
        try:
            response = api.generate("Hello, how are you?")
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
