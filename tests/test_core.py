"""
核心模块测试
"""

import asyncio
import pytest
from datetime import datetime

from src.core.message import Message, MessageType, MessageBus
from src.core.task import Task, TaskStatus, TaskManager, TaskPriority
from src.core.exceptions import (
    AgentError,
    TaskError,
    MessageError,
    ConfigurationError,
    RetryExhaustedError,
)


class TestMessage:
    """消息类测试"""

    def test_create_message(self):
        """测试创建消息"""
        message = Message(
            type=MessageType.TASK_REQUEST,
            sender="test_sender",
            content={"key": "value"},
        )

        assert message.type == MessageType.TASK_REQUEST
        assert message.sender == "test_sender"
        assert message.content == {"key": "value"}
        assert message.id is not None
        assert message.timestamp is not None

    def test_message_with_receiver(self):
        """测试带接收者的消息"""
        message = Message(
            type=MessageType.TASK_REQUEST,
            sender="sender",
            receiver="receiver",
            content={},
        )

        assert message.receiver == "receiver"

    def test_message_reply(self):
        """测试消息回复"""
        original = Message(
            type=MessageType.TASK_REQUEST,
            sender="sender",
            content={},
        )

        reply = original.reply(
            sender="responder",
            content={"result": "success"},
        )

        assert reply.type == MessageType.AGENT_RESPONSE
        assert reply.sender == "responder"
        assert reply.receiver == "sender"
        assert reply.correlation_id == original.id

    def test_message_priority(self):
        """测试消息优先级"""
        message = Message(
            type=MessageType.TASK_REQUEST,
            sender="sender",
            content={},
            priority=1,
        )

        assert message.priority == 1


class TestTask:
    """任务类测试"""

    def test_create_task(self):
        """测试创建任务"""
        task = Task(
            name="test_task",
            description="测试任务",
        )

        assert task.name == "test_task"
        assert task.status == TaskStatus.PENDING
        assert task.id is not None

    def test_task_status_transitions(self):
        """测试任务状态转换"""
        task = Task(name="test_task")

        # 开始任务
        task.start()
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None

        # 完成任务
        from src.core.task import TaskResult
        result = TaskResult(success=True, data={"output": "test"})
        task.complete(result)
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.result.success is True

    def test_task_failure(self):
        """测试任务失败"""
        task = Task(name="test_task")
        task.start()
        task.fail("测试错误")

        assert task.status == TaskStatus.FAILED
        assert task.result.success is False
        assert task.result.error == "测试错误"

    def test_task_cancellation(self):
        """测试任务取消"""
        task = Task(name="test_task")
        task.start()
        task.cancel()

        assert task.status == TaskStatus.CANCELLED

    def test_task_retry(self):
        """测试任务重试"""
        task = Task(name="test_task", max_retries=3)
        task.start()
        task.fail("错误")
        task.retry()

        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 1

    def test_task_properties(self):
        """测试任务属性"""
        task = Task(name="test_task")

        assert task.is_running is False
        assert task.is_completed is False
        assert task.can_retry is False

        task.start()
        assert task.is_running is True
        assert task.is_completed is False

    def test_task_priority(self):
        """测试任务优先级"""
        task = Task(
            name="test_task",
            priority=TaskPriority.HIGH,
        )

        assert task.priority == TaskPriority.HIGH


class TestMessageBus:
    """消息总线测试"""

    @pytest.mark.asyncio
    async def test_message_bus_subscribe(self):
        """测试消息订阅"""
        bus = MessageBus()
        received_messages = []

        async def handler(message: Message):
            received_messages.append(message)

        bus.subscribe(MessageType.TASK_REQUEST, handler)

        message = Message(
            type=MessageType.TASK_REQUEST,
            sender="test",
            content={},
        )

        await bus.start()
        await bus.publish(message)
        await asyncio.sleep(0.1)  # 等待消息处理
        await bus.stop()

        assert len(received_messages) == 1
        assert received_messages[0].id == message.id

    @pytest.mark.asyncio
    async def test_message_bus_broadcast(self):
        """测试消息广播"""
        bus = MessageBus()
        received_messages = []

        async def handler(message: Message):
            received_messages.append(message)

        bus.subscribe(MessageType.AGENT_BROADCAST, handler)

        message = Message(
            type=MessageType.AGENT_BROADCAST,
            sender="test",
            content={},
        )

        await bus.start()
        await bus.publish(message)
        await asyncio.sleep(0.1)
        await bus.stop()

        assert len(received_messages) == 1

    @pytest.mark.asyncio
    async def test_message_history(self):
        """测试消息历史"""
        bus = MessageBus()

        await bus.start()

        for i in range(5):
            message = Message(
                type=MessageType.TASK_REQUEST,
                sender="test",
                content={"index": i},
            )
            await bus.publish(message)

        await asyncio.sleep(0.1)

        history = bus.get_history(limit=10)
        assert len(history) == 5

        await bus.stop()


class TestTaskManager:
    """任务管理器测试"""

    @pytest.mark.asyncio
    async def test_create_task(self):
        """测试创建任务"""
        manager = TaskManager()

        task = manager.create_task(
            name="test_task",
            description="测试任务",
        )

        assert task.name == "test_task"
        assert manager.get_task(task.id) is not None

    @pytest.mark.asyncio
    async def test_submit_task(self):
        """测试提交任务"""
        manager = TaskManager()
        await manager.start()

        task = manager.create_task(name="test_task")
        await manager.submit_task(task)

        assert task.status == TaskStatus.QUEUED

        await manager.stop()

    @pytest.mark.asyncio
    async def test_task_priority(self):
        """测试任务优先级"""
        manager = TaskManager()

        low_task = manager.create_task(
            name="low_priority",
            priority=TaskPriority.LOW,
        )
        high_task = manager.create_task(
            name="high_priority",
            priority=TaskPriority.HIGH,
        )

        assert low_task.priority == TaskPriority.LOW
        assert high_task.priority == TaskPriority.HIGH

    @pytest.mark.asyncio
    async def test_get_tasks_by_status(self):
        """测试按状态获取任务"""
        manager = TaskManager()

        task1 = manager.create_task(name="task1")
        task2 = manager.create_task(name="task2")
        task3 = manager.create_task(name="task3")

        task2.start()
        task3.start()
        task3.complete(
            from src.core.task import TaskResult
            TaskResult(success=True)
        )

        pending_tasks = manager.get_tasks_by_status(TaskStatus.PENDING)
        running_tasks = manager.get_tasks_by_status(TaskStatus.RUNNING)
        completed_tasks = manager.get_tasks_by_status(TaskStatus.COMPLETED)

        assert len(pending_tasks) == 1
        assert len(running_tasks) == 1
        assert len(completed_tasks) == 1


class TestExceptions:
    """异常类测试"""

    def test_agent_error(self):
        """测试Agent错误"""
        error = AgentError("测试错误", agent_id="test_agent")

        assert str(error) == "测试错误"
        assert error.agent_id == "test_agent"
        assert error.details["agent_id"] == "test_agent"

    def test_task_error(self):
        """测试任务错误"""
        error = TaskError("任务错误", task_id="test_task")

        assert error.task_id == "test_task"
        assert error.details["task_id"] == "test_task"

    def test_retry_exhausted_error(self):
        """测试重试耗尽错误"""
        original_error = ValueError("原始错误")
        error = RetryExhaustedError(
            "重试失败",
            attempts=3,
            max_attempts=3,
            last_error=original_error,
        )

        assert error.attempts == 3
        assert error.max_attempts == 3
        assert error.last_error == original_error
        assert error.details["last_error"] == "原始错误"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
