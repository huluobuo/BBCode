# -*- coding: utf-8 -*-
"""
Shell 多线程处理模块
提供线程安全的输出处理和后台任务执行
"""

import queue
import threading
import time
from logging import getLogger
from typing import Callable, List, Optional, Tuple

logger = getLogger(__name__)


class ShellOutputWorker:
    """后台工作线程，处理 Shell 输出"""
    
    def __init__(self, max_queue_size: int = 1000):
        self._queue = queue.Queue(maxsize=max_queue_size)
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._batch_size = 50  # 每批处理的事件数
        self._batch_timeout = 0.01  # 批量等待超时（秒）
        
    def start(self):
        """启动工作线程"""
        with self._lock:
            if not self._running:
                self._running = True
                self._worker_thread = threading.Thread(
                    target=self._worker_loop,
                    daemon=True,
                    name="ShellOutputWorker"
                )
                self._worker_thread.start()
                logger.info("ShellOutputWorker 已启动")
    
    def stop(self):
        """停止工作线程"""
        with self._lock:
            self._running = False
        
        # 清空队列
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
            logger.info("ShellOutputWorker 已停止")
    
    def submit(self, data: str, stream_name: str, callback: Callable[[str, str], None]) -> bool:
        """提交输出数据到队列
        
        Args:
            data: 输出数据
            stream_name: 流名称（stdout/stderr）
            callback: 处理完成后的回调函数
            
        Returns:
            是否成功提交
        """
        try:
            self._queue.put_nowait((data, stream_name, callback))
            return True
        except queue.Full:
            logger.warning("Shell 输出队列已满，丢弃数据")
            return False
    
    def _worker_loop(self):
        """工作线程主循环"""
        while self._running:
            batch: List[Tuple[str, str, Callable]] = []
            
            # 收集一批数据
            try:
                # 等待第一个数据
                item = self._queue.get(timeout=0.1)
                batch.append(item)
                
                # 收集更多数据（批量处理）
                deadline = time.time() + self._batch_timeout
                while len(batch) < self._batch_size and time.time() < deadline:
                    try:
                        item = self._queue.get_nowait()
                        batch.append(item)
                    except queue.Empty:
                        break
                        
            except queue.Empty:
                continue
            
            # 处理批次数据
            if batch:
                self._process_batch(batch)
    
    def _process_batch(self, batch: List[Tuple[str, str, Callable]]):
        """处理一批数据"""
        # 按 stream_name 分组
        grouped: dict = {}
        for data, stream_name, callback in batch:
            if stream_name not in grouped:
                grouped[stream_name] = []
            grouped[stream_name].append((data, callback))
        
        # 合并相同 stream_name 的数据并回调
        for stream_name, items in grouped.items():
            combined_data = "".join(item[0] for item in items)
            # 使用最后一个回调
            callback = items[-1][2]
            try:
                callback(combined_data, stream_name)
            except Exception as e:
                logger.exception("处理 Shell 输出时出错", exc_info=e)


class ThreadSafeShellBuffer:
    """线程安全的 Shell 缓冲区"""
    
    def __init__(self, max_size: int = 10000):
        self._buffer: List[Tuple[str, str]] = []  # (data, stream_name)
        self._lock = threading.RLock()
        self._max_size = max_size
        self._data_available = threading.Event()
        
    def append(self, data: str, stream_name: str) -> bool:
        """追加数据到缓冲区"""
        with self._lock:
            # 如果缓冲区已满，移除旧数据
            if len(self._buffer) >= self._max_size:
                self._buffer = self._buffer[self._max_size // 4:]  # 移除25%的旧数据
            
            self._buffer.append((data, stream_name))
            self._data_available.set()
            return True
    
    def get_all(self) -> List[Tuple[str, str]]:
        """获取并清空所有数据"""
        with self._lock:
            result = self._buffer.copy()
            self._buffer.clear()
            self._data_available.clear()
            return result
    
    def wait_for_data(self, timeout: float = 0.1) -> bool:
        """等待数据可用"""
        return self._data_available.wait(timeout)
    
    def get_size(self) -> int:
        """获取当前缓冲区大小"""
        with self._lock:
            return len(self._buffer)


class AsyncShellRenderer:
    """异步 Shell 渲染器，在后台线程处理数据，在主线程更新UI"""
    
    def __init__(self, text_widget, update_interval_ms: int = 50):
        self._text_widget = text_widget
        self._buffer = ThreadSafeShellBuffer()
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self._update_interval_ms = update_interval_ms
        self._pending_updates: List[Tuple[str, str]] = []
        self._update_lock = threading.Lock()
        
    def start(self):
        """启动渲染器"""
        if not self._running:
            self._running = True
            self._worker_thread = threading.Thread(
                target=self._render_loop,
                daemon=True,
                name="AsyncShellRenderer"
            )
            self._worker_thread.start()
            logger.info("AsyncShellRenderer 已启动")
            
            # 延迟启动UI更新定时器，确保文本小部件已完全初始化
            try:
                self._text_widget.after(100, self._schedule_ui_update)
            except Exception as e:
                logger.exception("启动UI更新定时器时出错", exc_info=e)
    
    def stop(self):
        """停止渲染器"""
        self._running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
        logger.info("AsyncShellRenderer 已停止")
    
    def submit(self, data: str, stream_name: str):
        """提交数据到缓冲区"""
        self._buffer.append(data, stream_name)
    
    def _render_loop(self):
        """后台渲染循环"""
        while self._running:
            if self._buffer.wait_for_data(timeout=0.1):
                data_batch = self._buffer.get_all()
                if data_batch:
                    with self._update_lock:
                        self._pending_updates.extend(data_batch)
    
    def _schedule_ui_update(self):
        """安排UI更新"""
        if not self._running:
            return
            
        try:
            # 在主线程执行UI更新
            self._text_widget.after(self._update_interval_ms, self._do_ui_update)
        except Exception as e:
            logger.exception("安排UI更新时出错", exc_info=e)
    
    def _do_ui_update(self):
        """执行UI更新（在主线程）"""
        try:
            # 检查文本小部件是否有效
            if not self._text_widget or not self._text_widget.winfo_exists():
                return
            
            with self._update_lock:
                updates = self._pending_updates.copy()
                self._pending_updates.clear()
            
            if updates and hasattr(self._text_widget, '_append_to_io_queue'):
                # 合并相同 stream_name 的数据
                grouped: dict = {}
                for data, stream_name in updates:
                    if stream_name not in grouped:
                        grouped[stream_name] = []
                    grouped[stream_name].append(data)
                
                # 批量追加到IO队列
                for stream_name, data_list in grouped.items():
                    combined_data = "".join(data_list)
                    try:
                        self._text_widget._append_to_io_queue(combined_data, stream_name)
                    except Exception as e:
                        logger.exception("追加到IO队列时出错", exc_info=e)
                
                # 触发UI更新
                if hasattr(self._text_widget, '_update_visible_io'):
                    try:
                        self._text_widget._update_visible_io(None)
                    except Exception as e:
                        logger.exception("更新可见IO时出错", exc_info=e)
                    
        except Exception as e:
            logger.exception("UI更新时出错", exc_info=e)
        finally:
            # 安排下一次更新
            self._schedule_ui_update()


# 全局工作线程实例
_shell_output_worker: Optional[ShellOutputWorker] = None
_worker_lock = threading.Lock()


def get_shell_output_worker() -> ShellOutputWorker:
    """获取全局 Shell 输出工作线程"""
    global _shell_output_worker
    with _worker_lock:
        if _shell_output_worker is None:
            _shell_output_worker = ShellOutputWorker()
            _shell_output_worker.start()
        return _shell_output_worker


def shutdown_shell_output_worker():
    """关闭全局 Shell 输出工作线程"""
    global _shell_output_worker
    with _worker_lock:
        if _shell_output_worker is not None:
            _shell_output_worker.stop()
            _shell_output_worker = None
