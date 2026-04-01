# -*- coding: utf-8 -*-
"""
BBCode AI 聊天组件
支持 Ollama 本地模型，支持上下文记忆和对话管理
使用 /api/chat 接口进行原生对话
集成云知识库功能
"""

import json
import urllib.request
import urllib.error
import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass, asdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QComboBox, QScrollArea, QFrame,
    QSizePolicy, QApplication, QFileDialog, QMessageBox, QMenu,
    QTextBrowser
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QUrl
from PyQt6.QtGui import QFont, QColor, QAction, QClipboard

# 导入知识库模块
try:
    from plugins.knowledge_base import get_knowledge_base
    from plugins.cloud_kb_client import get_cloud_kb_client
    KNOWLEDGE_BASE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_BASE_AVAILABLE = False


@dataclass
class Message:
    """聊天消息"""
    role: str  # "user", "assistant", or "system"
    content: str
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }
    
    def to_api_format(self) -> dict:
        """转换为 API 格式（仅 role 和 content）"""
        return {
            "role": self.role,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        return cls(
            role=data.get("role", ""),
            content=data.get("content", ""),
            timestamp=data.get("timestamp")
        )


class OllamaAPI:
    """Ollama API 客户端 - 使用 /api/chat 接口"""
    
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
    
    def chat_stream(self, messages: List[Message], model: Optional[str] = None,
                    system: Optional[str] = None) -> str:
        """
        使用 /api/chat 接口进行流式对话
        messages: 对话历史消息列表
        """
        model = model or self.default_model
        
        # 构建 messages 数组（限制上下文长度）
        max_context = 20  # 最多保留20条消息
        recent_messages = messages[-max_context:] if len(messages) > max_context else messages
        
        # 转换为 API 格式
        api_messages = [msg.to_api_format() for msg in recent_messages]
        
        # 如果有 system 提示且第一条不是 system，则插入
        if system and (not api_messages or api_messages[0].get("role") != "system"):
            api_messages.insert(0, {"role": "system", "content": system})
        
        data = {
            "model": model,
            "messages": api_messages,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "num_ctx": 4096  # 上下文窗口大小
            }
        }
        
        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=300) as response:
            for line in response:
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'message' in chunk and 'content' in chunk['message']:
                            yield chunk['message']['content']
                        if chunk.get('done'):
                            break
                    except json.JSONDecodeError:
                        continue


class AIChatWorker(QThread):
    """AI 聊天工作线程"""
    
    message_chunk = pyqtSignal(str)
    message_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api: OllamaAPI, model: str, messages: List[Message],
                 system: Optional[str] = None):
        super().__init__()
        self.api = api
        self.model = model
        self.messages = messages
        self.system = system
        self._running = True
    
    def run(self):
        """运行生成"""
        try:
            for chunk in self.api.chat_stream(self.messages, self.model, self.system):
                if not self._running:
                    break
                self.message_chunk.emit(chunk)
            self.message_complete.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """停止生成"""
        self._running = False


class CodeBlockWidget(QFrame):
    """代码块组件 - 带复制按钮"""
    
    def __init__(self, language: str, code: str, parent=None):
        super().__init__(parent)
        self._code = code
        self._language = language or "text"
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            CodeBlockWidget {
                background-color: #1e1e1e;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部栏 - 语言标签和复制按钮
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #333;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        lang_label = QLabel(self._language.upper())
        lang_label.setStyleSheet("color: #858585; font-size: 11px; font-family: monospace;")
        header_layout.addWidget(lang_label)
        
        header_layout.addStretch()
        
        copy_btn = QPushButton("📋 复制")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #4ec9b0;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
        """)
        copy_btn.clicked.connect(self._copy_code)
        header_layout.addWidget(copy_btn)
        
        layout.addWidget(header)
        
        # 代码内容 - 使用 QTextBrowser 显示
        self._code_browser = QTextBrowser()
        self._code_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        self._code_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._code_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 转义代码显示
        escaped_code = self._code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self._code_browser.setHtml(f"<pre style='margin:0; white-space:pre-wrap; word-wrap:break-word;'>{escaped_code}</pre>")
        
        # 设置代码区域的最大高度
        self._code_browser.setMaximumHeight(400)
        
        layout.addWidget(self._code_browser)
    
    def _copy_code(self):
        """复制代码到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self._code)


class MessageBubble(QFrame):
    """消息气泡组件 - 支持代码复制"""
    
    copy_code_requested = pyqtSignal(str)
    
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        
        self._role = role
        self._content = content
        self._code_blocks: List[CodeBlockWidget] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(0)
        
        # 创建垂直布局容器
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(12, 10, 12, 10)
        self._content_layout.setSpacing(8)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 设置样式
        if self._role == "user":
            self._content_widget.setStyleSheet("""
                QWidget {
                    background-color: #007acc;
                    color: white;
                    border-radius: 16px;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                    line-height: 1.5;
                }
            """)
            layout.addStretch()
            layout.addWidget(self._content_widget, stretch=1)
        else:
            self._content_widget.setStyleSheet("""
                QWidget {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    border-radius: 16px;
                }
                QLabel {
                    color: #d4d4d4;
                    font-size: 14px;
                    line-height: 1.6;
                }
            """)
            layout.addWidget(self._content_widget, stretch=1)
            layout.addStretch()
        
        self._update_content()
    
    def _update_content(self):
        """更新显示内容"""
        # 清除现有内容
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._code_blocks.clear()
        
        # 解析内容，分离文本和代码块
        parts = self._split_content(self._content)
        
        for part_type, part_content in parts:
            if part_type == "text":
                # 创建文本标签
                label = QLabel()
                label.setWordWrap(True)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                label.setTextFormat(Qt.TextFormat.RichText)
                
                # 格式化文本（处理行内代码和换行）
                formatted_text = self._format_text(part_content)
                label.setText(formatted_text)
                self._content_layout.addWidget(label)
            
            elif part_type == "code":
                # 创建代码块组件
                language, code = part_content
                code_widget = CodeBlockWidget(language, code)
                self._code_blocks.append(code_widget)
                self._content_layout.addWidget(code_widget)
    
    def _split_content(self, content: str) -> List[tuple]:
        """将内容分割为文本和代码块"""
        parts = []
        remaining = content
        
        # 正则匹配代码块
        pattern = r'```(\w+)?\n(.*?)```'
        
        while remaining:
            match = re.search(pattern, remaining, re.DOTALL)
            if match:
                # 代码块前的文本
                if match.start() > 0:
                    text_part = remaining[:match.start()].strip()
                    if text_part:
                        parts.append(("text", text_part))
                
                # 代码块
                lang = match.group(1) or ""
                code = match.group(2)
                parts.append(("code", (lang, code)))
                
                remaining = remaining[match.end():]
            else:
                # 剩余都是文本
                if remaining.strip():
                    parts.append(("text", remaining.strip()))
                break
        
        return parts
    
    def _format_text(self, text: str) -> str:
        """格式化文本内容 - 支持 Markdown"""
        # 转义 HTML
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # 处理粗体 **text**
        text = re.sub(
            r'\*\*([^\*]+)\*\*',
            r'<b>\1</b>',
            text
        )
        
        # 处理斜体 *text*
        text = re.sub(
            r'\*([^\*]+)\*',
            r'<i>\1</i>',
            text
        )
        
        # 处理行内代码 `code`
        text = re.sub(
            r'`([^`]+)`',
            r'<code style="background:#2d2d2d;padding:2px 6px;border-radius:4px;color:#dcdcaa;font-family:monospace;font-size:13px;">\1</code>',
            text
        )
        
        # 处理标题 ### Title
        for i in range(6, 0, -1):
            text = re.sub(
                rf'^{"#" * i} (.+)$',
                rf'<h{i}>\1</h{i}>',
                text,
                flags=re.MULTILINE
            )
        
        # 处理无序列表 - item 或 * item
        def format_list(match):
            items = match.group(0).strip().split('\n')
            formatted_items = []
            for item in items:
                item_text = re.sub(r'^[\-\*] ', '', item.strip())
                if item_text:
                    formatted_items.append(f'<li>{item_text}</li>')
            return '<ul>' + ''.join(formatted_items) + '</ul>'
        
        text = re.sub(
            r'((?:^[\-\*] .+\n?)+)',
            format_list,
            text,
            flags=re.MULTILINE
        )
        
        # 处理有序列表 1. item
        def format_ordered_list(match):
            items = match.group(0).strip().split('\n')
            formatted_items = []
            for item in items:
                item_text = re.sub(r'^\d+\. ', '', item.strip())
                if item_text:
                    formatted_items.append(f'<li>{item_text}</li>')
            return '<ol>' + ''.join(formatted_items) + '</ol>'
        
        text = re.sub(
            r'((?:^\d+\. .+\n?)+)',
            format_ordered_list,
            text,
            flags=re.MULTILINE
        )
        
        # 处理换行
        text = text.replace('\n', '<br>')
        
        return text
    
    def append_content(self, text: str):
        """追加内容"""
        self._content += text
        self._update_content()
    
    def get_content(self) -> str:
        """获取内容"""
        return self._content


class AIChat(QWidget):
    """AI 聊天组件 - 支持上下文记忆和对话管理，集成云知识库"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 从设置加载 Ollama 配置
        self._load_ollama_config()
        
        self._current_worker: Optional[AIChatWorker] = None
        self._messages: List[Message] = []
        self._bubbles: List[MessageBubble] = []
        
        # 初始化知识库
        self._kb = None
        self._cloud_kb = None
        self._kb_enabled = False
        self._init_knowledge_base()
        
        self._setup_ui()
        self._check_ollama()
        
        # 尝试加载上次的对话
        self._load_conversation_history()
    
    def _load_ollama_config(self):
        """从设置加载 Ollama 配置"""
        try:
            from PyQt6.QtCore import QSettings
            settings = QSettings("BBCode", "IDE")
            
            # 加载主机和端口
            host = settings.value("ollamaHost", "127.0.0.1")
            port = int(settings.value("ollamaPort", 11434))
            
            # 构建完整的 URL
            if host.startswith("http://") or host.startswith("https://"):
                ollama_url = f"{host}:{port}"
            else:
                ollama_url = f"http://{host}:{port}"
            
            # 加载默认模型
            model = settings.value("defaultModel", "gemma3:1b")
            
            # 初始化 API
            self._api = OllamaAPI(host=ollama_url)
            self._api.default_model = model
            
            print(f"[AIChat] 已加载 Ollama 配置: {ollama_url}, 模型: {model}")
        except Exception as e:
            print(f"[AIChat] 加载 Ollama 配置失败: {e}")
            # 使用默认配置
            self._api = OllamaAPI()
            self._api.default_model = "gemma3:1b"
    
    def _init_knowledge_base(self):
        """初始化知识库"""
        if KNOWLEDGE_BASE_AVAILABLE:
            try:
                self._kb = get_knowledge_base()
                self._cloud_kb = get_cloud_kb_client()
                self._kb_enabled = True
            except Exception as e:
                print(f"知识库初始化失败: {e}")
                self._kb_enabled = False
    
    def _setup_ui(self):
        # 设置整体深色背景
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QLabel {
                color: #d4d4d4;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 3px 8px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #d4d4d4;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                selection-background-color: #007acc;
            }
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #424242;
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4f4f4f;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 状态栏
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self._status_label = QLabel("检查 Ollama 状态...")
        status_layout.addWidget(self._status_label)
        
        status_layout.addStretch()
        
        # 对话管理按钮
        self._manage_btn = QPushButton("对话管理 ▼")
        self._manage_btn.setFixedWidth(100)
        self._manage_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
        """)
        self._manage_btn.clicked.connect(self._show_manage_menu)
        status_layout.addWidget(self._manage_btn)
        
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
    
    def _show_manage_menu(self):
        """显示对话管理菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #007acc;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 4px 0;
            }
        """)
        
        clear_action = QAction("🗑️ 清空对话", self)
        clear_action.triggered.connect(self._clear_conversation)
        menu.addAction(clear_action)
        
        save_action = QAction("💾 保存对话", self)
        save_action.triggered.connect(self._save_conversation)
        menu.addAction(save_action)
        
        load_action = QAction("📂 加载对话", self)
        load_action.triggered.connect(self._load_conversation)
        menu.addAction(load_action)
        
        menu.addSeparator()
        
        # 知识库相关选项
        kb_menu = menu.addMenu("📚 知识库")
        kb_menu.setStyleSheet(menu.styleSheet())
        
        if self._kb_enabled:
            # 同步知识库
            sync_action = QAction("🔄 同步云知识库", kb_menu)
            sync_action.triggered.connect(self._sync_knowledge_base)
            kb_menu.addAction(sync_action)
            
            # 知识库设置
            kb_settings_action = QAction("⚙️ 云知识库设置...", kb_menu)
            kb_settings_action.triggered.connect(self._open_kb_settings)
            kb_menu.addAction(kb_settings_action)
            
            kb_menu.addSeparator()
            
            # 显示知识库状态
            if self._kb and self._kb.is_cloud_sync_enabled():
                status_action = QAction("✅ 云端同步已启用", kb_menu)
            else:
                status_action = QAction("⚠️ 云端同步未启用", kb_menu)
            status_action.setEnabled(False)
            kb_menu.addAction(status_action)
        else:
            kb_unavailable_action = QAction("知识库不可用", kb_menu)
            kb_unavailable_action.setEnabled(False)
            kb_menu.addAction(kb_unavailable_action)
        
        menu.exec(self._manage_btn.mapToGlobal(self._manage_btn.rect().bottomLeft()))
    
    def _sync_knowledge_base(self):
        """同步知识库"""
        if not self._kb_enabled or not self._kb:
            QMessageBox.warning(self, "警告", "知识库未启用")
            return
        
        if not self._kb.is_cloud_sync_enabled():
            reply = QMessageBox.question(
                self,
                "云知识库未启用",
                "云端同步未启用或未配置。是否打开设置？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._open_kb_settings()
            return
        
        # 显示进度对话框
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("正在同步云知识库...", "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("同步中")
        progress.show()
        
        # 在后台线程中同步
        def do_sync():
            success, message = self._kb.sync_from_cloud()
            return success, message
        
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(do_sync)
        
        def check_result():
            if future.done():
                progress.close()
                success, message = future.result()
                if success:
                    QMessageBox.information(self, "同步成功", message)
                else:
                    QMessageBox.warning(self, "同步失败", message)
                executor.shutdown()
            else:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(100, check_result)
        
        check_result()
    
    def _open_kb_settings(self):
        """打开知识库设置"""
        try:
            from plugins.cloud_kb_settings import show_cloud_kb_settings
            show_cloud_kb_settings(self)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开设置: {str(e)}")
    
    def _clear_conversation(self):
        """清空对话"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空当前对话吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清除消息列表
            self._messages.clear()
            
            # 清除气泡
            for bubble in self._bubbles:
                bubble.deleteLater()
            self._bubbles.clear()
            
            # 清除历史文件
            self._clear_history_file()
    
    def _save_conversation(self):
        """保存对话到文件"""
        if not self._messages:
            QMessageBox.information(self, "提示", "当前没有对话内容可保存")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存对话",
            os.path.expanduser(f"~/BBCode_对话_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
            "JSON 文件 (*.json)"
        )
        
        if file_path:
            try:
                data = {
                    "version": "1.0",
                    "saved_at": datetime.now().isoformat(),
                    "messages": [msg.to_dict() for msg in self._messages]
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", f"对话已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")
    
    def _load_conversation(self):
        """从文件加载对话"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "加载对话",
            os.path.expanduser("~"),
            "JSON 文件 (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 清除现有对话
                self._messages.clear()
                for bubble in self._bubbles:
                    bubble.deleteLater()
                self._bubbles.clear()
                
                # 加载消息
                for msg_data in data.get("messages", []):
                    msg = Message.from_dict(msg_data)
                    self._messages.append(msg)
                    self._add_message_bubble(msg.role, msg.content)
                
                QMessageBox.information(self, "成功", f"已加载 {len(self._messages)} 条消息")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载失败:\n{str(e)}")
    
    def _get_history_file_path(self) -> str:
        """获取历史记录文件路径"""
        config_dir = os.path.expanduser("~/.bbcode")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "ai_chat_history.json")
    
    def _save_conversation_history(self):
        """自动保存对话历史"""
        try:
            file_path = self._get_history_file_path()
            data = {
                "version": "1.0",
                "saved_at": datetime.now().isoformat(),
                "messages": [msg.to_dict() for msg in self._messages]
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存对话历史失败: {e}")
    
    def _load_conversation_history(self):
        """加载上次的对话历史"""
        try:
            file_path = self._get_history_file_path()
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for msg_data in data.get("messages", []):
                    msg = Message.from_dict(msg_data)
                    self._messages.append(msg)
                    self._add_message_bubble(msg.role, msg.content)
        except Exception as e:
            print(f"加载对话历史失败: {e}")
    
    def _clear_history_file(self):
        """清除历史文件"""
        try:
            file_path = self._get_history_file_path()
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"清除历史文件失败: {e}")
    
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
            self._add_message_bubble("assistant", "Ollama 未启动，请先启动 Ollama 服务。")
            return
        
        # 添加用户消息到历史
        user_msg = Message(role="user", content=text)
        self._messages.append(user_msg)
        
        # 添加用户消息气泡
        self._add_message_bubble("user", text)
        self._input.clear()
        
        # 创建 AI 回复气泡
        self._current_bubble = self._add_message_bubble("assistant", "")
        
        # 准备消息列表（包含当前用户消息）
        messages_for_api = self._messages.copy()
        
        # 构建系统提示词，包含知识库上下文
        system = self._build_system_prompt(text)
        
        # 启动生成，传入完整对话历史
        model = self._model_combo.currentText()
        
        self._current_worker = AIChatWorker(
            self._api, model, messages_for_api, system
        )
        self._current_worker.message_chunk.connect(self._on_message_chunk)
        self._current_worker.message_complete.connect(self._on_message_complete)
        self._current_worker.error_occurred.connect(self._on_error)
        self._current_worker.start()
        
        self._send_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
    
    def _build_system_prompt(self, query: str) -> str:
        """构建系统提示词，包含知识库上下文
        
        Args:
            query: 用户查询内容
            
        Returns:
            包含知识库上下文的系统提示词
        """
        base_prompt = "你是一个有用的AI编程助手。请始终使用中文回复用户的问题。"
        
        # 如果知识库可用，添加相关知识
        if self._kb_enabled and self._kb:
            try:
                kb_context = self._kb.get_context_for_query(query, max_length=1500)
                if kb_context:
                    base_prompt += f"\n\n在回答问题时，请参考以下知识库内容：\n{kb_context}"
            except Exception as e:
                print(f"获取知识库上下文失败: {e}")
        
        return base_prompt
    
    def _add_message_bubble(self, role: str, content: str) -> MessageBubble:
        """添加消息气泡（仅UI）"""
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
        # 保存AI回复到历史
        if hasattr(self, '_current_bubble'):
            content = self._current_bubble.get_content()
            if content:
                ai_msg = Message(role="assistant", content=content)
                self._messages.append(ai_msg)
                # 自动保存对话历史
                self._save_conversation_history()
        
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
