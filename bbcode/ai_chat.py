# -*- coding: utf-8 -*-
"""
BBCode AI 聊天组件
支持 Ollama 本地模型
"""

import json
import urllib.request
import urllib.error
import threading
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QComboBox, QScrollArea, QFrame,
    QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QColor


@dataclass
class Message:
    """聊天消息"""
    role: str  # "user" or "assistant"
    content: str


class OllamaAPI:
    """Ollama API 客户端"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.default_model = "qwen2.5-coder:7b"
    
    def is_available(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            req = urllib.request.Request(
                f"{self.host}/api/tags",
                method="GET",
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            req = urllib.request.Request(
                f"{self.host}/api/tags",
                method="GET",
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def generate_stream(self, prompt: str, model: Optional[str] = None, 
                        system: Optional[str] = None) -> str:
        """流式生成文本"""
        model = model or self.default_model
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        if system:
            data["system"] = system
        
        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=300) as response:
            for line in response:
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            yield chunk['response']
                        if chunk.get('done'):
                            break
                    except json.JSONDecodeError:
                        continue


class AIChatWorker(QThread):
    """AI 聊天工作线程"""
    
    message_chunk = pyqtSignal(str)
    message_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api: OllamaAPI, model: str, prompt: str, system: Optional[str] = None):
        super().__init__()
        self.api = api
        self.model = model
        self.prompt = prompt
        self.system = system
        self._running = True
    
    def run(self):
        """运行生成"""
        try:
            for chunk in self.api.generate_stream(self.prompt, self.model, self.system):
                if not self._running:
                    break
                self.message_chunk.emit(chunk)
            self.message_complete.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """停止生成"""
        self._running = False


class MessageBubble(QFrame):
    """消息气泡组件"""
    
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        
        self._role = role
        self._content = content
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 消息内容
        self._content_label = QLabel()
        self._content_label.setWordWrap(True)
        self._content_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        
        if self._role == "user":
            self._content_label.setStyleSheet("""
                QLabel {
                    background-color: #007acc;
                    color: white;
                    padding: 10px;
                    border-radius: 15px;
                }
            """)
            layout.addStretch()
            layout.addWidget(self._content_label)
        else:
            self._content_label.setStyleSheet("""
                QLabel {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    padding: 10px;
                    border-radius: 15px;
                }
            """)
            layout.addWidget(self._content_label)
            layout.addStretch()
        
        self._content_label.setText(self._format_content(self._content))
    
    def _format_content(self, content: str) -> str:
        """格式化内容（简单处理）"""
        # 转义 HTML
        content = content.replace("&", "&amp;")
        content = content.replace("<", "&lt;")
        content = content.replace(">", "&gt;")
        
        # 处理代码块
        import re
        content = re.sub(
            r'```(\w+)?\n(.*?)```',
            r'<pre style="background:#1e1e1e;padding:10px;border-radius:5px;overflow-x:auto;"><code>\2</code></pre>',
            content,
            flags=re.DOTALL
        )
        
        # 处理行内代码
        content = re.sub(
            r'`([^`]+)`',
            r'<code style="background:#1e1e1e;padding:2px 4px;border-radius:3px;">\1</code>',
            content
        )
        
        # 处理换行
        content = content.replace("\n", "<br>")
        
        return content
    
    def append_content(self, text: str):
        """追加内容"""
        self._content += text
        self._content_label.setText(self._format_content(self._content))


class AIChat(QWidget):
    """AI 聊天组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._api = OllamaAPI()
        self._current_worker: Optional[AIChatWorker] = None
        self._messages: List[Message] = []
        self._bubbles: List[MessageBubble] = []
        
        self._setup_ui()
        self._check_ollama()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 状态栏
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self._status_label = QLabel("检查 Ollama 状态...")
        status_layout.addWidget(self._status_label)
        
        status_layout.addStretch()
        
        # 模型选择
        status_layout.addWidget(QLabel("模型:"))
        self._model_combo = QComboBox()
        self._model_combo.setMinimumWidth(150)
        status_layout.addWidget(self._model_combo)
        
        layout.addLayout(status_layout)
        
        # 消息区域
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        
        self._messages_widget = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._messages_layout.setSpacing(10)
        self._messages_layout.addStretch()
        
        self._scroll_area.setWidget(self._messages_widget)
        layout.addWidget(self._scroll_area)
        
        # 输入区域
        input_widget = QWidget()
        input_widget.setFixedHeight(90)
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 5, 10, 10)
        input_layout.setSpacing(8)
        
        self._input = QTextEdit()
        self._input.setPlaceholderText("输入消息... (Ctrl+Enter 发送)")
        self._input.setStyleSheet("""
            QTextEdit {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        input_layout.addWidget(self._input, 1)
        
        # 按钮容器
        btn_container = QWidget()
        btn_container.setFixedWidth(130)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(5)
        
        self._send_btn = QPushButton("发送")
        self._send_btn.setFixedSize(60, 70)
        self._send_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        self._send_btn.clicked.connect(self._send_message)
        btn_layout.addWidget(self._send_btn)
        
        self._stop_btn = QPushButton("停止")
        self._stop_btn.setFixedSize(60, 70)
        self._stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #c75450;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        self._stop_btn.clicked.connect(self._stop_generation)
        self._stop_btn.setEnabled(False)
        btn_layout.addWidget(self._stop_btn)
        
        input_layout.addWidget(btn_container)
        
        layout.addWidget(input_widget)
        
        # 快捷键
        self._input.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """事件过滤器"""
        if obj == self._input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self._send_message()
                return True
        return super().eventFilter(obj, event)
    
    def _check_ollama(self):
        """检查 Ollama 状态"""
        if self._api.is_available():
            self._status_label.setText("✅ Ollama 已连接")
            self._status_label.setStyleSheet("color: #4ec9b0;")
            self._load_models()
        else:
            self._status_label.setText("❌ Ollama 未启动")
            self._status_label.setStyleSheet("color: #ff6b6b;")
    
    def _load_models(self):
        """加载模型列表"""
        models = self._api.list_models()
        if models:
            self._model_combo.clear()
            self._model_combo.addItems(models)
            # 选择默认模型
            default_index = self._model_combo.findText(self._api.default_model)
            if default_index >= 0:
                self._model_combo.setCurrentIndex(default_index)
    
    def _send_message(self):
        """发送消息"""
        text = self._input.toPlainText().strip()
        if not text:
            return
        
        if not self._api.is_available():
            self._add_message("assistant", "Ollama 未启动，请先启动 Ollama 服务。")
            return
        
        # 添加用户消息
        self._add_message("user", text)
        self._input.clear()
        
        # 创建 AI 回复气泡
        self._current_bubble = self._add_message("assistant", "")
        
        # 启动生成
        model = self._model_combo.currentText()
        system = "You are a helpful AI programming assistant."
        
        self._current_worker = AIChatWorker(self._api, model, text, system)
        self._current_worker.message_chunk.connect(self._on_message_chunk)
        self._current_worker.message_complete.connect(self._on_message_complete)
        self._current_worker.error_occurred.connect(self._on_error)
        self._current_worker.start()
        
        self._send_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
    
    def _add_message(self, role: str, content: str) -> MessageBubble:
        """添加消息"""
        bubble = MessageBubble(role, content)
        self._bubbles.append(bubble)
        
        # 插入到布局中（在 stretch 之前）
        self._messages_layout.insertWidget(
            self._messages_layout.count() - 1, bubble
        )
        
        # 滚动到底部
        QTimer.singleShot(100, self._scroll_to_bottom)
        
        return bubble
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self._scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _on_message_chunk(self, chunk: str):
        """接收消息块"""
        if hasattr(self, '_current_bubble'):
            self._current_bubble.append_content(chunk)
            self._scroll_to_bottom()
    
    def _on_message_complete(self):
        """消息生成完成"""
        self._send_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._current_worker = None
    
    def _on_error(self, error: str):
        """错误处理"""
        if hasattr(self, '_current_bubble'):
            self._current_bubble.append_content(f"\n[错误: {error}]")
        self._on_message_complete()
    
    def _stop_generation(self):
        """停止生成"""
        if self._current_worker:
            self._current_worker.stop()
            self._current_worker.wait()
            self._on_message_complete()


# 为了兼容性保留的类
class ChatManager:
    """兼容旧版 ChatManager"""
    pass
