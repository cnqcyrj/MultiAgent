"""
异常模块 - 定义项目自定义异常

本模块提供：
- 基础异常类
- Agent相关异常
- 任务相关异常
- 消息相关异常
- 配置相关异常
"""


class BaseError(Exception):
    """
    基础异常类

    所有自定义异常的父类
    """

    def __init__(self, message: str, details: dict = None):
        """
        初始化异常

        Args:
            message: 错误信息
            details: 详细信息
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class AgentError(BaseError):
    """
    Agent相关异常

    用于Agent执行过程中的错误
    """

    def __init__(
        self,
        message: str,
        agent_id: str = None,
        details: dict = None,
    ):
        """
        初始化Agent异常

        Args:
            message: 错误信息
            agent_id: Agent标识
            details: 详细信息
        """
        super().__init__(message, details)
        self.agent_id = agent_id
        if agent_id:
            self.details["agent_id"] = agent_id


class AgentNotFoundError(AgentError):
    """Agent未找到异常"""

    pass


class AgentTimeoutError(AgentError):
    """Agent超时异常"""

    pass


class AgentBusyError(AgentError):
    """Agent忙碌异常"""

    pass


class TaskError(BaseError):
    """
    任务相关异常

    用于任务执行过程中的错误
    """

    def __init__(
        self,
        message: str,
        task_id: str = None,
        details: dict = None,
    ):
        """
        初始化任务异常

        Args:
            message: 错误信息
            task_id: 任务ID
            details: 详细信息
        """
        super().__init__(message, details)
        self.task_id = task_id
        if task_id:
            self.details["task_id"] = task_id


class TaskNotFoundError(TaskError):
    """任务未找到异常"""

    pass


class TaskDependencyError(TaskError):
    """任务依赖错误"""

    pass


class TaskTimeoutError(TaskError):
    """任务超时异常"""

    pass


class TaskCancelledError(TaskError):
    """任务取消异常"""

    pass


class MessageError(BaseError):
    """
    消息相关异常

    用于消息传递过程中的错误
    """

    def __init__(
        self,
        message: str,
        message_id: str = None,
        details: dict = None,
    ):
        """
        初始化消息异常

        Args:
            message: 错误信息
            message_id: 消息ID
            details: 详细信息
        """
        super().__init__(message, details)
        self.message_id = message_id
        if message_id:
            self.details["message_id"] = message_id


class MessageDeliveryError(MessageError):
    """消息投递失败异常"""

    pass


class MessageTimeoutError(MessageError):
    """消息超时异常"""

    pass


class ConfigurationError(BaseError):
    """
    配置相关异常

    用于配置加载和验证过程中的错误
    """

    def __init__(
        self,
        message: str,
        config_key: str = None,
        details: dict = None,
    ):
        """
        初始化配置异常

        Args:
            message: 错误信息
            config_key: 配置键
            details: 详细信息
        """
        super().__init__(message, details)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class RetryExhaustedError(BaseError):
    """
    重试耗尽异常

    当重试次数达到上限时抛出
    """

    def __init__(
        self,
        message: str,
        attempts: int = 0,
        max_attempts: int = 0,
        last_error: Exception = None,
        details: dict = None,
    ):
        """
        初始化重试耗尽异常

        Args:
            message: 错误信息
            attempts: 已尝试次数
            max_attempts: 最大尝试次数
            last_error: 最后一次错误
            details: 详细信息
        """
        super().__init__(message, details)
        self.attempts = attempts
        self.max_attempts = max_attempts
        self.last_error = last_error
        self.details.update({
            "attempts": attempts,
            "max_attempts": max_attempts,
            "last_error": str(last_error) if last_error else None,
        })


class AnalysisError(BaseError):
    """
    分析相关异常

    用于代码分析过程中的错误
    """

    def __init__(
        self,
        message: str,
        file_path: str = None,
        details: dict = None,
    ):
        """
        初始化分析异常

        Args:
            message: 错误信息
            file_path: 文件路径
            details: 详细信息
        """
        super().__init__(message, details)
        self.file_path = file_path
        if file_path:
            self.details["file_path"] = file_path


class CodeParsingError(AnalysisError):
    """代码解析异常"""

    pass


class ArchitectureViolationError(AnalysisError):
    """架构违规异常"""

    pass


class OptimizationError(BaseError):
    """
    优化相关异常

    用于优化建议生成过程中的错误
    """

    pass


class TestGenerationError(BaseError):
    """
    测试生成相关异常

    用于测试生成过程中的错误
    """

    def __init__(
        self,
        message: str,
        target_function: str = None,
        details: dict = None,
    ):
        """
        初始化测试生成异常

        Args:
            message: 错误信息
            target_function: 目标函数
            details: 详细信息
        """
        super().__init__(message, details)
        self.target_function = target_function
        if target_function:
            self.details["target_function"] = target_function
