"""
编排Agent - 协调其他Agent协作

本模块实现：
- 任务分解和分发
- Agent协作协调
- 结果聚合
- 工作流管理
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from ..core.agent import AgentCapability, AgentConfig, BaseAgent
from ..core.exceptions import AgentError, TaskError, TaskDependencyError
from ..core.message import Message, MessageType, MessageBus
from ..core.task import Task, TaskManager, TaskResult, TaskStatus, TaskPriority
from .code_analyzer import CodeAnalyzerAgent
from .architecture import ArchitectureAgent
from .optimization import OptimizationAgent
from .test_generator import TestGeneratorAgent

logger = logging.getLogger(__name__)


class WorkflowStage(str, Enum):
    """工作流阶段"""

    INITIALIZATION = "initialization"  # 初始化
    CODE_ANALYSIS = "code_analysis"  # 代码分析
    ARCHITECTURE_REVIEW = "architecture_review"  # 架构评估
    OPTIMIZATION = "optimization"  # 优化建议
    TEST_GENERATION = "test_generation"  # 测试生成
    RESULT_AGGREGATION = "result_aggregation"  # 结果聚合
    COMPLETED = "completed"  # 完成


class WorkflowStatus(str, Enum):
    """工作流状态"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """工作流步骤"""

    stage: WorkflowStage
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Workflow:
    """工作流"""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    steps: List[WorkflowStep] = field(default_factory=list)
    current_stage: WorkflowStage = WorkflowStage.INITIALIZATION
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "current_stage": self.current_stage.value,
            "steps": [
                {
                    "stage": step.stage.value,
                    "agent_id": step.agent_id,
                    "task_id": step.task_id,
                    "status": step.status.value,
                    "error": step.error,
                }
                for step in self.steps
            ],
            "results": self.results,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class OrchestratorAgent(BaseAgent):
    """
    编排Agent

    负责：
    - 协调各个专业Agent
    - 管理工作流
    - 分解和分发任务
    - 聚合分析结果
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        message_bus: Optional[MessageBus] = None,
        task_manager: Optional[TaskManager] = None,
    ):
        """
        初始化编排Agent

        Args:
            agent_id: Agent标识
            config: 配置
            message_bus: 消息总线
            task_manager: 任务管理器
        """
        super().__init__(
            agent_id=agent_id,
            name="OrchestratorAgent",
            description="编排Agent，协调其他Agent协作",
            capabilities={
                AgentCapability.ORCHESTRATION,
            },
            config=config,
            message_bus=message_bus,
            task_manager=task_manager,
        )

        # 子Agent注册表
        self._agents: Dict[str, BaseAgent] = {}

        # 工作流管理
        self._workflows: Dict[str, Workflow] = {}

        # 工作流模板
        self._workflow_templates = self._init_workflow_templates()

        logger.info("编排Agent已初始化")

    def _init_workflow_templates(self) -> Dict[str, List[WorkflowStage]]:
        """初始化工作流模板"""
        return {
            "full_analysis": [
                WorkflowStage.CODE_ANALYSIS,
                WorkflowStage.ARCHITECTURE_REVIEW,
                WorkflowStage.OPTIMIZATION,
                WorkflowStage.TEST_GENERATION,
                WorkflowStage.RESULT_AGGREGATION,
            ],
            "quick_analysis": [
                WorkflowStage.CODE_ANALYSIS,
                WorkflowStage.OPTIMIZATION,
                WorkflowStage.RESULT_AGGREGATION,
            ],
            "architecture_review": [
                WorkflowStage.CODE_ANALYSIS,
                WorkflowStage.ARCHITECTURE_REVIEW,
                WorkflowStage.RESULT_AGGREGATION,
            ],
            "test_generation": [
                WorkflowStage.CODE_ANALYSIS,
                WorkflowStage.TEST_GENERATION,
                WorkflowStage.RESULT_AGGREGATION,
            ],
        }

    async def on_start(self) -> None:
        """Agent启动时的回调"""
        # 初始化子Agent
        await self._initialize_agents()
        logger.info("编排Agent已启动，子Agent已初始化")

    async def on_stop(self) -> None:
        """Agent停止时的回调"""
        # 停止所有子Agent
        for agent in self._agents.values():
            await agent.stop()
        logger.info("编排Agent已停止，子Agent已停止")

    async def _initialize_agents(self) -> None:
        """初始化子Agent"""
        # 创建消息总线（如果未提供）
        if not self.message_bus:
            self.message_bus = MessageBus()
            await self.message_bus.start()

        # 创建任务管理器（如果未提供）
        if not self.task_manager:
            self.task_manager = TaskManager()
            await self.task_manager.start()

        # 初始化代码分析Agent
        self._agents["code_analyzer"] = CodeAnalyzerAgent(
            agent_id="code_analyzer",
            config=self.config,
            message_bus=self.message_bus,
            task_manager=self.task_manager,
        )

        # 初始化架构评估Agent
        self._agents["architecture"] = ArchitectureAgent(
            agent_id="architecture",
            config=self.config,
            message_bus=self.message_bus,
            task_manager=self.task_manager,
        )

        # 初始化优化建议Agent
        self._agents["optimization"] = OptimizationAgent(
            agent_id="optimization",
            config=self.config,
            message_bus=self.message_bus,
            task_manager=self.task_manager,
        )

        # 初始化测试生成Agent
        self._agents["test_generator"] = TestGeneratorAgent(
            agent_id="test_generator",
            config=self.config,
            message_bus=self.message_bus,
            task_manager=self.task_manager,
        )

        # 启动所有子Agent
        for agent in self._agents.values():
            await agent.start()

    def register_agent(self, agent_id: str, agent: BaseAgent) -> None:
        """
        注册子Agent

        Args:
            agent_id: Agent标识
            agent: Agent实例
        """
        self._agents[agent_id] = agent
        logger.info(f"已注册Agent: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        获取子Agent

        Args:
            agent_id: Agent标识

        Returns:
            Agent实例或None
        """
        return self._agents.get(agent_id)

    def get_agents_by_capability(
        self, capability: AgentCapability
    ) -> List[BaseAgent]:
        """
        根据能力获取Agent

        Args:
            capability: 能力

        Returns:
            Agent列表
        """
        return [
            agent
            for agent in self._agents.values()
            if capability in agent.capabilities
        ]

    async def execute_task(self, task: Task) -> TaskResult:
        """
        执行任务

        Args:
            task: 任务

        Returns:
            任务结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始执行编排任务: {task.id}")

        try:
            # 提取任务参数
            source_code = task.input_data.get("source_code", "")
            file_path = task.input_data.get("file_path", "<string>")
            workflow_type = task.input_data.get("workflow_type", "full_analysis")
            options = task.input_data.get("options", {})

            if not source_code:
                return TaskResult(
                    success=False,
                    error="缺少源代码",
                )

            # 执行工作流
            workflow = await self.execute_workflow(
                source_code=source_code,
                file_path=file_path,
                workflow_type=workflow_type,
                options=options,
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                success=True,
                data=workflow.to_dict(),
                execution_time=execution_time,
                metadata={
                    "agent_id": self.agent_id,
                    "task_id": task.id,
                    "workflow_id": workflow.id,
                },
            )

        except Exception as e:
            self.logger.error(f"编排任务失败: {e}", exc_info=True)
            return TaskResult(
                success=False,
                error=str(e),
            )

    async def execute_workflow(
        self,
        source_code: str,
        file_path: str = "<string>",
        workflow_type: str = "full_analysis",
        options: Dict[str, Any] = None,
    ) -> Workflow:
        """
        执行工作流

        Args:
            source_code: 源代码
            file_path: 文件路径
            workflow_type: 工作流类型
            options: 选项

        Returns:
            工作流实例
        """
        # 获取工作流模板
        template = self._workflow_templates.get(workflow_type)
        if not template:
            raise ValueError(f"未知的工作流类型: {workflow_type}")

        # 创建工作流
        workflow = Workflow(
            name=f"{workflow_type}_{file_path}",
            description=f"对 {file_path} 执行 {workflow_type} 分析",
        )

        # 初始化步骤
        for stage in template:
            step = WorkflowStep(stage=stage)
            workflow.steps.append(step)

        # 保存工作流
        self._workflows[workflow.id] = workflow

        # 设置初始上下文
        workflow.context = {
            "source_code": source_code,
            "file_path": file_path,
            "options": options or {},
        }

        # 执行工作流
        try:
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()

            await self._execute_workflow_steps(workflow)

            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()

            self.logger.info(f"工作流完成: {workflow.id}")

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            workflow.completed_at = datetime.now()
            self.logger.error(f"工作流失败: {e}", exc_info=True)
            raise

        return workflow

    async def _execute_workflow_steps(self, workflow: Workflow) -> None:
        """
        执行工作流步骤

        Args:
            workflow: 工作流
        """
        for step in workflow.steps:
            workflow.current_stage = step.stage
            step.status = TaskStatus.RUNNING
            step.started_at = datetime.now()

            try:
                # 根据阶段执行相应的Agent
                result = await self._execute_stage(step, workflow.context)

                # 保存结果
                step.output_data = result
                step.status = TaskStatus.COMPLETED
                step.completed_at = datetime.now()

                # 更新工作流上下文
                self._update_workflow_context(workflow, step)

                self.logger.info(f"阶段完成: {step.stage.value}")

            except Exception as e:
                step.status = TaskStatus.FAILED
                step.error = str(e)
                step.completed_at = datetime.now()
                self.logger.error(f"阶段失败: {step.stage.value} - {e}")
                raise

    async def _execute_stage(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        执行单个阶段

        Args:
            step: 工作流步骤
            context: 工作流上下文

        Returns:
            阶段结果
        """
        stage = step.stage

        if stage == WorkflowStage.CODE_ANALYSIS:
            return await self._execute_code_analysis(context)
        elif stage == WorkflowStage.ARCHITECTURE_REVIEW:
            return await self._execute_architecture_review(context)
        elif stage == WorkflowStage.OPTIMIZATION:
            return await self._execute_optimization(context)
        elif stage == WorkflowStage.TEST_GENERATION:
            return await self._execute_test_generation(context)
        elif stage == WorkflowStage.RESULT_AGGREGATION:
            return await self._execute_result_aggregation(context)
        else:
            raise ValueError(f"未知的阶段: {stage}")

    async def _execute_code_analysis(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行代码分析

        Args:
            context: 上下文

        Returns:
            分析结果
        """
        agent = self._agents.get("code_analyzer")
        if not agent:
            raise AgentError("代码分析Agent未注册")

        task = Task(
            name="代码分析",
            input_data={
                "source_code": context["source_code"],
                "file_path": context["file_path"],
                "language": context.get("options", {}).get("language", "python"),
            },
        )

        result = await agent.execute_task(task)
        if not result.success:
            raise TaskError(f"代码分析失败: {result.error}")

        return result.data

    async def _execute_architecture_review(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行架构评估

        Args:
            context: 上下文

        Returns:
            评估结果
        """
        agent = self._agents.get("architecture")
        if not agent:
            raise AgentError("架构评估Agent未注册")

        # 从上下文中获取项目结构信息
        code_analysis = context.get("code_analysis", {})
        project_structure = {
            "files": [context["file_path"]],
            "modules": [],
        }

        task = Task(
            name="架构评估",
            input_data={
                "project_structure": project_structure,
                "code_files": {context["file_path"]: context["source_code"]},
                "dependencies": {},
            },
        )

        result = await agent.execute_task(task)
        if not result.success:
            raise TaskError(f"架构评估失败: {result.error}")

        return result.data

    async def _execute_optimization(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行优化建议

        Args:
            context: 上下文

        Returns:
            优化建议
        """
        agent = self._agents.get("optimization")
        if not agent:
            raise AgentError("优化建议Agent未注册")

        task = Task(
            name="优化建议",
            input_data={
                "code_analysis": context.get("code_analysis", {}),
                "architecture_assessment": context.get("architecture_review", {}),
                "scope": context.get("options", {}).get(
                    "optimization_scope",
                    ["performance", "code_quality", "architecture"]
                ),
            },
        )

        result = await agent.execute_task(task)
        if not result.success:
            raise TaskError(f"优化建议失败: {result.error}")

        return result.data

    async def _execute_test_generation(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行测试生成

        Args:
            context: 上下文

        Returns:
            测试生成结果
        """
        agent = self._agents.get("test_generator")
        if not agent:
            raise AgentError("测试生成Agent未注册")

        code_analysis = context.get("code_analysis", {})
        target_functions = [
            f.get("name") for f in code_analysis.get("functions", [])
        ]

        task = Task(
            name="测试生成",
            input_data={
                "code_analysis": code_analysis,
                "target_functions": target_functions,
                "test_types": context.get("options", {}).get(
                    "test_types", ["unit", "edge_case"]
                ),
                "framework": context.get("options", {}).get(
                    "test_framework", "pytest"
                ),
            },
        )

        result = await agent.execute_task(task)
        if not result.success:
            raise TaskError(f"测试生成失败: {result.error}")

        return result.data

    async def _execute_result_aggregation(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行结果聚合

        Args:
            context: 上下文

        Returns:
            聚合结果
        """
        # 聚合所有分析结果
        aggregated = {
            "summary": {},
            "code_analysis": context.get("code_analysis", {}),
            "architecture_review": context.get("architecture_review", {}),
            "optimization": context.get("optimization", {}),
            "test_generation": context.get("test_generation", {}),
        }

        # 生成摘要
        summary = {
            "file_path": context.get("file_path", ""),
            "analysis_timestamp": datetime.now().isoformat(),
            "metrics": {},
            "key_findings": [],
            "recommendations": [],
        }

        # 从代码分析中提取指标
        code_analysis = context.get("code_analysis", {})
        if code_analysis:
            summary["metrics"]["lines_of_code"] = code_analysis.get("loc", 0)
            summary["metrics"]["function_count"] = len(
                code_analysis.get("functions", [])
            )
            summary["metrics"]["class_count"] = len(
                code_analysis.get("classes", [])
            )
            summary["metrics"]["complexity"] = code_analysis.get(
                "complexity", {}
            ).get("total", 0)

            # 技术债务
            tech_debts = code_analysis.get("tech_debts", [])
            if tech_debts:
                summary["key_findings"].append(
                    f"发现 {len(tech_debts)} 个技术债务"
                )

        # 从架构评估中提取信息
        architecture_review = context.get("architecture_review", {})
        if architecture_review:
            violations = architecture_review.get("violations", [])
            if violations:
                summary["key_findings"].append(
                    f"发现 {len(violations)} 个架构违规"
                )

            health_score = architecture_review.get("metrics", {}).get(
                "health_score", 100
            )
            summary["metrics"]["architecture_health"] = health_score

        # 从优化建议中提取信息
        optimization = context.get("optimization", {})
        if optimization:
            items = optimization.get("items", [])
            if items:
                summary["key_findings"].append(
                    f"生成 {len(items)} 个优化建议"
                )
                summary["recommendations"].extend(
                    optimization.get("recommendations", [])
                )

        # 从测试生成中提取信息
        test_generation = context.get("test_generation", {})
        if test_generation:
            test_suite = test_generation.get("test_suite", {})
            test_cases = test_suite.get("test_cases", [])
            if test_cases:
                summary["key_findings"].append(
                    f"生成 {len(test_cases)} 个测试用例"
                )
                summary["metrics"]["test_coverage_target"] = test_suite.get(
                    "coverage_target", 0
                )

        aggregated["summary"] = summary

        return aggregated

    def _update_workflow_context(
        self, workflow: Workflow, step: WorkflowStep
    ) -> None:
        """
        更新工作流上下文

        Args:
            workflow: 工作流
            step: 完成的步骤
        """
        # 将步骤结果添加到上下文
        workflow.context[step.stage.value] = step.output_data
        workflow.results[step.stage.value] = step.output_data

    async def handle_query(
        self, query_type: str, data: Dict[str, Any]
    ) -> Any:
        """
        处理查询

        Args:
            query_type: 查询类型
            data: 查询数据

        Returns:
            查询结果
        """
        if query_type == "execute_workflow":
            source_code = data.get("source_code", "")
            file_path = data.get("file_path", "<string>")
            workflow_type = data.get("workflow_type", "full_analysis")
            options = data.get("options", {})
            workflow = await self.execute_workflow(
                source_code, file_path, workflow_type, options
            )
            return workflow.to_dict()
        elif query_type == "get_workflow":
            workflow_id = data.get("workflow_id")
            workflow = self._workflows.get(workflow_id)
            if workflow:
                return workflow.to_dict()
            return None
        elif query_type == "list_workflows":
            return [w.to_dict() for w in self._workflows.values()]
        elif query_type == "agents":
            return {
                agent_id: agent.get_stats()
                for agent_id, agent in self._agents.items()
            }
        elif query_type == "capabilities":
            return [cap.value for cap in self.capabilities]
        else:
            raise ValueError(f"不支持的查询类型: {query_type}")

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        获取工作流

        Args:
            workflow_id: 工作流ID

        Returns:
            工作流实例或None
        """
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> List[Workflow]:
        """
        列出所有工作流

        Returns:
            工作流列表
        """
        return list(self._workflows.values())

    def get_agent_stats(self) -> Dict[str, Any]:
        """
        获取所有Agent的统计信息

        Returns:
            统计信息字典
        """
        return {
            "orchestrator": self.get_stats(),
            "agents": {
                agent_id: agent.get_stats()
                for agent_id, agent in self._agents.items()
            },
        }
