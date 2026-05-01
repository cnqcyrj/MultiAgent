"""
任务模块 - 任务定义和管理

本模块提供：
- 任务状态定义
- 任务结构体
- 任务管理器
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"  # 等待执行
    QUEUED = "queued"  # 已排队
    RUNNING = "running"  # 执行中
    PAUSED = "paused"  # 已暂停
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"  # 超时


class TaskPriority(str, Enum):
    """任务优先级"""

    CRITICAL = "critical"  # 紧急
    HIGH = "high"  # 高
    MEDIUM = "medium"  # 中
    LOW = "low"  # 低


class TaskResult(BaseModel):
    """
    任务结果

    属性:
        success: 是否成功
        data: 结果数据
        error: 错误信息
        execution_time: 执行时间（秒）
        metadata: 元数据
    """

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """
    任务结构体

    属性:
        id: 任务唯一标识
        name: 任务名称
        description: 任务描述
        status: 任务状态
        priority: 任务优先级
        assigned_agent: 分配的Agent标识
        input_data: 输入数据
        output_data: 输出数据
        result: 任务结果
        created_at: 创建时间
        started_at: 开始时间
        completed_at: 完成时间
        timeout: 超时时间（秒）
        retry_count: 重试次数
        max_retries: 最大重试次数
        dependencies: 依赖任务ID列表
        metadata: 元数据
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_agent: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[TaskResult] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout: int = 300  # 默认5分钟超时
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic配置"""

        json_encoders = {datetime: lambda v: v.isoformat()}

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self.status == TaskStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.TIMEOUT,
        ]

    @property
    def can_retry(self) -> bool:
        """是否可以重试"""
        return (
            self.status == TaskStatus.FAILED
            and self.retry_count < self.max_retries
        )

    def start(self) -> None:
        """开始任务"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        logger.info(f"任务开始执行: {self.id} - {self.name}")

    def complete(self, result: TaskResult) -> None:
        """
        完成任务

        Args:
            result: 任务结果
        """
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        if self.started_at:
            result.execution_time = (
                self.completed_at - self.started_at
            ).total_seconds()
        logger.info(f"任务完成: {self.id} - {self.name}, 耗时: {result.execution_time:.2f}秒")

    def fail(self, error: str) -> None:
        """
        任务失败

        Args:
            error: 错误信息
        """
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.result = TaskResult(success=False, error=error)
        if self.started_at:
            self.result.execution_time = (
                self.completed_at - self.started_at
            ).total_seconds()
        logger.error(f"任务失败: {self.id} - {self.name}, 错误: {error}")

    def cancel(self) -> None:
        """取消任务"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
        logger.info(f"任务已取消: {self.id} - {self.name}")

    def retry(self) -> None:
        """重试任务"""
        self.retry_count += 1
        self.status = TaskStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.result = None
        logger.info(f"任务重试: {self.id} - {self.name}, 第{self.retry_count}次重试")


class TaskManager:
    """
    任务管理器

    特性:
    - 任务队列管理
    - 任务依赖处理
    - 任务超时控制
    - 任务重试机制
    - 并发任务执行
    """

    def __init__(self, max_concurrent_tasks: int = 10):
        """
        初始化任务管理器

        Args:
            max_concurrent_tasks: 最大并发任务数
        """
        self._tasks: Dict[str, Task] = {}
        self._task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._max_concurrent = max_concurrent_tasks
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None

        logger.info(f"任务管理器已初始化，最大并发数: {max_concurrent_tasks}")

    async def start(self) -> None:
        """启动任务管理器"""
        if self._running:
            return

        self._running = True
        self._processor_task = asyncio.create_task(self._process_queue())
        logger.info("任务管理器已启动")

    async def stop(self) -> None:
        """停止任务管理器"""
        self._running = False

        # 取消所有运行中的任务
        for task_id, task in self._running_tasks.items():
            task.cancel()
            if task_id in self._tasks:
                self._tasks[task_id].cancel()

        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        logger.info("任务管理器已停止")

    def create_task(
        self,
        name: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        input_data: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        max_retries: int = 3,
        dependencies: Optional[List[str]] = None,
        assigned_agent: Optional[str] = None,
        **kwargs,
    ) -> Task:
        """
        创建任务

        Args:
            name: 任务名称
            description: 任务描述
            priority: 任务优先级
            input_data: 输入数据
            timeout: 超时时间
            max_retries: 最大重试次数
            dependencies: 依赖任务ID列表
            assigned_agent: 分配的Agent
            **kwargs: 其他参数

        Returns:
            创建的任务
        """
        task = Task(
            name=name,
            description=description,
            priority=priority,
            input_data=input_data or {},
            timeout=timeout,
            max_retries=max_retries,
            dependencies=dependencies or [],
            assigned_agent=assigned_agent,
            metadata=kwargs,
        )
        self._tasks[task.id] = task
        logger.info(f"任务已创建: {task.id} - {task.name}")
        return task

    async def submit_task(self, task: Task) -> None:
        """
        提交任务到队列

        Args:
            task: 任务
        """
        # 检查依赖是否满足
        if task.dependencies:
            for dep_id in task.dependencies:
                if dep_id not in self._tasks:
                    raise ValueError(f"依赖任务不存在: {dep_id}")
                dep_task = self._tasks[dep_id]
                if not dep_task.is_completed:
                    raise ValueError(f"依赖任务未完成: {dep_id}")

        task.status = TaskStatus.QUEUED
        # 优先级数值越小优先级越高
        priority_value = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }[task.priority]

        await self._task_queue.put((priority_value, task.id))
        logger.info(f"任务已提交: {task.id} - {task.name}")

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务

        Args:
            task_id: 任务ID

        Returns:
            任务或None
        """
        return self._tasks.get(task_id)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        按状态获取任务

        Args:
            status: 任务状态

        Returns:
            任务列表
        """
        return [task for task in self._tasks.values() if task.status == status]

    def get_tasks_by_agent(self, agent_id: str) -> List[Task]:
        """
        按Agent获取任务

        Args:
            agent_id: Agent标识

        Returns:
            任务列表
        """
        return [
            task
            for task in self._tasks.values()
            if task.assigned_agent == agent_id
        ]

    async def _process_queue(self) -> None:
        """处理任务队列"""
        while self._running:
            try:
                # 从队列获取任务
                try:
                    priority, task_id = await asyncio.wait_for(
                        self._task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                task = self._tasks.get(task_id)
                if not task or task.status != TaskStatus.QUEUED:
                    continue

                # 检查并发限制
                if len(self._running_tasks) >= self._max_concurrent:
                    # 重新入队
                    await self._task_queue.put((priority, task_id))
                    await asyncio.sleep(0.1)
                    continue

                # 启动任务执行
                exec_task = asyncio.create_task(
                    self._execute_task(task)
                )
                self._running_tasks[task_id] = exec_task

            except Exception as e:
                logger.error(f"处理任务队列时发生错误: {e}")

    async def _execute_task(self, task: Task) -> None:
        """
        执行任务

        Args:
            task: 任务
        """
        async with self._semaphore:
            task.start()
            try:
                # 这里应该调用实际的任务处理器
                # 由子类或外部注入
                logger.info(f"正在执行任务: {task.id} - {task.name}")
                # 模拟任务执行
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                task.cancel()
            except Exception as e:
                task.fail(str(e))
                # 检查是否需要重试
                if task.can_retry:
                    task.retry()
                    await self.submit_task(task)
            finally:
                self._running_tasks.pop(task.id, None)

    @property
    def pending_count(self) -> int:
        """等待中的任务数量"""
        return len(self.get_tasks_by_status(TaskStatus.PENDING)) + \
               len(self.get_tasks_by_status(TaskStatus.QUEUED))

    @property
    def running_count(self) -> int:
        """运行中的任务数量"""
        return len(self._running_tasks)

    @property
    def completed_count(self) -> int:
        """已完成的任务数量"""
        return len(self.get_tasks_by_status(TaskStatus.COMPLETED))
