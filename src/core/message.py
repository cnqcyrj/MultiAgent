"""
消息模块 - 实现Agent间的消息传递机制

本模块提供：
- 消息类型定义
- 消息结构体
- 消息总线（发布-订阅模式）
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """消息类型枚举"""

    # 任务相关
    TASK_REQUEST = "task_request"  # 任务请求
    TASK_RESPONSE = "task_response"  # 任务响应
    TASK_PROGRESS = "task_progress"  # 任务进度更新
    TASK_FAILED = "task_failed"  # 任务失败

    # Agent协作
    AGENT_QUERY = "agent_query"  # Agent间查询
    AGENT_RESPONSE = "agent_response"  # Agent间响应
    AGENT_BROADCAST = "agent_broadcast"  # 广播消息

    # 系统消息
    SYSTEM_EVENT = "system_event"  # 系统事件
    HEARTBEAT = "heartbeat"  # 心跳检测
    ERROR = "error"  # 错误消息

    # 数据交换
    CODE_ANALYSIS = "code_analysis"  # 代码分析结果
    ARCHITECTURE_REVIEW = "architecture_review"  # 架构评估结果
    OPTIMIZATION_SUGGESTION = "optimization_suggestion"  # 优化建议
    TEST_GENERATION = "test_generation"  # 测试生成结果


class Message(BaseModel):
    """
    消息结构体

    属性:
        id: 消息唯一标识
        type: 消息类型
        sender: 发送者Agent标识
        receiver: 接收者Agent标识，None表示广播
        content: 消息内容
        metadata: 元数据
        timestamp: 创建时间
        correlation_id: 关联ID，用于追踪请求-响应链
        priority: 消息优先级 (0-9, 0为最高)
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MessageType
    sender: str
    receiver: Optional[str] = None
    content: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    priority: int = Field(default=5, ge=0, le=9)

    class Config:
        """Pydantic配置"""

        json_encoders = {datetime: lambda v: v.isoformat()}

    def reply(self, sender: str, content: Dict[str, Any], **kwargs) -> "Message":
        """
        创建回复消息

        Args:
            sender: 回复者标识
            content: 回复内容
            **kwargs: 其他参数

        Returns:
            新的回复消息
        """
        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=sender,
            receiver=self.sender,
            content=content,
            correlation_id=self.id,
            priority=self.priority,
            **kwargs,
        )


class MessageBus:
    """
    消息总线 - 实现发布-订阅模式

    特性:
    - 支持点对点消息
    - 支持广播消息
    - 支持消息过滤
    - 异步消息处理
    - 消息持久化（可选）
    """

    def __init__(self, max_queue_size: int = 1000):
        """
        初始化消息总线

        Args:
            max_queue_size: 最大消息队列大小
        """
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._message_history: List[Message] = []
        self._max_history = 1000

        logger.info("消息总线已初始化")

    async def start(self) -> None:
        """启动消息总线"""
        if self._running:
            return

        self._running = True
        self._processor_task = asyncio.create_task(self._process_messages())
        logger.info("消息总线已启动")

    async def stop(self) -> None:
        """停止消息总线"""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("消息总线已停止")

    def subscribe(self, message_type: MessageType, handler: Callable) -> None:
        """
        订阅特定类型的消息

        Args:
            message_type: 消息类型
            handler: 消息处理函数
        """
        if message_type not in self._subscribers:
            self._subscribers[message_type] = []
        self._subscribers[message_type].append(handler)
        logger.debug(f"已订阅消息类型: {message_type}")

    def unsubscribe(self, message_type: MessageType, handler: Callable) -> None:
        """
        取消订阅

        Args:
            message_type: 消息类型
            handler: 消息处理函数
        """
        if message_type in self._subscribers:
            self._subscribers[message_type] = [
                h for h in self._subscribers[message_type] if h != handler
            ]
            logger.debug(f"已取消订阅消息类型: {message_type}")

    async def publish(self, message: Message) -> None:
        """
        发布消息

        Args:
            message: 要发布的消息
        """
        try:
            await self._message_queue.put(message)
            logger.debug(f"消息已入队: {message.id}, 类型: {message.type}")
        except asyncio.QueueFull:
            logger.error(f"消息队列已满，丢弃消息: {message.id}")
            raise

    async def send_direct(self, message: Message) -> None:
        """
        直接发送消息给特定接收者

        Args:
            message: 消息
        """
        if not message.receiver:
            raise ValueError("直接发送消息必须指定接收者")

        await self.publish(message)

    async def broadcast(self, message: Message) -> None:
        """
        广播消息

        Args:
            message: 消息
        """
        message.receiver = None  # 确保是广播
        await self.publish(message)

    async def _process_messages(self) -> None:
        """处理消息队列"""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self._message_queue.get(), timeout=1.0
                )
                await self._dispatch_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"处理消息时发生错误: {e}")

    async def _dispatch_message(self, message: Message) -> None:
        """
        分发消息给订阅者

        Args:
            message: 消息
        """
        # 记录消息历史
        self._message_history.append(message)
        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history:]

        # 获取该类型消息的所有处理器
        handlers = self._subscribers.get(message.type, [])

        # 如果是直接消息，只发送给目标接收者
        if message.receiver:
            handlers = [
                h
                for h in handlers
                if hasattr(h, "__self__")
                and getattr(h.__self__, "agent_id", None) == message.receiver
            ]

        # 并发执行所有处理器
        tasks = []
        for handler in handlers:
            task = asyncio.create_task(self._safe_call_handler(handler, message))
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_call_handler(
        self, handler: Callable, message: Message
    ) -> None:
        """
        安全调用处理器

        Args:
            handler: 处理函数
            message: 消息
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
        except Exception as e:
            logger.error(f"消息处理器执行失败: {e}", exc_info=True)

    def get_history(
        self,
        message_type: Optional[MessageType] = None,
        limit: int = 100,
    ) -> List[Message]:
        """
        获取消息历史

        Args:
            message_type: 消息类型过滤
            limit: 返回数量限制

        Returns:
            消息列表
        """
        messages = self._message_history
        if message_type:
            messages = [m for m in messages if m.type == message_type]
        return messages[-limit:]

    @property
    def queue_size(self) -> int:
        """当前队列大小"""
        return self._message_queue.qsize()
