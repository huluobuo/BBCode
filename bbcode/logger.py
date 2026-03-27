# -*- coding: utf-8 -*-
"""
BBCode 日志系统
支持文件日志和控制台日志
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class BBCodeLogger:
    """BBCode 日志管理器"""
    
    _instance: Optional['BBCodeLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is not None:
            return
        
        self._logger = logging.getLogger("BBCode")
        self._logger.setLevel(logging.DEBUG)
        
        # 防止重复添加处理器
        if self._logger.handlers:
            return
        
        # 创建日志目录
        log_dir = Path.home() / ".bbcode" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 日志文件路径
        log_file = log_dir / f"bbcode_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 文件处理器 - 按大小轮转
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    @property
    def logger(self) -> logging.Logger:
        """获取日志记录器"""
        return self._logger
    
    def debug(self, msg: str):
        """调试日志"""
        self._logger.debug(msg)
    
    def info(self, msg: str):
        """信息日志"""
        self._logger.info(msg)
    
    def warning(self, msg: str):
        """警告日志"""
        self._logger.warning(msg)
    
    def error(self, msg: str):
        """错误日志"""
        self._logger.error(msg)
    
    def critical(self, msg: str):
        """严重错误日志"""
        self._logger.critical(msg)
    
    def exception(self, msg: str):
        """异常日志"""
        self._logger.exception(msg)


# 全局日志实例
logger = BBCodeLogger()


def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 模块名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    if name:
        return logging.getLogger(f"BBCode.{name}")
    return logger.logger
