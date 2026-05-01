"""
优化建议Agent - 生成优化方案

本模块实现：
- 性能优化建议
- 代码质量优化
- 架构优化建议
- 重构方案生成
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.agent import AgentCapability, AgentConfig, BaseAgent
from ..core.exceptions import OptimizationError
from ..core.message import Message, MessageType
from ..core.task import Task, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class OptimizationCategory(str, Enum):
    """优化类别"""

    PERFORMANCE = "performance"  # 性能优化
    CODE_QUALITY = "code_quality"  # 代码质量
    ARCHITECTURE = "architecture"  # 架构优化
    SECURITY = "security"  # 安全优化
    MAINTAINABILITY = "maintainability"  # 可维护性
    READABILITY = "readability"  # 可读性
    TESTABILITY = "testability"  # 可测试性


class OptimizationPriority(str, Enum):
    """优化优先级"""

    CRITICAL = "critical"  # 紧急
    HIGH = "high"  # 高
    MEDIUM = "medium"  # 中
    LOW = "low"  # 低


class ImpactLevel(str, Enum):
    """影响级别"""

    HIGH = "high"  # 高影响
    MEDIUM = "medium"  # 中影响
    LOW = "low"  # 低影响


@dataclass
class OptimizationItem:
    """优化项"""

    category: OptimizationCategory
    priority: OptimizationPriority
    title: str
    description: str
    current_state: str
    suggested_change: str
    impact: ImpactLevel
    effort_hours: float
    code_example: Optional[str] = None
    file_path: Optional[str] = None
    line_range: Optional[Tuple[int, int]] = None
    related_patterns: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)


@dataclass
class OptimizationPlan:
    """优化计划"""

    items: List[OptimizationItem]
    total_effort_hours: float
    priority_summary: Dict[str, int]
    category_summary: Dict[str, int]
    recommendations: List[str]
    estimated_impact: str
    generation_time: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "items": [
                {
                    "category": item.category.value,
                    "priority": item.priority.value,
                    "title": item.title,
                    "description": item.description,
                    "current_state": item.current_state,
                    "suggested_change": item.suggested_change,
                    "impact": item.impact.value,
                    "effort_hours": item.effort_hours,
                    "code_example": item.code_example,
                    "file_path": item.file_path,
                    "line_range": item.line_range,
                    "related_patterns": item.related_patterns,
                    "benefits": item.benefits,
                    "risks": item.risks,
                }
                for item in self.items
            ],
            "total_effort_hours": self.total_effort_hours,
            "priority_summary": self.priority_summary,
            "category_summary": self.category_summary,
            "recommendations": self.recommendations,
            "estimated_impact": self.estimated_impact,
            "generation_time": self.generation_time,
        }


class OptimizationAgent(BaseAgent):
    """
    优化建议Agent

    负责：
    - 分析代码问题
    - 生成优化建议
    - 评估优化影响
    - 制定优化计划
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        message_bus=None,
        task_manager=None,
    ):
        """
        初始化优化建议Agent

        Args:
            agent_id: Agent标识
            config: 配置
            message_bus: 消息总线
            task_manager: 任务管理器
        """
        super().__init__(
            agent_id=agent_id,
            name="OptimizationAgent",
            description="优化建议Agent，生成优化方案",
            capabilities={
                AgentCapability.OPTIMIZATION,
            },
            config=config,
            message_bus=message_bus,
            task_manager=task_manager,
        )

        # 优化规则库
        self._optimization_rules = self._init_optimization_rules()

        # 重构模式库
        self._refactoring_patterns = self._init_refactoring_patterns()

        logger.info("优化建议Agent已初始化")

    def _init_optimization_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """初始化优化规则库"""
        return {
            "performance": [
                {
                    "pattern": "loop_concatenation",
                    "description": "循环中的字符串拼接",
                    "suggestion": "使用join()方法或列表推导式",
                    "priority": "high",
                },
                {
                    "pattern": "repeated_computation",
                    "description": "重复计算",
                    "suggestion": "使用缓存或记忆化",
                    "priority": "medium",
                },
                {
                    "pattern": "inefficient_data_structure",
                    "description": "低效的数据结构选择",
                    "suggestion": "选择合适的数据结构",
                    "priority": "high",
                },
            ],
            "code_quality": [
                {
                    "pattern": "magic_numbers",
                    "description": "魔法数字",
                    "suggestion": "使用常量替代魔法数字",
                    "priority": "medium",
                },
                {
                    "pattern": "long_parameter_list",
                    "description": "过长的参数列表",
                    "suggestion": "使用参数对象或配置类",
                    "priority": "medium",
                },
                {
                    "pattern": "deep_nesting",
                    "description": "过深的嵌套",
                    "suggestion": "提取方法或使用早返回模式",
                    "priority": "high",
                },
            ],
            "architecture": [
                {
                    "pattern": "god_class",
                    "description": "上帝类",
                    "suggestion": "拆分为多个职责单一的类",
                    "priority": "high",
                },
                {
                    "pattern": "circular_dependency",
                    "description": "循环依赖",
                    "suggestion": "引入依赖注入或中介者模式",
                    "priority": "critical",
                },
            ],
        }

    def _init_refactoring_patterns(self) -> Dict[str, Dict[str, Any]]:
        """初始化重构模式库"""
        return {
            "extract_method": {
                "description": "提取方法",
                "when": "方法过长或包含重复代码",
                "how": "将相关代码块提取为独立方法",
            },
            "replace_temp_with_query": {
                "description": "用查询替代临时变量",
                "when": "临时变量只使用一次",
                "how": "将表达式提取为方法",
            },
            "introduce_parameter_object": {
                "description": "引入参数对象",
                "when": "方法参数过多",
                "how": "将相关参数封装为对象",
            },
            "replace_conditional_with_polymorphism": {
                "description": "用多态替代条件语句",
                "when": "复杂的条件分支",
                "how": "使用策略模式或状态模式",
            },
            "extract_interface": {
                "description": "提取接口",
                "when": "需要解耦依赖",
                "how": "定义抽象接口并注入实现",
            },
        }

    async def execute_task(self, task: Task) -> TaskResult:
        """
        执行优化任务

        Args:
            task: 任务

        Returns:
            任务结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始执行优化任务: {task.id}")

        try:
            # 提取任务参数
            code_analysis = task.input_data.get("code_analysis", {})
            architecture_assessment = task.input_data.get("architecture_assessment", {})
            optimization_scope = task.input_data.get("scope", ["performance", "code_quality"])

            # 生成优化计划
            plan = await self.generate_optimization_plan(
                code_analysis, architecture_assessment, optimization_scope
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                success=True,
                data=plan.to_dict(),
                execution_time=execution_time,
                metadata={
                    "agent_id": self.agent_id,
                    "task_id": task.id,
                },
            )

        except Exception as e:
            self.logger.error(f"优化任务失败: {e}", exc_info=True)
            return TaskResult(
                success=False,
                error=str(e),
            )

    async def generate_optimization_plan(
        self,
        code_analysis: Dict[str, Any],
        architecture_assessment: Dict[str, Any],
        scope: List[str],
    ) -> OptimizationPlan:
        """
        生成优化计划

        Args:
            code_analysis: 代码分析结果
            architecture_assessment: 架构评估结果
            scope: 优化范围

        Returns:
            优化计划
        """
        start_time = datetime.now()
        items = []

        # 根据代码分析生成优化项
        if "code_quality" in scope:
            items.extend(
                await self._generate_code_quality_optimizations(code_analysis)
            )

        # 根据架构评估生成优化项
        if "architecture" in scope:
            items.extend(
                await self._generate_architecture_optimizations(architecture_assessment)
            )

        # 性能优化
        if "performance" in scope:
            items.extend(
                await self._generate_performance_optimizations(code_analysis)
            )

        # 安全优化
        if "security" in scope:
            items.extend(
                await self._generate_security_optimizations(code_analysis)
            )

        # 计算统计信息
        total_effort = sum(item.effort_hours for item in items)

        priority_summary = {}
        for item in items:
            priority = item.priority.value
            priority_summary[priority] = priority_summary.get(priority, 0) + 1

        category_summary = {}
        for item in items:
            category = item.category.value
            category_summary[category] = category_summary.get(category, 0) + 1

        # 生成建议
        recommendations = self._generate_optimization_recommendations(
            items, total_effort, priority_summary
        )

        # 评估影响
        estimated_impact = self._estimate_impact(items)

        execution_time = (datetime.now() - start_time).total_seconds()

        return OptimizationPlan(
            items=items,
            total_effort_hours=total_effort,
            priority_summary=priority_summary,
            category_summary=category_summary,
            recommendations=recommendations,
            estimated_impact=estimated_impact,
            generation_time=execution_time,
        )

    async def _generate_code_quality_optimizations(
        self,
        code_analysis: Dict[str, Any],
    ) -> List[OptimizationItem]:
        """
        生成代码质量优化项

        Args:
            code_analysis: 代码分析结果

        Returns:
            优化项列表
        """
        items = []

        # 检查技术债务
        tech_debts = code_analysis.get("tech_debts", [])
        for debt in tech_debts:
            debt_type = debt.get("type", "")
            severity = debt.get("severity", "medium")

            # 转换优先级
            priority_map = {
                "low": OptimizationPriority.LOW,
                "medium": OptimizationPriority.MEDIUM,
                "high": OptimizationPriority.HIGH,
                "critical": OptimizationPriority.CRITICAL,
            }
            priority = priority_map.get(severity, OptimizationPriority.MEDIUM)

            # 生成优化项
            if debt_type == "long_method":
                items.append(OptimizationItem(
                    category=OptimizationCategory.CODE_QUALITY,
                    priority=priority,
                    title="方法过长重构",
                    description=debt.get("description", ""),
                    current_state=f"方法有 {debt.get('location', {}).get('end_line', 0) - debt.get('location', {}).get('start_line', 0)} 行",
                    suggested_change="将方法拆分为多个职责单一的小方法",
                    impact=ImpactLevel.MEDIUM,
                    effort_hours=2.0,
                    file_path=debt.get("location", {}).get("file"),
                    line_range=(
                        debt.get("location", {}).get("start_line"),
                        debt.get("location", {}).get("end_line"),
                    ),
                    related_patterns=["extract_method"],
                    benefits=["提高可读性", "降低复杂度", "便于测试"],
                    risks=["可能增加方法调用开销"],
                ))
            elif debt_type == "complexity":
                items.append(OptimizationItem(
                    category=OptimizationCategory.CODE_QUALITY,
                    priority=priority,
                    title="降低圈复杂度",
                    description=debt.get("description", ""),
                    current_state=f"圈复杂度为 {debt.get('complexity', 0)}",
                    suggested_change="使用策略模式、早返回等模式降低复杂度",
                    impact=ImpactLevel.HIGH,
                    effort_hours=4.0,
                    file_path=debt.get("location", {}).get("file"),
                    line_range=(
                        debt.get("location", {}).get("start_line"),
                        debt.get("location", {}).get("end_line"),
                    ),
                    related_patterns=["replace_conditional_with_polymorphism"],
                    benefits=["提高可维护性", "减少bug", "便于测试"],
                    risks=["需要更多的类和文件"],
                ))

        # 检查可维护性指数
        metrics = code_analysis.get("metrics", {})
        maintainability = metrics.get("maintainability_index", 100)
        if maintainability < 50:
            items.append(OptimizationItem(
                category=OptimizationCategory.MAINTAINABILITY,
                priority=OptimizationPriority.HIGH,
                title="提高可维护性",
                description="代码可维护性指数较低",
                current_state=f"可维护性指数: {maintainability}",
                suggested_change="重构代码结构，减少技术债务",
                impact=ImpactLevel.HIGH,
                effort_hours=16.0,
                benefits=["降低维护成本", "提高开发效率"],
                risks=["需要较多时间投入"],
            ))

        return items

    async def _generate_architecture_optimizations(
        self,
        architecture_assessment: Dict[str, Any],
    ) -> List[OptimizationItem]:
        """
        生成架构优化项

        Args:
            architecture_assessment: 架构评估结果

        Returns:
            优化项列表
        """
        items = []

        # 检查架构违规
        violations = architecture_assessment.get("violations", [])
        for violation in violations:
            principle = violation.get("principle", "")
            severity = violation.get("severity", "medium")

            priority_map = {
                "low": OptimizationPriority.LOW,
                "medium": OptimizationPriority.MEDIUM,
                "high": OptimizationPriority.HIGH,
                "critical": OptimizationPriority.CRITICAL,
            }
            priority = priority_map.get(severity, OptimizationPriority.MEDIUM)

            items.append(OptimizationItem(
                category=OptimizationCategory.ARCHITECTURE,
                priority=priority,
                title=f"修复{principle}违规",
                description=violation.get("description", ""),
                current_state=violation.get("location", ""),
                suggested_change=violation.get("suggestion", ""),
                impact=ImpactLevel.HIGH if severity in ["high", "critical"] else ImpactLevel.MEDIUM,
                effort_hours=8.0 if severity in ["high", "critical"] else 4.0,
                benefits=["改善架构质量", "提高可扩展性"],
                risks=["可能影响现有功能"],
            ))

        # 检查耦合度
        metrics = architecture_assessment.get("metrics", {})
        coupling = metrics.get("avg_coupling", 0)
        if coupling > 0.7:
            items.append(OptimizationItem(
                category=OptimizationCategory.ARCHITECTURE,
                priority=OptimizationPriority.HIGH,
                title="降低模块耦合度",
                description="模块间耦合度过高",
                current_state=f"平均耦合度: {coupling}",
                suggested_change="使用依赖注入、事件驱动等方式解耦",
                impact=ImpactLevel.HIGH,
                effort_hours=12.0,
                related_patterns=["extract_interface"],
                benefits=["提高模块独立性", "便于测试和替换"],
                risks="可能需要重构调用方式",
            ))

        return items

    async def _generate_performance_optimizations(
        self,
        code_analysis: Dict[str, Any],
    ) -> List[OptimizationItem]:
        """
        生成性能优化项

        Args:
            code_analysis: 代码分析结果

        Returns:
            优化项列表
        """
        items = []

        # 基于代码特征的性能优化建议
        functions = code_analysis.get("functions", [])
        for func in functions:
            complexity = func.get("complexity", 0)
            if complexity > 10:
                items.append(OptimizationItem(
                    category=OptimizationCategory.PERFORMANCE,
                    priority=OptimizationPriority.MEDIUM,
                    title=f"优化函数 {func.get('name', '')}",
                    description=f"函数复杂度为 {complexity}，可能存在性能问题",
                    current_state=f"圈复杂度: {complexity}",
                    suggested_change="简化算法，减少嵌套循环",
                    impact=ImpactLevel.MEDIUM,
                    effort_hours=4.0,
                    benefits=["提高执行效率", "减少资源消耗"],
                    risks=["可能影响代码可读性"],
                ))

        return items

    async def _generate_security_optimizations(
        self,
        code_analysis: Dict[str, Any],
    ) -> List[OptimizationItem]:
        """
        生成安全优化项

        Args:
            code_analysis: 代码分析结果

        Returns:
            优化项列表
        """
        items = []

        # 检查常见的安全问题
        imports = code_analysis.get("imports", [])
        security_risks = ["pickle", "eval", "exec", "subprocess"]
        for risk in security_risks:
            if any(risk in imp for imp in imports):
                items.append(OptimizationItem(
                    category=OptimizationCategory.SECURITY,
                    priority=OptimizationPriority.HIGH,
                    title=f"安全风险: {risk} 使用",
                    description=f"代码中使用了 {risk}，可能存在安全风险",
                    current_state=f"导入了 {risk} 模块",
                    suggested_change=f"审查 {risk} 的使用，确保输入经过验证",
                    impact=ImpactLevel.HIGH,
                    effort_hours=2.0,
                    benefits=["提高安全性", "防止代码注入"],
                    risks=["可能需要修改现有功能"],
                ))

        return items

    def _generate_optimization_recommendations(
        self,
        items: List[OptimizationItem],
        total_effort: float,
        priority_summary: Dict[str, int],
    ) -> List[str]:
        """
        生成优化建议

        Args:
            items: 优化项列表
            total_effort: 总工作量
            priority_summary: 优先级统计

        Returns:
            建议列表
        """
        recommendations = []

        # 基于优先级的建议
        critical_count = priority_summary.get("critical", 0)
        high_count = priority_summary.get("high", 0)

        if critical_count > 0:
            recommendations.append(
                f"存在 {critical_count} 个紧急优化项，建议立即处理"
            )

        if high_count > 0:
            recommendations.append(
                f"存在 {high_count} 个高优先级优化项，建议在当前迭代中处理"
            )

        # 基于工作量的建议
        if total_effort > 40:
            recommendations.append(
                f"总工作量为 {total_effort} 小时，建议分阶段实施"
            )
        elif total_effort > 0:
            recommendations.append(
                f"总工作量为 {total_effort} 小时，可以集中处理"
            )

        # 按类别的建议
        categories = set(item.category for item in items)
        if OptimizationCategory.SECURITY in categories:
            recommendations.append("存在安全优化项，建议优先处理安全问题")

        if OptimizationCategory.ARCHITECTURE in categories:
            recommendations.append("存在架构优化项，建议在功能开发前完成架构优化")

        if not recommendations:
            recommendations.append("当前代码质量良好，建议持续监控和优化")

        return recommendations

    def _estimate_impact(self, items: List[OptimizationItem]) -> str:
        """
        评估优化影响

        Args:
            items: 优化项列表

        Returns:
            影响评估
        """
        if not items:
            return "无优化项"

        high_impact_count = sum(
            1 for item in items if item.impact == ImpactLevel.HIGH
        )
        medium_impact_count = sum(
            1 for item in items if item.impact == ImpactLevel.MEDIUM
        )

        if high_impact_count > 5:
            return "高影响 - 预计显著提升代码质量和可维护性"
        elif high_impact_count > 0 or medium_impact_count > 3:
            return "中等影响 - 预计明显改善代码质量"
        else:
            return "低影响 - 预计小幅改善代码质量"

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
        if query_type == "optimize":
            code_analysis = data.get("code_analysis", {})
            architecture_assessment = data.get("architecture_assessment", {})
            scope = data.get("scope", ["performance", "code_quality"])
            result = await self.generate_optimization_plan(
                code_analysis, architecture_assessment, scope
            )
            return result.to_dict()
        elif query_type == "capabilities":
            return [cap.value for cap in self.capabilities]
        else:
            raise ValueError(f"不支持的查询类型: {query_type}")
