# -*- coding: utf-8 -*-
"""
BBCode PyQt6 核心模块
提供全局访问器和核心功能
"""

import sys
import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING, cast, Any, Dict, List, Callable

if TYPE_CHECKING:
    from thonny.qt_workbench import QtWorkbench
    from plugins.qt_terminal import TerminalWidget
    from thonny.qt_runner import Runner

# 全局变量
_workbench: Optional["QtWorkbench"] = None
_runner: Optional["Runner"] = None
_shell: Optional["TerminalWidget"] = None


def get_workbench() -> "QtWorkbench":
    """获取全局 Workbench 实例"""
    if _workbench is None:
        raise RuntimeError("Workbench not initialized")
    return _workbench


def get_runner() -> "Runner":
    """获取全局 Runner 实例"""
    if _runner is None:
        raise RuntimeError("Runner not initialized")
    return _runner


def get_shell(create: bool = True) -> Optional["TerminalWidget"]:
    """获取全局 Shell 实例"""
    return _shell


def set_workbench(workbench: "QtWorkbench"):
    """设置全局 Workbench 实例"""
    global _workbench
    _workbench = workbench


def set_runner(runner: "Runner"):
    """设置全局 Runner 实例"""
    global _runner
    _runner = runner


def set_shell(shell: "TerminalWidget"):
    """设置全局 Shell 实例"""
    global _shell
    _shell = shell


# 版本信息
def get_version() -> str:
    """获取版本号"""
    try:
        version_file = Path(__file__).parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
    except Exception:
        pass
    return "2.0.0"


# 路径相关
def get_thonny_user_dir() -> str:
    """获取用户配置目录"""
    if sys.platform == "win32":
        base_dir = os.environ.get("APPDATA", Path.home())
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        base_dir = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    
    thonny_dir = Path(base_dir) / "BBCodePyQt6"
    thonny_dir.mkdir(parents=True, exist_ok=True)
    return str(thonny_dir)


def get_vendored_libs_dir() -> str:
    """获取 vendored 库目录"""
    return str(Path(__file__).parent / "vendored_libs")


# 调试模式
_in_debug_mode: Optional[bool] = None


def in_debug_mode() -> bool:
    """检查是否在调试模式"""
    global _in_debug_mode
    if _in_debug_mode is None:
        _in_debug_mode = os.environ.get("BBCODE_DEBUG", "0") in ["1", "True", "true"]
    return _in_debug_mode


# 便携模式
def is_portable() -> bool:
    """检查是否为便携模式"""
    exe_dir = Path(sys.executable).parent
    portable_marker = exe_dir / "portable_bbcode.ini"
    return portable_marker.exists()


# 语言支持
def tr(message: str) -> str:
    """翻译函数（简化版）"""
    # TODO: 实现完整的国际化支持
    return message


# 日志
import logging

logger = logging.getLogger("bbcode")


def set_logging_level(level=None):
    """设置日志级别"""
    if level is None:
        level = logging.DEBUG if in_debug_mode() else logging.INFO
    
    logging.getLogger("bbcode").setLevel(level)


# 兼容性导入
# 为了兼容原版代码，提供相同的接口
from thonny.qt_config import get_option, set_option, has_option, Configuration

__all__ = [
    "get_workbench",
    "get_runner",
    "get_shell",
    "set_workbench",
    "set_runner",
    "set_shell",
    "get_version",
    "get_thonny_user_dir",
    "get_vendored_libs_dir",
    "in_debug_mode",
    "is_portable",
    "tr",
    "get_option",
    "set_option",
    "has_option",
    "Configuration",
]
