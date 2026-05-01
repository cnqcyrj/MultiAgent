"""
日志工具模块 - 提供统一的日志配置

本模块提供：
- 日志配置
- 日志工厂
- 日志格式化
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "multiagent",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        log_format: 日志格式

    Returns:
        配置好的日志记录器
    """
    # 获取或创建日志记录器
    logger = logging.getLogger(name)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 默认日志格式
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    日志混入类

    为类提供日志功能
    """

    @property
    def logger(self) -> logging.Logger:
        """获取日志记录器"""
        class_name = self.__class__.__name__
        module_name = self.__class__.__module__
        logger_name = f"{module_name}.{class_name}"
        return logging.getLogger(logger_name)


class StructuredLogger:
    """
    结构化日志记录器

    提供结构化的日志记录功能
    """

    def __init__(self, name: str, context: dict = None):
        """
        初始化结构化日志记录器

        Args:
            name: 日志记录器名称
            context: 默认上下文
        """
        self.logger = logging.getLogger(name)
        self.context = context or {}

    def _format_message(self, message: str, **kwargs) -> str:
        """
        格式化消息

        Args:
            message: 消息
            **kwargs: 额外的上下文

        Returns:
            格式化后的消息
        """
        context = {**self.context, **kwargs}
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            return f"{message} [{context_str}]"
        return message

    def info(self, message: str, **kwargs) -> None:
        """记录信息级别日志"""
        self.logger.info(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs) -> None:
        """记录错误级别日志"""
        self.logger.error(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs) -> None:
        """记录警告级别日志"""
        self.logger.warning(self._format_message(message, **kwargs))

    def debug(self, message: str, **kwargs) -> None:
        """记录调试级别日志"""
        self.logger.debug(self._format_message(message, **kwargs))

    def exception(self, message: str, **kwargs) -> None:
        """记录异常级别日志（包含堆栈跟踪）"""
        self.logger.exception(self._format_message(message, **kwargs))

    def with_context(self, **kwargs) -> "StructuredLogger":
        """
        创建带有额外上下文的新日志记录器

        Args:
            **kwargs: 上下文

        Returns:
            新的结构化日志记录器
        """
        new_context = {**self.context, **kwargs}
        return StructuredLogger(self.logger.name, new_context)
