"""
Ollama AI助手集成
提供本地AI模型支持，集成知识库功能
"""

import urllib.error
from typing import Iterator, Optional

from thonny import get_workbench
from thonny.assistance import Assistant, ChatContext, ChatResponseChunk

# 系统提示词 - 中文回答和编程教学
SYSTEM_PROMPT = """你是一个专业的编程助手。请遵守以下规则：

1. **语言要求**：你必须用中文回答所有问题。

2. **文件操作**：支持查看和修改当前编辑的文件。

3. **知识库**：当提供相关知识库内容时，请结合这些知识来回答问题。

4. **回答格式**：
   - 使用Markdown格式
   - 代码块使用```python标记
   - 重要内容使用**粗体**标记

5. **编程教学**：
   - 详细解释代码每一行
   - 提供多种方案时说明优缺点
   - 鼓励用户多尝试

所有回答必须是中文！"""


class OllamaAssistant(Assistant):
    """Ollama AI助手"""

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = "11434"
    DEFAULT_MODEL = "gemma3:1b"

    def __init__(self):
        self._is_ready = False
        self._tested_connection = False
        self._client = None
        self._knowledge_base = None

    def _get_knowledge_base(self):
        """获取知识库实例（懒加载）"""
        if self._knowledge_base is None:
            from thonny.plugins.knowledge_base import get_knowledge_base

            self._knowledge_base = get_knowledge_base()
        return self._knowledge_base

    def get_ready(self) -> bool:
        if not self._tested_connection:
            self._test_connection()
        return self._is_ready

    def _get_config(self) -> dict:
        """获取配置"""
        return {
            "host": get_workbench().get_option("assistance.ollama_host", self.DEFAULT_HOST),
            "port": get_workbench().get_option("assistance.ollama_port", self.DEFAULT_PORT),
            "model": get_workbench().get_option("assistance.ollama_model", self.DEFAULT_MODEL),
            "use_knowledge": get_workbench().get_option("assistance.use_knowledge", True),
        }

    def _test_connection(self) -> None:
        """测试Ollama连接"""
        try:
            import ollama

            config = self._get_config()
            client = ollama.Client(host=f"{config['host']}:{config['port']}")
            client.list()

            self._is_ready = True
            print(f"Ollama连接成功: {config['host']}:{config['port']}")

            # 初始化知识库
            try:
                kb = self._get_knowledge_base()
                files = kb.list_knowledge_files()
                if files:
                    print(f"知识库已加载，包含 {len(files)} 个文件")
            except Exception as e:
                print(f"知识库加载失败: {e}")

        except ImportError:
            print("未安装ollama库，请运行: pip install ollama")
        except urllib.error.URLError as e:
            config = self._get_config()
            print(f"无法连接到Ollama ({config['host']}:{config['port']}): {e}")
        except Exception as e:
            print(f"Ollama连接错误: {e}")

        self._tested_connection = True

    def _get_knowledge_context(self, query: str) -> str:
        """获取与查询相关的知识上下文"""
        config = self._get_config()
        if not config.get("use_knowledge", True):
            return ""

        try:
            kb = self._get_knowledge_base()
            context = kb.get_context_for_query(query, max_length=3000)
            return context
        except Exception as e:
            print(f"获取知识库上下文失败: {e}")
            return ""

    def complete_chat(self, context: ChatContext) -> Iterator[ChatResponseChunk]:
        """完成对话"""
        try:
            import ollama

            config = self._get_config()
            client = ollama.Client(host=f"{config['host']}:{config['port']}")

            # 获取最后一条用户消息
            last_user_message = ""
            for msg in reversed(context.messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break

            # 获取知识库上下文
            knowledge_context = ""
            if last_user_message:
                knowledge_context = self._get_knowledge_context(last_user_message)

            # 构建系统提示词
            system_content = SYSTEM_PROMPT
            if knowledge_context:
                system_content += f"\n\n{knowledge_context}"

            # 构建消息
            messages = [{"role": "system", "content": system_content}]
            messages.extend(
                [{"role": msg.role, "content": msg.content} for msg in context.messages]
            )

            # 流式请求
            stream = client.chat(
                model=config["model"],
                messages=messages,
                stream=True,
            )

            for chunk in stream:
                if content := chunk.get("message", {}).get("content"):
                    yield ChatResponseChunk(content, is_final=False)

            yield ChatResponseChunk("", is_final=True)

        except Exception as e:
            yield ChatResponseChunk(f"Ollama请求失败: {str(e)}", is_final=False)
            yield ChatResponseChunk("", is_final=True)

    def cancel_completion(self) -> None:
        pass


def load_plugin():
    """加载插件"""
    # 设置默认值
    get_workbench().set_default("assistance.ollama_host", OllamaAssistant.DEFAULT_HOST)
    get_workbench().set_default("assistance.ollama_port", OllamaAssistant.DEFAULT_PORT)
    get_workbench().set_default("assistance.ollama_model", OllamaAssistant.DEFAULT_MODEL)
    get_workbench().set_default("assistance.use_knowledge", True)

    # 注册助手
    get_workbench().add_assistant("ollama", OllamaAssistant())
