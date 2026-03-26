# -*- coding: utf-8 -*-
"""
线程安全工具模块
提供线程安全的装饰器和工具函数
"""

import functools
import threading
import time
from logging import getLogger
from typing import Any, Callable, Optional, TypeVar

logger = getLogger(__name__)

T = TypeVar('T')


def thread_safe(lock_attr: str = '_lock'):
    """线程安全装饰器，使用对象的锁属性
    
    Args:
        lock_attr: 锁属性的名称
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            lock = getattr(self, lock_attr, None)
            if lock is None:
                logger.warning(f"对象 {self} 没有锁属性 {lock_attr}")
                return func(self, *args, **kwargs)
            
            with lock:
                return func(self, *args, **kwargs)
        return wrapper
    return decorator


def synchronized(lock: Optional[threading.Lock] = None):
    """同步装饰器，使用指定的锁或创建新锁
    
    Args:
        lock: 可选的锁对象，如果不提供则创建新锁
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        _lock = lock or threading.Lock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            with _lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimiter:
    """速率限制器，限制函数调用频率"""
    
    def __init__(self, max_calls: int, period: float):
        """
        Args:
            max_calls: 在指定时间段内允许的最大调用次数
            period: 时间段（秒）
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: list = []
        self._lock = threading.Lock()
    
    def is_allowed(self) -> bool:
        """检查是否允许调用"""
        with self._lock:
            now = time.time()
            # 移除过期的调用记录
            self.calls = [t for t in self.calls if now - t < self.period]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """作为装饰器使用"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            if self.is_allowed():
                return func(*args, **kwargs)
            else:
                logger.debug(f"函数 {func.__name__} 被速率限制")
                return None
        return wrapper


class ThreadSafeCounter:
    """线程安全的计数器"""
    
    def __init__(self, initial: int = 0):
        self._value = initial
        self._lock = threading.Lock()
    
    def increment(self, delta: int = 1) -> int:
        """增加计数器值"""
        with self._lock:
            self._value += delta
            return self._value
    
    def decrement(self, delta: int = 1) -> int:
        """减少计数器值"""
        with self._lock:
            self._value -= delta
            return self._value
    
    def get(self) -> int:
        """获取当前值"""
        with self._lock:
            return self._value
    
    def set(self, value: int):
        """设置值"""
        with self._lock:
            self._value = value


class ThreadSafeQueue:
    """线程安全的队列，带大小限制"""
    
    def __init__(self, maxsize: int = 0):
        self._queue = []
        self._maxsize = maxsize
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)
    
    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> bool:
        """添加项目到队列"""
        with self._not_full:
            if self._maxsize > 0:
                if not block:
                    if len(self._queue) >= self._maxsize:
                        return False
                elif timeout is None:
                    while len(self._queue) >= self._maxsize:
                        self._not_full.wait()
                elif timeout < 0:
                    raise ValueError("timeout 必须是非负数")
                else:
                    endtime = time.time() + timeout
                    while len(self._queue) >= self._maxsize:
                        remaining = endtime - time.time()
                        if remaining <= 0:
                            return False
                        self._not_full.wait(remaining)
            
            self._queue.append(item)
            self._not_empty.notify()
            return True
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """从队列获取项目"""
        with self._not_empty:
            if not block:
                if not self._queue:
                    raise Exception("队列空")
            elif timeout is None:
                while not self._queue:
                    self._not_empty.wait()
            elif timeout < 0:
                raise ValueError("timeout 必须是非负数")
            else:
                endtime = time.time() + timeout
                while not self._queue:
                    remaining = endtime - time.time()
                    if remaining <= 0:
                        raise Exception("获取超时")
                    self._not_empty.wait(remaining)
            
            item = self._queue.pop(0)
            self._not_full.notify()
            return item
    
    def get_nowait(self) -> Any:
        """非阻塞获取"""
        return self.get(block=False)
    
    def put_nowait(self, item: Any) -> bool:
        """非阻塞添加"""
        return self.put(item, block=False)
    
    def qsize(self) -> int:
        """获取队列大小"""
        with self._lock:
            return len(self._queue)
    
    def empty(self) -> bool:
        """检查队列是否为空"""
        with self._lock:
            return not self._queue
    
    def full(self) -> bool:
        """检查队列是否已满"""
        with self._lock:
            return self._maxsize > 0 and len(self._queue) >= self._maxsize
    
    def clear(self):
        """清空队列"""
        with self._lock:
            self._queue.clear()
            self._not_full.notify_all()


class BackgroundTask:
    """后台任务管理器"""
    
    def __init__(self, max_workers: int = 4):
        self._max_workers = max_workers
        self._workers: list = []
        self._tasks: ThreadSafeQueue = ThreadSafeQueue()
        self._running = False
        self._lock = threading.Lock()
    
    def start(self):
        """启动后台任务管理器"""
        with self._lock:
            if not self._running:
                self._running = True
                for i in range(self._max_workers):
                    worker = threading.Thread(
                        target=self._worker_loop,
                        daemon=True,
                        name=f"BackgroundTaskWorker-{i}"
                    )
                    worker.start()
                    self._workers.append(worker)
                logger.info(f"后台任务管理器已启动，{self._max_workers} 个工作线程")
    
    def stop(self):
        """停止后台任务管理器"""
        with self._lock:
            self._running = False
        
        # 清空任务队列
        self._tasks.clear()
        
        # 等待工作线程结束
        for worker in self._workers:
            if worker.is_alive():
                worker.join(timeout=1.0)
        
        self._workers.clear()
        logger.info("后台任务管理器已停止")
    
    def submit(self, func: Callable, *args, **kwargs) -> bool:
        """提交任务"""
        if not self._running:
            logger.warning("后台任务管理器未运行")
            return False
        
        return self._tasks.put_nowait((func, args, kwargs))
    
    def _worker_loop(self):
        """工作线程循环"""
        while self._running:
            try:
                func, args, kwargs = self._tasks.get(timeout=0.1)
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.exception("执行后台任务时出错", exc_info=e)
            except Exception:
                continue


# 全局后台任务管理器
_background_task_manager: Optional[BackgroundTask] = None
_manager_lock = threading.Lock()


def get_background_task_manager() -> BackgroundTask:
    """获取全局后台任务管理器"""
    global _background_task_manager
    with _manager_lock:
        if _background_task_manager is None:
            _background_task_manager = BackgroundTask()
            _background_task_manager.start()
        return _background_task_manager


def shutdown_background_task_manager():
    """关闭全局后台任务管理器"""
    global _background_task_manager
    with _manager_lock:
        if _background_task_manager is not None:
            _background_task_manager.stop()
            _background_task_manager = None
