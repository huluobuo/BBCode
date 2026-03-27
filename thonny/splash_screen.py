# -*- coding: utf-8 -*-
"""
BBCode 启动动画/闪屏
在程序启动时显示加载进度
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QApplication, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush, QPen


class SplashScreen(QWidget):
    """启动动画窗口"""
    
    loading_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        self.setFixedSize(500, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 居中显示
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        self._setup_ui()
        self._loading_steps = []
        self._current_step = 0
        
    def _setup_ui(self):
        """设置UI"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 标题
        self._title = QLabel("BBCode")
        self._title.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self._title.setStyleSheet("color: #ffffff;")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title)
        
        # 副标题
        self._subtitle = QLabel("PyQt6 Edition")
        self._subtitle.setFont(QFont("Segoe UI", 14))
        self._subtitle.setStyleSheet("color: #a0a0a0;")
        self._subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._subtitle)
        
        layout.addStretch()
        
        # 状态文本
        self._status_label = QLabel("正在初始化...")
        self._status_label.setFont(QFont("Segoe UI", 11))
        self._status_label.setStyleSheet("color: #cccccc;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._status_label)
        
        # 进度条
        self._progress = QProgressBar()
        self._progress.setFixedHeight(4)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet("""
            QProgressBar {
                background-color: #3e3e42;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self._progress)
        
        # 版本信息
        self._version_label = QLabel("v2.0.0")
        self._version_label.setFont(QFont("Segoe UI", 9))
        self._version_label.setStyleSheet("color: #666666;")
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._version_label)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#252526"))
        gradient.setColorAt(1, QColor("#1e1e1e"))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
        
        # 边框
        painter.setPen(QPen(QColor("#3e3e42"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
    
    def set_loading_steps(self, steps: list):
        """设置加载步骤"""
        self._loading_steps = steps
        self._progress.setMaximum(len(steps))
    
    def update_status(self, message: str, progress: int = None):
        """更新状态"""
        self._status_label.setText(message)
        if progress is not None:
            self._progress.setValue(progress)
        else:
            self._current_step += 1
            self._progress.setValue(self._current_step)
        
        QApplication.processEvents()
    
    def finish_loading(self):
        """完成加载"""
        self._progress.setValue(self._progress.maximum())
        self.loading_finished.emit()
        
        # 淡出动画
        self._opacity = 1.0
        self._fade_timer = QTimer(self)
        self._fade_timer.timeout.connect(self._fade_out)
        self._fade_timer.start(16)  # ~60fps
    
    def _fade_out(self):
        """淡出效果"""
        self._opacity -= 0.05
        if self._opacity <= 0:
            self._fade_timer.stop()
            self.close()
        else:
            self.setWindowOpacity(self._opacity)


class LoadingManager:
    """加载管理器"""
    
    def __init__(self):
        self.splash = None
        
    def show_splash(self):
        """显示启动动画"""
        self.splash = SplashScreen()
        self.splash.set_loading_steps([
            "正在加载配置...",
            "正在初始化主题...",
            "正在加载插件...",
            "正在连接 Ollama...",
            "正在准备界面...",
        ])
        self.splash.show()
        QApplication.processEvents()
        return self.splash
    
    def update(self, message: str):
        """更新进度"""
        if self.splash:
            self.splash.update_status(message)
    
    def finish(self):
        """完成加载"""
        if self.splash:
            self.splash.finish_loading()


# 全局加载管理器
_loading_manager = None

def get_loading_manager() -> LoadingManager:
    """获取全局加载管理器"""
    global _loading_manager
    if _loading_manager is None:
        _loading_manager = LoadingManager()
    return _loading_manager
