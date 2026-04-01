# -*- coding: utf-8 -*-
"""
BBCode 启动动画/欢迎屏幕 - 纯3D旋转效果，透明背景
使用 Blender 模型 (logo.blend)
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from bbcode.logger import get_logger

log = get_logger("SplashScreen")

# 导入3D Logo渲染组件
try:
    from bbcode.logo3d_widget import Logo3DWidget
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False
    try:
        from bbcode.logo3d_widget import Logo3DFallbackWidget
    except ImportError:
        Logo3DFallbackWidget = None


class SplashScreen(QWidget):
    """启动动画窗口 - 纯3D旋转"""

    finished = pyqtSignal()

    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        # 设置窗口大小 - 只显示3D模型
        self.setFixedSize(200, 200)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 居中显示
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

        self._setup_ui()
        self._setup_audio()

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

        # 定时器 - 控制加载进度
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress)
        self._timer.start(200)  # 200ms更新一次

    def _setup_ui(self):
        """设置UI - 只显示3D模型"""
        # 主容器 - 透明背景
        self._container = QWidget(self)
        self._container.setGeometry(0, 0, 200, 200)
        self._container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 3D Logo - 使用 Blender 模型
        if HAS_OPENGL:
            self._logo_widget = Logo3DWidget()
        elif Logo3DFallbackWidget:
            self._logo_widget = Logo3DFallbackWidget()
        else:
            # 最后的备用方案
            from PyQt6.QtWidgets import QLabel
            self._logo_widget = QLabel("BBCode")
            self._logo_widget.setStyleSheet("""
                QLabel {
                    color: #4ec9b0;
                    font-size: 24px;
                    font-weight: bold;
                    background-color: transparent;
                }
            """)

        layout.addWidget(self._logo_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_audio(self):
        """设置音频播放器"""
        self._audio_player = None
        self._audio_output = None

        try:
            self._audio_player = QMediaPlayer()
            self._audio_output = QAudioOutput()
            self._audio_player.setAudioOutput(self._audio_output)

            # 设置音频文件路径
            audio_path = os.path.join(os.path.dirname(__file__), '..', 'msc', 'M50000338Hjy28NaGu.mp3')
            if os.path.exists(audio_path):
                self._audio_player.setSource(QUrl.fromLocalFile(audio_path))
                log.info(f"音频文件已加载: {audio_path}")
            else:
                log.warning(f"音频文件不存在: {audio_path}")
        except Exception as e:
            log.error(f"初始化音频播放器失败: {e}")

    def _play_finish_sound(self):
        """播放完成音效"""
        if self._audio_player and self._audio_output:
            try:
                self._audio_output.setVolume(0.5)  # 设置音量为50%
                self._audio_player.play()
                log.info("播放完成音效")
            except Exception as e:
                log.error(f"播放音频失败: {e}")

    def _update_progress(self):
        """更新进度"""
        if self._current_step < len(self._loading_steps):
            step_text = self._loading_steps[self._current_step]
            log.info(step_text)
            self._current_step += 1
        else:
            # 加载完成
            self._timer.stop()
            log.info("启动动画完成")
            QTimer.singleShot(300, self._finish)

    def _finish(self):
        """完成启动"""
        # 播放完成音效
        self._play_finish_sound()

        # 停止logo动画
        self._logo_widget.stop_animation()
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
