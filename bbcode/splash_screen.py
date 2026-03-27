# -*- coding: utf-8 -*-
"""
BBCode 启动动画/欢迎屏幕
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QLinearGradient, QPixmap, QIcon


class SplashScreen(QWidget):
    """启动动画窗口"""
    
    finished = pyqtSignal()
    
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
        self._setup_effects()
        
        # 加载步骤
        self._loading_steps = [
            "初始化配置...",
            "加载编辑器组件...",
            "加载文件浏览器...",
            "加载AI助手...",
            "加载终端...",
            "准备就绪"
        ]
        self._current_step = 0
        
        # 定时器
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress)
        self._timer.start(500)  # 每500ms更新一次
    
    def _setup_ui(self):
        """设置UI"""
        # 主容器
        self._container = QWidget(self)
        self._container.setGeometry(10, 10, 480, 280)
        self._container.setStyleSheet("""
            QWidget {
                background-color: #2d2d30;
                border-radius: 15px;
                border: 2px solid #3c3c3c;
            }
        """)
        
        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Logo
        self._logo_label = QLabel()
        self._logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_label.setStyleSheet("border: none;")
        # 加载并缩放logo
        logo_pixmap = QPixmap("res/bbc.png")
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._logo_label.setPixmap(scaled_logo)
        layout.addWidget(self._logo_label)
        
        # 标题
        self._title_label = QLabel("BBCode")
        self._title_label.setStyleSheet("""
            QLabel {
                color: #4ec9b0;
                font-size: 36px;
                font-weight: bold;
                border: none;
            }
        """)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title_label)
        
        # 副标题
        self._subtitle_label = QLabel("Python IDE")
        self._subtitle_label.setStyleSheet("""
            QLabel {
                color: #569cd6;
                font-size: 18px;
                border: none;
            }
        """)
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._subtitle_label)
        
        layout.addStretch()
        
        # 状态标签
        self._status_label = QLabel("正在启动...")
        self._status_label.setStyleSheet("""
            QLabel {
                color: #d4d4d4;
                font-size: 12px;
                border: none;
            }
        """)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._status_label)
        
        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e1e1e;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self._progress_bar)
        
        # 版本标签
        self._version_label = QLabel("v3.0.0")
        self._version_label.setStyleSheet("""
            QLabel {
                color: #858585;
                font-size: 10px;
                border: none;
            }
        """)
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._version_label)
    
    def _setup_effects(self):
        """设置阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self._container.setGraphicsEffect(shadow)
    
    def _update_progress(self):
        """更新进度"""
        if self._current_step < len(self._loading_steps):
            step_text = self._loading_steps[self._current_step]
            self._status_label.setText(step_text)
            
            progress = int((self._current_step + 1) / len(self._loading_steps) * 100)
            self._progress_bar.setValue(progress)
            
            self._current_step += 1
        else:
            # 加载完成
            self._timer.stop()
            QTimer.singleShot(500, self._finish)
    
    def _finish(self):
        """完成启动"""
        self.finished.emit()
        self.close()
    
    def show_splash(self):
        """显示启动画面"""
        self.show()
        # 处理事件以显示窗口
        QApplication.processEvents()


def show_splash_screen(app: QApplication) -> SplashScreen:
    """
    显示启动动画
    
    使用示例:
        splash = show_splash_screen(app)
        # ... 初始化其他组件 ...
        splash.finished.connect(main_window.show)
    """
    splash = SplashScreen()
    splash.show_splash()
    return splash
