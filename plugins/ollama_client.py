# -*- coding: utf-8 -*-
"""
BBCode Ollama API 客户端
用于集成本地 Ollama AI 模型
"""

import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Callable, Generator
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# 导入配置系统
try:
    from thonny.qt_config import get_option, set_option
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


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
    """Ollama API 客户端"""
    
    DEFAULT_HOST = "http://localhost:11434"
    CONFIG_KEY = "ai.ollama_host"
    
    def __init__(self, host: str = None):
        # 优先使用传入的 host，其次使用配置，最后使用默认值
        if host:
            self.host = host
        elif CONFIG_AVAILABLE and get_option(self.CONFIG_KEY):
            self.host = get_option(self.CONFIG_KEY)
        else:
            self.host = self.DEFAULT_HOST
        
        self.model = "qwen2.5-coder:7b"  # 默认使用代码模型
    
    def set_host(self, host: str):
        """设置主机地址并保存到配置"""
        self.host = host
        if CONFIG_AVAILABLE:
            set_option(self.CONFIG_KEY, host)
    
    def get_host(self) -> str:
        """获取当前主机地址"""
        return self.host
    
    def set_model(self, model: str):
        """设置模型"""
        self.model = model
    
    def set_model(self, model: str):
        """设置模型"""
        self.model = model
    
    def list_models(self) -> List[Dict]:
        """获取可用模型列表"""
        try:
            url = f"{self.host}/api/tags"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('models', [])
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def generate(self, prompt: str, system: str = None, options: OllamaOptions = None) -> str:
        """生成文本（同步）"""
        url = f"{self.host}/api/generate"
        
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
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def generate_stream(self, prompt: str, system: str = None, options: OllamaOptions = None) -> Generator[str, None, None]:
        """生成文本（流式）"""
        url = f"{self.host}/api/generate"
        
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
        except Exception as e:
            raise Exception(f"Stream request failed: {e}")
    
    def chat(self, messages: List[OllamaMessage], options: OllamaOptions = None) -> str:
        """对话模式（同步）"""
        url = f"{self.host}/api/chat"
        
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
        except Exception as e:
            raise Exception(f"Chat request failed: {e}")
    
    def is_available(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            url = f"{self.host}/api/tags"
            with urllib.request.urlopen(url, timeout=2) as response:
                return response.status == 200
        except:
            return False


class OllamaWorker(QThread):
    """Ollama 后台工作线程"""
    
    response_ready = pyqtSignal(str)
    response_chunk = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, api: OllamaAPI):
        super().__init__()
        self.api = api
        self.prompt = ""
        self.system = ""
        self.use_stream = True
        self._running = False
    
    def set_prompt(self, prompt: str, system: str = ""):
        """设置提示词"""
        self.prompt = prompt
        self.system = system
    
    def run(self):
        """运行生成"""
        self._running = True
        
        try:
            if self.use_stream:
                # 流式生成
                for chunk in self.api.generate_stream(self.prompt, self.system):
                    if not self._running:
                        break
                    self.response_chunk.emit(chunk)
            else:
                # 同步生成
                response = self.api.generate(self.prompt, self.system)
                self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished_signal.emit()
    
    def stop(self):
        """停止生成"""
        self._running = False


class OllamaChatManager(QObject):
    """Ollama 聊天管理器"""
    
    message_received = pyqtSignal(str)
    message_chunk = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.api = OllamaAPI()
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
    
    def set_model(self, model: str):
        """设置模型"""
        self.api.set_model(model)
    
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
        self.worker.response_chunk.connect(self._on_chunk)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.finished_signal.connect(self._on_finished)
        
        # 启动线程
        self.worker.start()
    
    def _on_chunk(self, chunk: str):
        """接收流式响应块"""
        self.message_chunk.emit(chunk)
    
    def _on_error(self, error: str):
        """处理错误"""
        self.error_occurred.emit(error)
    
    def _on_finished(self):
        """生成完成"""
        pass
    
    def stop_generation(self):
        """停止生成"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)


# 便捷函数
def create_ollama_client() -> OllamaAPI:
    """创建 Ollama 客户端"""
    return OllamaAPI()


def check_ollama_status() -> Dict[str, any]:
    """检查 Ollama 状态"""
    api = OllamaAPI()
    return {
        "available": api.is_available(),
        "models": api.list_models() if api.is_available() else [],
        "default_model": api.model
    }


if __name__ == "__main__":
    # 测试代码
    print("Checking Ollama status...")
    status = check_ollama_status()
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
