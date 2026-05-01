"""
Agent基类模块 - 定义Agent的基础结构和通用功能

本模块提供：
- Agent能力定义
- Agent基类
- Agent生命周期管理
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field

from .exceptions import AgentError, AgentTimeoutError, RetryExhaustedError
from .message import Message, MessageBus, MessageType
from .task import Task, TaskManager, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent状态"""

    IDLE = "idle"  # 空闲
    BUSY = "busy"  # 忙碌
    ERROR = "error"  # 错误
    OFFLINE = "offline"  # 离线


class AgentCapability(str, Enum):
    """Agent能力枚举"""

    CODE_ANALYSIS = "code_analysis"  # 代码分析
    ARCHITECTURE_REVIEW = "architecture_review"  # 架构评估
    OPTIMIZATION = "optimization"  # 优化建议
    TEST_GENERATION = "test_generation"  # 测试生成
    ORCHESTRATION = "orchestration"  # 任务编排
    CODE_PARSING = "code_parsing"  # 代码解析
    PATTERN_DETECTION = "pattern_detection"  # 模式检测
    COMPLEXITY_ANALYSIS = "complexity_analysis"  # 复杂度分析


class AgentConfig(BaseModel):
    """
    Agent配置

    属性:
        max_concurrent_tasks: 最大并发任务数
        timeout: 默认超时时间（秒）
        retry_attempts: 重试次数
        retry_delay: 重试延迟（秒）
        enable_logging: 是否启用日志
        log_level: 日志级别
    """

    max_concurrent_tasks: int = 5
    timeout: int = 300
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_logging: bool = True
    log_level: str = "INFO"
    custom_config: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """
    Agent基类

    所有Agent都必须继承此类并实现抽象方法。

    特性:
    - 消息处理
    - 任务执行
    - 生命周期管理
    - 错误处理和重试
    - 性能监控
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "BaseAgent",
        description: str = "",
        capabilities: Optional[Set[AgentCapability]] = None,
        config: Optional[AgentConfig] = None,
        message_bus: Optional[MessageBus] = None,
        task_manager: Optional[TaskManager] = None,
    ):
        """
        初始化Agent

        Args:
            agent_id: Agent唯一标识
            name: Agent名称
            description: Agent描述
            capabilities: Agent能力集合
            config: Agent配置
            message_bus: 消息总线
            task_manager: 任务管理器
        """
        self.agent_id = agent_id or str(uuid4())
        self.name = name
        self.description = description
        self.capabilities = capabilities or set()
        self.config = config or AgentConfig()
        self.message_bus = message_bus
        self.task_manager = task_manager

        # 状态管理
        self._status = AgentStatus.IDLE
        self._current_tasks: Dict[str, Task] = {}
        self._task_handlers: Dict[str, Callable] = {}

        # 性能统计
        self._stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "messages_processed": 0,
            "errors": 0,
        }

        # 初始化日志
        self.logger = logging.getLogger(f"agent.{self.name}")
        if self.config.enable_logging:
            self.logger.setLevel(getattr(logging, self.config.log_level))

        self.logger.info(f"Agent已初始化: {self.name} ({self.agent_id})")

    @property
    def status(self) -> AgentStatus:
        """获取Agent状态"""
        return self._status

    @status.setter
    def status(self, value: AgentStatus) -> None:
        """设置Agent状态"""
        old_status = self._status
        self._status = value
        self.logger.debug(f"状态变更: {old_status} -> {value}")

    @property
    def is_available(self) -> bool:
        """是否可用"""
        return self._status in [AgentStatus.IDLE, AgentStatus.BUSY]

    @property
    def current_task_count(self) -> int:
        """当前任务数量"""
        return len(self._current_tasks)

    @property
    def can_accept_task(self) -> bool:
        """是否可以接受新任务"""
        return (
            self.is_available
            and self.current_task_count < self.config.max_concurrent_tasks
        )

    async def start(self) -> None:
        """启动Agent"""
        self.logger.info(f"Agent启动: {self.name}")
        self.status = AgentStatus.IDLE

        # 订阅消息
        if self.message_bus:
            self._subscribe_messages()

        # 调用子类的初始化方法
        await self.on_start()

    async def stop(self) -> None:
        """停止Agent"""
        self.logger.info(f"Agent停止: {self.name}")

        # 取消当前任务
        for task_id in list(self._current_tasks.keys()):
            await self.cancel_task(task_id)

        self.status = AgentStatus.OFFLINE

        # 调用子类的清理方法
        await self.on_stop()

    async def on_start(self) -> None:
        """Agent启动时的回调，子类可以重写"""
        pass

    async def on_stop(self) -> None:
        """Agent停止时的回调，子类可以重写"""
        pass

    def _subscribe_messages(self) -> None:
        """订阅消息"""
        if not self.message_bus:
            return

        # 订阅任务请求
        self.message_bus.subscribe(
            MessageType.TASK_REQUEST, self._handle_task_message
        )

        # 订阅Agent查询
        self.message_bus.subscribe(
            MessageType.AGENT_QUERY, self._handle_query_message
        )

        # 订阅广播消息
        self.message_bus.subscribe(
            MessageType.AGENT_BROADCAST, self._handle_broadcast_message
        )

    async def _handle_task_message(self, message: Message) -> None:
        """
        处理任务消息

        Args:
            message: 消息
        """
        if message.receiver and message.receiver != self.agent_id:
            return

        self._stats["messages_processed"] += 1
        self.logger.debug(f"收到任务消息: {message.id}")

        # 提取任务信息
        task_data = message.content.get("task")
        if not task_data:
            await self._send_error_response(message, "缺少任务数据")
            return

        # 创建任务并执行
        try:
            task = Task(**task_data)
            result = await self.execute_task(task)
            await self._send_task_response(message, result)
        except Exception as e:
            self.logger.error(f"处理任务失败: {e}", exc_info=True)
            await self._send_error_response(message, str(e))

    async def _handle_query_message(self, message: Message) -> None:
        """
        处理查询消息

        Args:
            message: 消息
        """
        if message.receiver and message.receiver != self.agent_id:
            return

        self._stats["messages_processed"] += 1
        self.logger.debug(f"收到查询消息: {message.id}")

        query_type = message.content.get("query_type")
        try:
            result = await self.handle_query(query_type, message.content)
            response = message.reply(
                sender=self.agent_id,
                content={"result": result},
            )
            await self.message_bus.publish(response)
        except Exception as e:
            self.logger.error(f"处理查询失败: {e}", exc_info=True)
            await self._send_error_response(message, str(e))

    async def _handle_broadcast_message(self, message: Message) -> None:
        """
        处理广播消息

        Args:
            message: 消息
        """
        if message.sender == self.agent_id:
            return  # 忽略自己的广播

        self._stats["messages_processed"] += 1
        await self.handle_broadcast(message)

    async def _send_task_response(
        self, original_message: Message, result: TaskResult
    ) -> None:
        """
        发送任务响应

        Args:
            original_message: 原始消息
            result: 任务结果
        """
        response = original_message.reply(
            sender=self.agent_id,
            content={
                "result": result.dict(),
                "agent_id": self.agent_id,
            },
        )
        await self.message_bus.publish(response)

    async def _send_error_response(
        self, original_message: Message, error: str
    ) -> None:
        """
        发送错误响应

        Args:
            original_message: 原始消息
            error: 错误信息
        """
        response = Message(
            type=MessageType.ERROR,
            sender=self.agent_id,
            receiver=original_message.sender,
            content={
                "error": error,
                "original_message_id": original_message.id,
            },
            correlation_id=original_message.id,
        )
        await self.message_bus.publish(response)

    @abstractmethod
    async def execute_task(self, task: Task) -> TaskResult:
        """
        执行任务（子类必须实现）

        Args:
            task: 任务

        Returns:
            任务结果
        """
        pass

    async def handle_query(
        self, query_type: str, data: Dict[str, Any]
    ) -> Any:
        """
        处理查询（子类可以重写）

        Args:
            query_type: 查询类型
            data: 查询数据

        Returns:
            查询结果
        """
        raise NotImplementedError(f"不支持的查询类型: {query_type}")

    async def handle_broadcast(self, message: Message) -> None:
        """
        处理广播消息（子类可以重写）

        Args:
            message: 广播消息
        """
        pass

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        **kwargs,
    ) -> Any:
        """
        带重试的执行

        Args:
            func: 要执行的函数
            *args: 位置参数
            max_retries: 最大重试次数
            retry_delay: 重试延迟
            **kwargs: 关键字参数

        Returns:
            函数返回值

        Raises:
            RetryExhaustedError: 重试耗尽
        """
        max_retries = max_retries or self.config.retry_attempts
        retry_delay = retry_delay or self.config.retry_delay
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    self.logger.warning(
                        f"执行失败，{retry_delay}秒后重试 "
                        f"(第{attempt + 1}/{max_retries}次): {e}"
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避

        raise RetryExhaustedError(
            f"重试{max_retries}次后仍然失败",
            attempts=max_retries,
            max_attempts=max_retries,
            last_error=last_error,
        )

    async def send_message(
        self,
        receiver: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: int = 5,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        发送消息

        Args:
            receiver: 接收者标识
            message_type: 消息类型
            content: 消息内容
            priority: 优先级
            correlation_id: 关联ID
        """
        if not self.message_bus:
            raise AgentError("消息总线未配置")

        message = Message(
            type=message_type,
            sender=self.agent_id,
            receiver=receiver,
            content=content,
            priority=priority,
            correlation_id=correlation_id,
        )
        await self.message_bus.publish(message)

    async def broadcast_message(
        self,
        message_type: MessageType,
        content: Dict[str, Any],
    ) -> None:
        """
        广播消息

        Args:
            message_type: 消息类型
            content: 消息内容
        """
        if not self.message_bus:
            raise AgentError("消息总线未配置")

        message = Message(
            type=message_type,
            sender=self.agent_id,
            content=content,
        )
        await self.message_bus.broadcast(message)

    async def cancel_task(self, task_id: str) -> None:
        """
        取消任务

        Args:
            task_id: 任务ID
        """
        if task_id in self._current_tasks:
            task = self._current_tasks[task_id]
            task.cancel()
            del self._current_tasks[task_id]
            self.logger.info(f"任务已取消: {task_id}")

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self._status.value,
            "current_tasks": self.current_task_count,
            "capabilities": [c.value for c in self.capabilities],
            "stats": self._stats.copy(),
        }

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.name})>"
