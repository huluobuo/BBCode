# -*- coding: utf-8 -*-
"""
BBCode PyQt6 Runner 模块
负责运行和调试 Python 代码
"""

import os
import sys
import subprocess
import threading
import queue
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QProcess
from PyQt6.QtWidgets import QMessageBox

from thonny.qt_core import get_workbench, get_shell, get_option, set_option


class BackendState(Enum):
    """后端状态"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"


class Runner(QObject):
    """代码运行管理器"""
    
    # 信号
    state_changed = pyqtSignal(BackendState)
    output_received = pyqtSignal(str)  # stdout
    error_received = pyqtSignal(str)   # stderr
    execution_started = pyqtSignal(str)  # filename
    execution_finished = pyqtSignal(str, int)  # filename, return_code
    
    def __init__(self):
        super().__init__()
        
        self._state = BackendState.STOPPED
        self._process: Optional[QProcess] = None
        self._current_file: Optional[str] = None
        self._backend_name: str = "LocalCPython"
        self._command_queue: queue.Queue = queue.Queue()
        
        # 后端配置
        self._backends: Dict[str, Dict[str, Any]] = {
            "LocalCPython": {
                "name": "Local Python 3",
                "executable": sys.executable,
                "type": "local",
            },
            "MicroPython": {
                "name": "MicroPython (ESP32)",
                "executable": "mpremote",
                "type": "remote",
            },
            "CircuitPython": {
                "name": "CircuitPython",
                "executable": "circuitpython",
                "type": "remote",
            },
        }
    
    def get_state(self) -> BackendState:
        """获取当前状态"""
        return self._state
    
    def _set_state(self, state: BackendState):
        """设置状态"""
        self._state = state
        self.state_changed.emit(state)
    
    def get_backend_name(self) -> str:
        """获取当前后端名称"""
        return self._backend_name
    
    def set_backend(self, backend_name: str):
        """设置后端"""
        if backend_name in self._backends:
            self._backend_name = backend_name
            set_option("run.backend_name", backend_name)
    
    def get_available_backends(self) -> List[str]:
        """获取可用后端列表"""
        return list(self._backends.keys())
    
    def run_script(self, filename: str, args: List[str] = None):
        """运行脚本"""
        if self._state != BackendState.STOPPED:
            self.stop_execution()
        
        self._current_file = filename
        self._set_state(BackendState.STARTING)
        
        backend = self._backends.get(self._backend_name)
        if not backend:
            QMessageBox.critical(None, "错误", f"未知后端: {self._backend_name}")
            return
        
        # 创建进程
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        
        # 构建命令
        if backend["type"] == "local":
            cmd = [backend["executable"], filename]
            if args:
                cmd.extend(args)
        else:
            # 远程后端
            cmd = [backend["executable"], "run", filename]
        
        # 设置工作目录
        work_dir = str(Path(filename).parent)
        self._process.setWorkingDirectory(work_dir)
        
        # 启动进程
        self._process.start(cmd[0], cmd[1:])
        
        self._set_state(BackendState.RUNNING)
        self.execution_started.emit(filename)
    
    def run_current_script(self):
        """运行当前编辑器中的脚本"""
        workbench = get_workbench()
        editor = workbench._editor_tabs.get_current_editor()
        
        if not editor:
            QMessageBox.warning(None, "警告", "没有打开的脚本")
            return
        
        filename = editor.get_file_path()
        if not filename:
            # 先保存文件
            if not workbench._editor_tabs.save_current_file():
                return
            filename = editor.get_file_path()
        
        if filename:
            self.run_script(filename)
    
    def debug_script(self, filename: str = None):
        """调试脚本"""
        if filename is None:
            # 获取当前文件
            workbench = get_workbench()
            editor = workbench._editor_tabs.get_current_editor()
            if not editor:
                QMessageBox.warning(None, "警告", "没有打开的脚本")
                return
            filename = editor.get_file_path()
            if not filename:
                QMessageBox.warning(None, "警告", "请先保存文件")
                return
        
        self._current_file = filename
        self._set_state(BackendState.STARTING)
        
        # 使用 pdb 进行调试
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        
        # 构建调试命令
        cmd = [sys.executable, "-m", "pdb", filename]
        
        # 设置工作目录
        work_dir = str(Path(filename).parent)
        self._process.setWorkingDirectory(work_dir)
        
        # 启动进程
        self._process.start(cmd[0], cmd[1:])
        
        self._set_state(BackendState.RUNNING)
        self.execution_started.emit(filename)
        
        # 输出调试提示
        shell = get_shell()
        if shell:
            shell.write(f"\n[开始调试: {filename}]\n")
            shell.write("调试命令:\n")
            shell.write("  n - 执行下一行\n")
            shell.write("  s - 进入函数\n")
            shell.write("  c - 继续执行\n")
            shell.write("  b - 设置断点\n")
            shell.write("  p - 打印变量\n")
            shell.write("  q - 退出调试\n\n")
    
    def debug_current_script(self):
        """调试当前脚本"""
        self.debug_script()
    
    def stop_execution(self):
        """停止执行"""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._set_state(BackendState.STOPPING)
            self._process.terminate()
            
            # 等待进程结束
            if not self._process.waitForFinished(3000):
                self._process.kill()
        
        self._set_state(BackendState.STOPPED)
    
    def interrupt_execution(self):
        """中断执行（发送 Ctrl+C）"""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            # 在 Windows 上发送 Ctrl+C 比较复杂
            # 这里使用 terminate 作为替代
            self._process.terminate()
    
    def _on_stdout(self):
        """处理标准输出"""
        if self._process:
            data = self._process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
            self.output_received.emit(data)
            
            # 同时输出到 shell
            shell = get_shell()
            if shell:
                shell.write(data)
    
    def _on_stderr(self):
        """处理标准错误"""
        if self._process:
            data = self._process.readAllStandardError().data().decode('utf-8', errors='ignore')
            self.error_received.emit(data)
            
            # 同时输出到 shell
            shell = get_shell()
            if shell:
                shell.write_error(data)
    
    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        """进程结束处理"""
        self._set_state(BackendState.STOPPED)
        
        if self._current_file:
            self.execution_finished.emit(self._current_file, exit_code)
        
        # 输出提示
        shell = get_shell()
        if shell:
            if exit_code == 0:
                shell.write(f"\n[程序已完成，退出代码: {exit_code}]\n")
            else:
                shell.write_error(f"\n[程序异常退出，代码: {exit_code}]\n")
    
    def execute_command(self, command: str):
        """执行命令（用于 Shell）"""
        if self._state == BackendState.RUNNING:
            # 如果正在运行程序，将命令发送到程序的标准输入
            if self._process:
                self._process.write(command.encode() + b'\n')
        else:
            # 否则在本地执行
            self._execute_local_command(command)
    
    def _execute_local_command(self, command: str):
        """在本地执行命令"""
        import subprocess
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            shell = get_shell()
            if shell:
                if result.stdout:
                    shell.write(result.stdout)
                if result.stderr:
                    shell.write_error(result.stderr)
        except Exception as e:
            shell = get_shell()
            if shell:
                shell.write_error(f"命令执行错误: {e}\n")
    
    def send_input(self, text: str):
        """向运行的程序发送输入"""
        if self._process and self._state == BackendState.RUNNING:
            self._process.write(text.encode() + b'\n')
    
    def is_running(self) -> bool:
        """检查是否有程序在运行"""
        return self._state == BackendState.RUNNING
    
    def get_current_file(self) -> Optional[str]:
        """获取当前运行的文件"""
        return self._current_file


# 全局 Runner 实例
_runner: Optional[Runner] = None


def get_runner() -> Runner:
    """获取全局 Runner 实例"""
    global _runner
    if _runner is None:
        _runner = Runner()
    return _runner


def set_runner(runner: Runner):
    """设置全局 Runner 实例"""
    global _runner
    _runner = runner
