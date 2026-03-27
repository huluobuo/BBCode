# -*- coding: utf-8 -*-
"""
BBCode PyQt6 AI 聊天插件
基于 PyQt6 的现代化 AI 编程助手界面
集成 Ollama API
"""

import re
import time
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy,
    QApplication, QMenu, QToolButton, QSplitter, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QUrl
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QDesktopServices

from thonny.qt_themes import get_theme_manager

# 导入 Ollama 客户端
try:
    from plugins.ollama_client import OllamaChatManager, check_ollama_status
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class MessageType(Enum):
    """消息类型"""
    USER = "user"
    AI = "ai"
    SYSTEM = "system"
    ERROR = "error"


@dataclass
class ChatMessage:
    """聊天消息数据类"""
    content: str
    message_type: MessageType
    timestamp: float
    metadata: Optional[Dict] = None


class MarkdownParser:
    """简化的 Markdown 解析器"""
    
    @staticmethod
    def parse(text: str) -> str:
        """解析 Markdown 文本为 HTML"""
        # 代码块
        text = re.sub(
            r'```(\w+)?\n(.*?)```',
            r'<pre class="code-block"><code>\2</code></pre>',
            text,
            flags=re.DOTALL
        )
        
        # 行内代码
        text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)
        
        # 粗体
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # 斜体
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # 标题
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # 列表
        text = re.sub(r'^- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>', text, flags=re.DOTALL)
        
        # 链接
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # 换行
        text = text.replace('\n', '<br>')
        
        return text


class MessageBubble(QFrame):
    """消息气泡组件"""
    
    link_clicked = pyqtSignal(str)
    
    def __init__(self, message: ChatMessage, parent=None):
        super().__init__(parent)
        self._message = message
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        theme = get_theme_manager().get_colors()
        
        # 根据消息类型设置样式
        if self._message.message_type == MessageType.USER:
            bg_color = theme.accent
            text_color = "#ffffff"
            alignment = Qt.AlignmentFlag.AlignRight
        elif self._message.message_type == MessageType.AI:
            bg_color = theme.bg_tertiary
            text_color = theme.text_primary
            alignment = Qt.AlignmentFlag.AlignLeft
        elif self._message.message_type == MessageType.ERROR:
            bg_color = theme.error
            text_color = "#ffffff"
            alignment = Qt.AlignmentFlag.AlignLeft
        else:
            bg_color = theme.bg_secondary
            text_color = theme.text_secondary
            alignment = Qt.AlignmentFlag.AlignCenter
        
        # 设置气泡样式
        self.setStyleSheet(f"""
            MessageBubble {{
                background-color: {bg_color};
                border-radius: 12px;
                padding: 12px;
                margin: 4px 8px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # 发送者标签
        sender_label = QLabel()
        if self._message.message_type == MessageType.USER:
            sender_label.setText("你")
        elif self._message.message_type == MessageType.AI:
            sender_label.setText("AI 助手")
        elif self._message.message_type == MessageType.ERROR:
            sender_label.setText("错误")
        else:
            sender_label.setText("系统")
        
        sender_label.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 11px;")
        layout.addWidget(sender_label)
        
        # 消息内容
        content_label = QTextEdit()
        content_label.setReadOnly(True)
        content_label.setFrameStyle(QFrame.Shape.NoFrame)
        content_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 去掉内框和背景
        content_label.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
        """)
        
        # 解析 Markdown
        html_content = MarkdownParser.parse(self._message.content)
        
        content_label.setHtml(f"""
            <html>
            <head>
                <style>
                    body {{
                        color: {text_color};
                        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                        font-size: 13px;
                        line-height: 1.5;
                    }}
                    pre.code-block {{
                        background-color: {theme.bg_primary};
                        border: 1px solid {theme.border};
                        border-radius: 6px;
                        padding: 12px;
                        margin: 8px 0;
                        overflow-x: auto;
                    }}
                    code {{
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 12px;
                    }}
                    code.inline-code {{
                        background-color: {theme.bg_primary};
                        padding: 2px 6px;
                        border-radius: 3px;
                        color: {theme.accent};
                    }}
                    a {{
                        color: {theme.accent};
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    h1, h2, h3 {{
                        margin: 8px 0;
                        color: {text_color};
                    }}
                    ul {{
                        margin: 8px 0;
                        padding-left: 20px;
                    }}
                    li {{
                        margin: 4px 0;
                    }}
                </style>
            </head>
            <body>{html_content}</body>
            </html>
        """)
        
        # 调整高度适应内容
        doc = content_label.document()
        doc.setTextWidth(content_label.viewport().width())
        height = doc.size().height() + 20
        content_label.setFixedHeight(int(height))
        
        content_label.setStyleSheet(f"background-color: transparent; color: {text_color};")
        layout.addWidget(content_label)
        
        # 时间戳
        time_str = time.strftime("%H:%M", time.localtime(self._message.timestamp))
        time_label = QLabel(time_str)
        time_label.setStyleSheet(f"color: {text_color}; font-size: 10px; opacity: 0.7;")
        layout.addWidget(time_label)
        
        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        # 处理链接点击
        pass


class AIChatWidget(QWidget):
    """AI 聊天组件 - 集成 Ollama"""

    message_sent = pyqtSignal(str)
    code_insert_requested = pyqtSignal(str)
    quick_action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._messages: List[ChatMessage] = []
        self._current_ai_message: Optional[MessageBubble] = None
        self._is_generating = False

        # 初始化 Ollama 管理器
        self._ollama: Optional[OllamaChatManager] = None
        if OLLAMA_AVAILABLE:
            self._ollama = OllamaChatManager()
            self._ollama.message_chunk.connect(self._on_ollama_chunk)
            self._ollama.error_occurred.connect(self._on_ollama_error)

        self._setup_ui()
        self._check_ollama_status()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # 消息显示区域
        self._messages_widget = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._messages_layout.setSpacing(8)
        self._messages_layout.addStretch()
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._messages_widget)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        splitter.addWidget(scroll)
        
        # 输入区域
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(12, 8, 12, 12)
        input_layout.setSpacing(8)

        # 多行文本输入框
        self._input_field = QTextEdit()
        self._input_field.setPlaceholderText("输入消息或代码问题...\n支持多行文本，按 Ctrl+Enter 发送")
        self._input_field.setFixedHeight(80)
        self._input_field.setAcceptRichText(False)
        # 设置等宽字体，方便输入代码
        from PyQt6.QtGui import QFont
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._input_field.setFont(font)
        input_layout.addWidget(self._input_field)

        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # 发送提示标签
        hint_label = QLabel("Ctrl+Enter 发送")
        hint_label.setStyleSheet("color: #666; font-size: 11px;")
        btn_layout.addWidget(hint_label)

        btn_layout.addStretch()

        # 模型选择下拉框
        self._model_combo = QComboBox()
        self._model_combo.setFixedHeight(32)
        self._model_combo.setFixedWidth(150)
        self._model_combo.setEnabled(False)
        btn_layout.addWidget(self._model_combo)

        # 设置按钮
        self._settings_btn = QPushButton("⚙")
        self._settings_btn.setFixedSize(32, 32)
        self._settings_btn.setToolTip("AI设置")
        self._settings_btn.clicked.connect(self._show_settings)
        btn_layout.addWidget(self._settings_btn)

        # 发送按钮
        self._send_btn = QPushButton("发送")
        self._send_btn.setFixedSize(80, 32)
        self._send_btn.setObjectName("primary")
        self._send_btn.clicked.connect(self._on_send_button_clicked)
        btn_layout.addWidget(self._send_btn)

        input_layout.addLayout(btn_layout)

        splitter.addWidget(input_widget)

        # 设置分割器比例
        splitter.setSizes([400, 60, 60])

        # 添加快捷菜单
        self._setup_context_menu()
    
    def _setup_context_menu(self):
        """设置右键菜单"""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        
        clear_action = menu.addAction("清空对话")
        clear_action.triggered.connect(self.clear_messages)
        
        copy_action = menu.addAction("复制全部")
        copy_action.triggered.connect(self._copy_all)
        
        menu.exec(self.mapToGlobal(pos))
    
    def add_message(self, content: str, message_type: MessageType = MessageType.AI):
        """添加消息"""
        message = ChatMessage(
            content=content,
            message_type=message_type,
            timestamp=time.time()
        )
        self._messages.append(message)
        
        # 创建消息气泡
        bubble = MessageBubble(message)
        
        # 插入到布局中（在 stretch 之前）
        self._messages_layout.insertWidget(
            self._messages_layout.count() - 1,
            bubble
        )
        
        # 滚动到底部
        QTimer.singleShot(100, self._scroll_to_bottom)
    
    def add_ai_response(self, content: str):
        """添加 AI 响应"""
        self.add_message(content, MessageType.AI)
    
    def add_system_message(self, content: str):
        """添加系统消息"""
        self.add_message(content, MessageType.SYSTEM)
    
    def add_error_message(self, content: str):
        """添加错误消息"""
        self.add_message(content, MessageType.ERROR)
    
    def clear_messages(self):
        """清空所有消息"""
        self._messages.clear()
        
        # 清除所有消息气泡
        while self._messages_layout.count() > 1:  # 保留 stretch
            item = self._messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _copy_all(self):
        """复制所有消息"""
        text = ""
        for msg in self._messages:
            sender = "用户" if msg.message_type == MessageType.USER else "AI"
            text += f"[{sender}]: {msg.content}\n\n"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        # 获取滚动区域并滚动到底部
        parent = self._messages_widget.parent()
        while parent and not isinstance(parent, QScrollArea):
            parent = parent.parent()
        
        if isinstance(parent, QScrollArea):
            scrollbar = parent.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def get_input_text(self) -> str:
        """获取输入框文本"""
        return self._input_field.toPlainText()

    def set_input_text(self, text: str):
        """设置输入框文本"""
        self._input_field.setPlainText(text)

    def focus_input(self):
        """聚焦输入框"""
        self._input_field.setFocus()

    def keyPressEvent(self, event):
        """键盘事件处理 - 支持 Ctrl+Enter 发送"""
        # 检查是否是 Ctrl+Enter
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._on_send_button_clicked()
        else:
            super().keyPressEvent(event)
    
    def set_loading(self, loading: bool):
        """设置加载状态"""
        self._is_generating = loading
        self._send_btn.setEnabled(True)
        if loading:
            self._send_btn.setText("停止")
        else:
            self._send_btn.setText("发送")

    def _check_ollama_status(self):
        """检查 Ollama 状态"""
        if not OLLAMA_AVAILABLE:
            self.add_system_message("Ollama 模块未安装，AI 功能不可用")
            return

        if self._ollama and self._ollama.is_available():
            models = self._ollama.get_available_models()
            if models:
                self._model_combo.clear()
                self._model_combo.addItems(models)
                self._model_combo.setEnabled(True)
                self.add_system_message(f"Ollama 已连接，可用模型: {', '.join(models[:3])}...")
            else:
                self.add_system_message("Ollama 已连接，但未找到模型。请运行: ollama pull qwen2.5-coder:7b")
        else:
            self.add_system_message("Ollama 未启动。请运行: ollama serve")

    def _send_to_ollama(self, message: str, code_context: str = ""):
        """发送消息到 Ollama"""
        if not self._ollama:
            self.add_error_message("Ollama 未初始化")
            return

        # 设置当前模型
        if self._model_combo.currentText():
            self._ollama.set_model(self._model_combo.currentText())

        # 创建空的 AI 消息气泡（用于流式更新）
        self._current_ai_message = None
        self._current_ai_content = ""

        # 设置加载状态
        self.set_loading(True)

        # 发送请求
        self._ollama.send_message(message, code_context)

    def _on_ollama_chunk(self, chunk: str):
        """接收 Ollama 流式响应"""
        if self._current_ai_message is None:
            # 创建新的 AI 消息气泡
            message = ChatMessage(
                content=chunk,
                message_type=MessageType.AI,
                timestamp=time.time()
            )
            self._messages.append(message)
            self._current_ai_message = MessageBubble(message)
            self._messages_layout.insertWidget(
                self._messages_layout.count() - 1,
                self._current_ai_message
            )
            self._current_ai_content = chunk
        else:
            # 更新现有消息
            self._current_ai_content += chunk
            # 重新创建气泡以更新内容
            self._current_ai_message.deleteLater()
            message = ChatMessage(
                content=self._current_ai_content,
                message_type=MessageType.AI,
                timestamp=time.time()
            )
            self._current_ai_message = MessageBubble(message)
            self._messages_layout.insertWidget(
                self._messages_layout.count() - 1,
                self._current_ai_message
            )

        # 滚动到底部
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _on_ollama_error(self, error: str):
        """处理 Ollama 错误"""
        self.set_loading(False)
        self.add_error_message(f"Ollama 错误: {error}")

    def _stop_generation(self):
        """停止生成"""
        if self._ollama:
            self._ollama.stop_generation()
        self.set_loading(False)

    def _send_message(self):
        """发送消息"""
        text = self._input_field.toPlainText().strip()
        if text:
            # 添加用户消息
            self.add_message(text, MessageType.USER)

            # 清空输入框
            self._input_field.clear()

            # 发送到 Ollama
            self._send_to_ollama(text)

            # 发送信号
            self.message_sent.emit(text)

    def _on_send_button_clicked(self):
        """发送按钮点击处理"""
        if self._is_generating:
            self._stop_generation()
        else:
            self._send_message()

    def _show_settings(self):
        """显示设置对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QTabWidget

        dialog = QDialog(self)
        dialog.setWindowTitle("AI 设置")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # 创建标签页
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # === 基本设置 ===
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)

        # Ollama URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Ollama 地址:"))
        self._url_input = QLineEdit()
        if self._ollama:
            self._url_input.setText(self._ollama.api.get_host())
        self._url_input.setPlaceholderText("http://localhost:11434")
        url_layout.addWidget(self._url_input)
        basic_layout.addLayout(url_layout)

        # 测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self._test_ollama_connection)
        basic_layout.addWidget(test_btn)

        # 连接状态
        self._connection_status = QLabel("未测试")
        basic_layout.addWidget(self._connection_status)

        basic_layout.addStretch()
        tabs.addTab(basic_tab, "基本设置")

        # === 系统提示词 ===
        prompt_tab = QWidget()
        prompt_layout = QVBoxLayout(prompt_tab)

        prompt_layout.addWidget(QLabel("系统提示词:"))
        self._prompt_edit = QTextEdit()
        if self._ollama:
            self._prompt_edit.setText(self._ollama.get_system_prompt())
        self._prompt_edit.setPlaceholderText("输入系统提示词...")
        prompt_layout.addWidget(self._prompt_edit)

        # 恢复默认按钮
        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self._reset_system_prompt)
        prompt_layout.addWidget(reset_btn)

        tabs.addTab(prompt_tab, "系统提示词")

        # === 辅助信息 ===
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)

        info_text = """
<h3>AI 编程助手使用说明</h3>

<p><b>快捷操作:</b></p>
<ul>
<li><b>解释代码</b> - 分析代码功能和逻辑</li>
<li><b>优化代码</b> - 提高性能和可读性</li>
<li><b>生成注释</b> - 自动添加代码注释</li>
<li><b>修复错误</b> - 查找并修复代码问题</li>
</ul>

<p><b>使用技巧:</b></p>
<ul>
<li>在编辑器中选中代码后使用快捷操作</li>
<li>可以直接提问任何编程相关问题</li>
<li>支持 Markdown 格式的回复</li>
<li>代码块会自动语法高亮</li>
</ul>

<p><b>模型推荐:</b></p>
<ul>
<li>qwen2.5-coder:7b - 代码能力强，中文好</li>
<li>codellama:7b - Meta 出品，代码专用</li>
<li>deepseek-coder:6.7b - 国产，代码能力强</li>
</ul>

<p><b>注意事项:</b></p>
<ul>
<li>确保 Ollama 服务已启动</li>
<li>首次使用需要下载模型</li>
<li>所有 AI 处理在本地完成</li>
</ul>
"""
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(info_label)
        info_layout.addStretch()

        tabs.addTab(info_tab, "使用说明")

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(lambda: self._save_settings(dialog))
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    def _test_ollama_connection(self):
        """测试 Ollama 连接"""
        url = self._url_input.text().strip()
        if not url:
            url = "http://localhost:11434"

        self._connection_status.setText("正在测试...")

        # 在后台测试
        from PyQt6.QtCore import QThread, pyqtSignal
        from plugins.ollama_client import OllamaAPI

        class TestThread(QThread):
            result = pyqtSignal(bool, str)

            def __init__(self, url):
                super().__init__()
                self.url = url

            def run(self):
                try:
                    api = OllamaAPI(self.url)
                    if api.is_available():
                        models = api.list_models()
                        model_names = [m.get('name', '') for m in models[:3]]
                        self.result.emit(True, f"连接成功！可用模型: {', '.join(model_names)}")
                    else:
                        self.result.emit(False, "连接失败，请检查 Ollama 服务是否运行")
                except Exception as e:
                    self.result.emit(False, f"连接错误: {str(e)}")

        self._test_thread = TestThread(url)
        self._test_thread.result.connect(lambda ok, msg: self._connection_status.setText(msg))
        self._test_thread.start()

    def _reset_system_prompt(self):
        """恢复默认系统提示词"""
        default_prompt = """你是一个专业的AI编程助手，集成在BBCode Python IDE中。

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
        self._prompt_edit.setText(default_prompt)

    def _save_settings(self, dialog):
        """保存设置"""
        # 保存 URL
        url = self._url_input.text().strip()
        if url and self._ollama:
            self._ollama.api.set_host(url)

        # 保存系统提示词
        prompt = self._prompt_edit.toPlainText().strip()
        if prompt and self._ollama:
            self._ollama.set_system_prompt(prompt)

        dialog.accept()


class AIChatDockWidget(QWidget):
    """AI 聊天停靠窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建 AI 聊天组件
        self._chat_widget = AIChatWidget()
        layout.addWidget(self._chat_widget)
    
    def get_chat_widget(self) -> AIChatWidget:
        """获取聊天组件"""
        return self._chat_widget


def create_chat_dock(parent=None) -> QFrame:
    """创建聊天停靠窗口"""
    frame = QFrame(parent)
    frame.setFrameStyle(QFrame.Shape.StyledPanel)
    
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    
    chat_widget = AIChatWidget()
    layout.addWidget(chat_widget)
    
    return frame


# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from thonny.qt_themes import apply_theme
    
    app = QApplication(sys.argv)
    apply_theme(app, "dark")
    
    window = AIChatWidget()
    window.resize(400, 600)
    
    # 添加测试消息
    window.add_message("你好！我是你的 AI 编程助手。", MessageType.AI)
    window.add_message("请帮我解释这段代码", MessageType.USER)
    window.add_ai_response("""
当然可以！这段代码的功能是：

```python
def hello():
    print("Hello, World!")
```

这是一个简单的函数定义，它会打印 "Hello, World!"。

**主要特点：**
- 使用 `def` 关键字定义函数
- 函数名为 `hello`
- 使用 `print()` 函数输出文本

如需更多帮助，请随时告诉我！
    """)
    
    window.show()
    sys.exit(app.exec())
