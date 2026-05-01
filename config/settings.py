"""
配置管理模块 - 提供项目配置

本模块提供：
- 配置类定义
- 环境变量加载
- 默认配置
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class Settings:
    """
    项目配置

    属性:
        app_name: 应用名称
        app_version: 应用版本
        debug: 是否启用调试模式
        log_level: 日志级别
        log_file: 日志文件路径
        max_concurrent_tasks: 最大并发任务数
        task_timeout: 任务超时时间（秒）
        retry_attempts: 重试次数
        retry_delay: 重试延迟（秒）
        supported_languages: 支持的编程语言
        default_workflow: 默认工作流类型
        output_directory: 输出目录
        temp_directory: 临时目录
    """

    # 应用配置
    app_name: str = "MultiAgent-CodeForge"
    app_version: str = "1.0.0"
    debug: bool = False

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # 任务配置
    max_concurrent_tasks: int = 10
    task_timeout: int = 300
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Agent配置
    code_analyzer_enabled: bool = True
    architecture_agent_enabled: bool = True
    optimization_agent_enabled: bool = True
    test_generator_enabled: bool = True

    # 分析配置
    supported_languages: list = field(default_factory=lambda: ["python"])
    default_workflow: str = "full_analysis"
    max_file_size: int = 1024 * 1024  # 1MB

    # 输出配置
    output_directory: str = "output"
    temp_directory: str = "temp"
    test_framework: str = "pytest"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "debug": self.debug,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "task_timeout": self.task_timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "supported_languages": self.supported_languages,
            "default_workflow": self.default_workflow,
            "max_file_size": self.max_file_size,
            "output_directory": self.output_directory,
            "temp_directory": self.temp_directory,
            "test_framework": self.test_framework,
        }


def load_settings(env_file: Optional[str] = None) -> Settings:
    """
    加载配置

    Args:
        env_file: 环境变量文件路径

    Returns:
        配置实例
    """
    # 加载环境变量
    if env_file:
        load_dotenv(env_file)
    else:
        # 尝试加载默认的.env文件
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)

    # 从环境变量创建配置
    settings = Settings(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE"),
        max_concurrent_tasks=int(os.getenv("MAX_CONCURRENT_TASKS", "10")),
        task_timeout=int(os.getenv("TASK_TIMEOUT", "300")),
        retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
        retry_delay=float(os.getenv("RETRY_DELAY", "1.0")),
        default_workflow=os.getenv("DEFAULT_WORKFLOW", "full_analysis"),
        output_directory=os.getenv("OUTPUT_DIRECTORY", "output"),
        temp_directory=os.getenv("TEMP_DIRECTORY", "temp"),
        test_framework=os.getenv("TEST_FRAMEWORK", "pytest"),
    )

    return settings


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    获取全局配置

    Returns:
        配置实例
    """
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def update_settings(**kwargs) -> Settings:
    """
    更新配置

    Args:
        **kwargs: 配置参数

    Returns:
        更新后的配置实例
    """
    global _settings
    if _settings is None:
        _settings = load_settings()

    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)

    return _settings


def reset_settings() -> None:
    """重置配置为默认值"""
    global _settings
    _settings = None
