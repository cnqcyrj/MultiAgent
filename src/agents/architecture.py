"""
架构评估Agent - 评估代码架构合理性

本模块实现：
- 架构模式识别
- 依赖关系分析
- 模块化评估
- 设计原则检查
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path

from ..core.agent import AgentCapability, AgentConfig, BaseAgent
from ..core.exceptions import AnalysisError, ArchitectureViolationError
from ..core.message import Message, MessageType
from ..core.task import Task, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class ArchitecturePattern(str, Enum):
    """架构模式"""

    MVC = "mvc"  # Model-View-Controller
    MVP = "mvp"  # Model-View-Presenter
    MVVM = "mvvm"  # Model-View-ViewModel
    CLEAN_ARCHITECTURE = "clean_architecture"  # 整洁架构
    HEXAGONAL = "hexagonal"  # 六边形架构
    MICROSERVICES = "microservices"  # 微服务架构
    LAYERED = "layered"  # 分层架构
    EVENT_DRIVEN = "event_driven"  # 事件驱动架构
    PLUGIN = "plugin"  # 插件架构
    UNKNOWN = "unknown"  # 未知模式


class DesignPrinciple(str, Enum):
    """设计原则"""

    SRP = "single_responsibility"  # 单一职责原则
    OCP = "open_closed"  # 开闭原则
    LSP = "liskov_substitution"  # 里氏替换原则
    ISP = "interface_segregation"  # 接口隔离原则
    DIP = "dependency_inversion"  # 依赖倒置原则
    DRY = "dont_repeat_yourself"  # DRY原则
    KISS = "keep_it_simple"  # KISS原则
    YAGNI = "you_arent_gonna_need_it"  # YAGNI原则


@dataclass
class ModuleInfo:
    """模块信息"""

    name: str
    path: str
    dependencies: List[str]
    dependents: List[str]
    public_api: List[str]
    internal_classes: List[str]
    cohesion_score: float  # 内聚度
    coupling_score: float  # 耦合度


@dataclass
class DependencyRelation:
    """依赖关系"""

    source: str
    target: str
    dependency_type: str  # import, inheritance, composition, aggregation
    strength: float  # 依赖强度


@dataclass
class ArchitectureViolation:
    """架构违规"""

    principle: DesignPrinciple
    severity: str  # low, medium, high, critical
    location: str
    description: str
    suggestion: str
    impact: str


@dataclass
class ArchitectureAssessment:
    """架构评估结果"""

    detected_pattern: ArchitecturePattern
    modules: List[ModuleInfo]
    dependencies: List[DependencyRelation]
    violations: List[ArchitectureViolation]
    metrics: Dict[str, float]
    recommendations: List[str]
    assessment_time: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "detected_pattern": self.detected_pattern.value,
            "modules": [
                {
                    "name": m.name,
                    "path": m.path,
                    "dependencies": m.dependencies,
                    "dependents": m.dependents,
                    "cohesion_score": m.cohesion_score,
                    "coupling_score": m.coupling_score,
                }
                for m in self.modules
            ],
            "dependencies": [
                {
                    "source": d.source,
                    "target": d.target,
                    "type": d.dependency_type,
                    "strength": d.strength,
                }
                for d in self.dependencies
            ],
            "violations": [
                {
                    "principle": v.principle.value,
                    "severity": v.severity,
                    "location": v.location,
                    "description": v.description,
                    "suggestion": v.suggestion,
                    "impact": v.impact,
                }
                for v in self.violations
            ],
            "metrics": self.metrics,
            "recommendations": self.recommendations,
            "assessment_time": self.assessment_time,
        }


class ArchitectureAgent(BaseAgent):
    """
    架构评估Agent

    负责：
    - 识别架构模式
    - 分析依赖关系
    - 评估设计原则
    - 生成架构建议
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        message_bus=None,
        task_manager=None,
    ):
        """
        初始化架构评估Agent

        Args:
            agent_id: Agent标识
            config: 配置
            message_bus: 消息总线
            task_manager: 任务管理器
        """
        super().__init__(
            agent_id=agent_id,
            name="ArchitectureAgent",
            description="架构评估Agent，评估代码架构合理性",
            capabilities={
                AgentCapability.ARCHITECTURE_REVIEW,
                AgentCapability.PATTERN_DETECTION,
            },
            config=config,
            message_bus=message_bus,
            task_manager=task_manager,
        )

        # 架构模式特征
        self._pattern_signatures = self._init_pattern_signatures()

        # 设计原则检查器
        self._principle_checkers = self._init_principle_checkers()

        logger.info("架构评估Agent已初始化")

    def _init_pattern_signatures(self) -> Dict[ArchitecturePattern, Dict[str, Any]]:
        """初始化架构模式特征"""
        return {
            ArchitecturePattern.MVC: {
                "required_components": ["model", "view", "controller"],
                "directory_patterns": ["models", "views", "controllers"],
                "class_suffixes": ["Model", "View", "Controller"],
            },
            ArchitecturePattern.CLEAN_ARCHITECTURE: {
                "required_components": ["entity", "use_case", "adapter", "framework"],
                "directory_patterns": ["domain", "application", "infrastructure", "interfaces"],
                "layer_dependencies": {
                    "domain": [],
                    "application": ["domain"],
                    "infrastructure": ["application", "domain"],
                    "interfaces": ["application", "domain"],
                },
            },
            ArchitecturePattern.HEXAGONAL: {
                "required_components": ["port", "adapter"],
                "directory_patterns": ["ports", "adapters", "domain"],
            },
            ArchitecturePattern.LAYERED: {
                "required_components": ["presentation", "business", "data"],
                "directory_patterns": ["presentation", "business", "data", "persistence"],
            },
        }

    def _init_principle_checkers(self) -> Dict[DesignPrinciple, callable]:
        """初始化设计原则检查器"""
        return {
            DesignPrinciple.SRP: self._check_srp,
            DesignPrinciple.OCP: self._check_ocp,
            DesignPrinciple.DIP: self._check_dip,
            DesignPrinciple.DRY: self._check_dry,
        }

    async def execute_task(self, task: Task) -> TaskResult:
        """
        执行架构评估任务

        Args:
            task: 任务

        Returns:
            任务结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始执行架构评估任务: {task.id}")

        try:
            # 提取任务参数
            project_structure = task.input_data.get("project_structure", {})
            code_files = task.input_data.get("code_files", {})
            dependencies = task.input_data.get("dependencies", {})

            # 执行评估
            result = await self.assess_architecture(
                project_structure, code_files, dependencies
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                success=True,
                data=result.to_dict(),
                execution_time=execution_time,
                metadata={
                    "agent_id": self.agent_id,
                    "task_id": task.id,
                },
            )

        except Exception as e:
            self.logger.error(f"架构评估失败: {e}", exc_info=True)
            return TaskResult(
                success=False,
                error=str(e),
            )

    async def assess_architecture(
        self,
        project_structure: Dict[str, Any],
        code_files: Dict[str, str],
        dependencies: Dict[str, List[str]],
    ) -> ArchitectureAssessment:
        """
        评估架构

        Args:
            project_structure: 项目结构
            code_files: 代码文件内容
            dependencies: 依赖关系

        Returns:
            评估结果
        """
        start_time = datetime.now()

        # 1. 识别架构模式
        detected_pattern = self._detect_pattern(project_structure, code_files)

        # 2. 分析模块
        modules = await self._analyze_modules(project_structure, code_files)

        # 3. 分析依赖关系
        dep_relations = self._analyze_dependencies(dependencies, modules)

        # 4. 检查设计原则
        violations = await self._check_design_principles(
            modules, dep_relations, code_files
        )

        # 5. 计算指标
        metrics = self._calculate_architecture_metrics(
            modules, dep_relations, violations
        )

        # 6. 生成建议
        recommendations = self._generate_recommendations(
            detected_pattern, modules, violations, metrics
        )

        execution_time = (datetime.now() - start_time).total_seconds()

        return ArchitectureAssessment(
            detected_pattern=detected_pattern,
            modules=modules,
            dependencies=dep_relations,
            violations=violations,
            metrics=metrics,
            recommendations=recommendations,
            assessment_time=execution_time,
        )

    def _detect_pattern(
        self,
        project_structure: Dict[str, Any],
        code_files: Dict[str, str],
    ) -> ArchitecturePattern:
        """
        检测架构模式

        Args:
            project_structure: 项目结构
            code_files: 代码文件

        Returns:
            检测到的架构模式
        """
        # 提取目录结构
        directories = set()
        if "directories" in project_structure:
            directories = set(project_structure["directories"])
        elif "root" in project_structure:
            # 从根目录提取
            root = project_structure["root"]
            for key in project_structure:
                if key != "root":
                    directories.add(key)

        # 匹配模式
        best_match = ArchitecturePattern.UNKNOWN
        best_score = 0

        for pattern, signature in self._pattern_signatures.items():
            score = 0
            expected_dirs = set(signature.get("directory_patterns", []))

            # 计算目录匹配度
            if expected_dirs:
                matched = len(expected_dirs.intersection(directories))
                score = matched / len(expected_dirs)

            if score > best_score:
                best_score = score
                best_match = pattern

        # 如果匹配度太低，返回未知
        if best_score < 0.3:
            return ArchitecturePattern.UNKNOWN

        return best_match

    async def _analyze_modules(
        self,
        project_structure: Dict[str, Any],
        code_files: Dict[str, str],
    ) -> List[ModuleInfo]:
        """
        分析模块

        Args:
            project_structure: 项目结构
            code_files: 代码文件

        Returns:
            模块信息列表
        """
        modules = []

        # 从项目结构中提取模块
        if "modules" in project_structure:
            for module_data in project_structure["modules"]:
                module = ModuleInfo(
                    name=module_data.get("name", ""),
                    path=module_data.get("path", ""),
                    dependencies=module_data.get("dependencies", []),
                    dependents=module_data.get("dependents", []),
                    public_api=module_data.get("public_api", []),
                    internal_classes=module_data.get("internal_classes", []),
                    cohesion_score=module_data.get("cohesion", 0.5),
                    coupling_score=module_data.get("coupling", 0.5),
                )
                modules.append(module)
        else:
            # 从目录结构推断模块
            for key, value in project_structure.items():
                if key == "root":
                    continue
                if isinstance(value, dict) or isinstance(value, list):
                    module = ModuleInfo(
                        name=key,
                        path=key,
                        dependencies=[],
                        dependents=[],
                        public_api=[],
                        internal_classes=[],
                        cohesion_score=0.5,
                        coupling_score=0.5,
                    )
                    modules.append(module)

        return modules

    def _analyze_dependencies(
        self,
        dependencies: Dict[str, List[str]],
        modules: List[ModuleInfo],
    ) -> List[DependencyRelation]:
        """
        分析依赖关系

        Args:
            dependencies: 依赖数据
            modules: 模块列表

        Returns:
            依赖关系列表
        """
        relations = []

        for source, targets in dependencies.items():
            for target in targets:
                # 确定依赖类型
                dep_type = "import"
                if "extends" in target or "inherits" in target:
                    dep_type = "inheritance"
                elif "uses" in target:
                    dep_type = "composition"
                elif "has" in target:
                    dep_type = "aggregation"

                relation = DependencyRelation(
                    source=source,
                    target=target.replace("extends:", "").replace("uses:", "").replace("has:", ""),
                    dependency_type=dep_type,
                    strength=1.0,  # 默认强度
                )
                relations.append(relation)

        return relations

    async def _check_design_principles(
        self,
        modules: List[ModuleInfo],
        dependencies: List[DependencyRelation],
        code_files: Dict[str, str],
    ) -> List[ArchitectureViolation]:
        """
        检查设计原则

        Args:
            modules: 模块列表
            dependencies: 依赖关系
            code_files: 代码文件

        Returns:
            违规列表
        """
        violations = []

        # 执行各项检查
        violations.extend(self._check_srp(modules, code_files))
        violations.extend(self._check_ocp(modules, code_files))
        violations.extend(self._check_dip(modules, dependencies))
        violations.extend(self._check_dry(code_files))

        return violations

    def _check_srp(
        self,
        modules: List[ModuleInfo],
        code_files: Dict[str, str],
    ) -> List[ArchitectureViolation]:
        """
        检查单一职责原则

        Args:
            modules: 模块列表
            code_files: 代码文件

        Returns:
            违规列表
        """
        violations = []

        for module in modules:
            # 检查模块是否承担了过多职责
            if len(module.public_api) > 20:
                violations.append(ArchitectureViolation(
                    principle=DesignPrinciple.SRP,
                    severity="medium",
                    location=module.name,
                    description=f"模块 {module.name} 有 {len(module.public_api)} 个公开API，可能承担了过多职责",
                    suggestion=f"建议将模块 {module.name} 拆分为多个更专注的模块",
                    impact="增加维护难度，降低代码可读性",
                ))

        return violations

    def _check_ocp(
        self,
        modules: List[ModuleInfo],
        code_files: Dict[str, str],
    ) -> List[ArchitectureViolation]:
        """
        检查开闭原则

        Args:
            modules: 模块列表
            code_files: 代码文件

        Returns:
            违规列表
        """
        violations = []

        # 检查代码中的switch/if-else链
        for file_path, content in code_files.items():
            # 简单检测：如果文件中有很多elif，可能违反OCP
            elif_count = content.count("elif")
            if elif_count > 5:
                violations.append(ArchitectureViolation(
                    principle=DesignPrinciple.OCP,
                    severity="medium",
                    location=file_path,
                    description=f"文件 {file_path} 包含 {elif_count} 个elif分支，可能违反开闭原则",
                    suggestion="考虑使用策略模式或工厂模式替代大量的条件分支",
                    impact="新增功能时需要修改现有代码，增加出错风险",
                ))

        return violations

    def _check_dip(
        self,
        modules: List[ModuleInfo],
        dependencies: List[DependencyRelation],
    ) -> List[ArchitectureViolation]:
        """
        检查依赖倒置原则

        Args:
            modules: 模块列表
            dependencies: 依赖关系

        Returns:
            违规列表
        """
        violations = []

        # 检查是否存在高层模块直接依赖低层模块
        high_level_modules = {"domain", "application", "business", "core"}
        low_level_modules = {"infrastructure", "data", "external", "persistence"}

        for dep in dependencies:
            source_is_high = any(h in dep.source.lower() for h in high_level_modules)
            target_is_low = any(l in dep.target.lower() for l in low_level_modules)

            if source_is_high and target_is_low:
                violations.append(ArchitectureViolation(
                    principle=DesignPrinciple.DIP,
                    severity="high",
                    location=f"{dep.source} -> {dep.target}",
                    description=f"高层模块 {dep.source} 直接依赖低层模块 {dep.target}",
                    suggestion="引入抽象接口，让高层模块依赖抽象而非具体实现",
                    impact="增加模块间耦合，降低系统的灵活性和可测试性",
                ))

        return violations

    def _check_dry(
        self,
        code_files: Dict[str, str],
    ) -> List[ArchitectureViolation]:
        """
        检查DRY原则

        Args:
            code_files: 代码文件

        Returns:
            违规列表
        """
        violations = []

        # 简单的代码重复检测
        # 实际应用中应该使用更复杂的算法
        file_contents = list(code_files.values())
        for i in range(len(file_contents)):
            for j in range(i + 1, len(file_contents)):
                # 检查是否有大段重复代码
                content1 = file_contents[i]
                content2 = file_contents[j]

                # 简单的相似度检测
                if len(content1) > 100 and len(content2) > 100:
                    common_lines = set(content1.splitlines()).intersection(
                        set(content2.splitlines())
                    )
                    if len(common_lines) > 10:
                        violations.append(ArchitectureViolation(
                            principle=DesignPrinciple.DRY,
                            severity="medium",
                            location=f"文件 {i+1} 和文件 {j+1}",
                            description=f"检测到 {len(common_lines)} 行重复代码",
                            suggestion="提取公共代码到共享模块或工具类",
                            impact="代码重复增加维护成本，容易导致不一致",
                        ))

        return violations

    def _calculate_architecture_metrics(
        self,
        modules: List[ModuleInfo],
        dependencies: List[DependencyRelation],
        violations: List[ArchitectureViolation],
    ) -> Dict[str, float]:
        """
        计算架构指标

        Args:
            modules: 模块列表
            dependencies: 依赖关系
            violations: 违规列表

        Returns:
            指标字典
        """
        if not modules:
            return {}

        # 计算平均内聚度
        avg_cohesion = sum(m.cohesion_score for m in modules) / len(modules)

        # 计算平均耦合度
        avg_coupling = sum(m.coupling_score for m in modules) / len(modules)

        # 计算依赖密度
        dep_density = len(dependencies) / max(len(modules), 1)

        # 计算违规严重度
        severity_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        total_severity = sum(
            severity_scores.get(v.severity, 0) for v in violations
        )

        # 计算架构健康度
        health_score = max(0, 100 - total_severity * 5)

        return {
            "module_count": len(modules),
            "dependency_count": len(dependencies),
            "violation_count": len(violations),
            "avg_cohesion": round(avg_cohesion, 3),
            "avg_coupling": round(avg_coupling, 3),
            "dependency_density": round(dep_density, 3),
            "health_score": round(health_score, 2),
            "total_severity": total_severity,
        }

    def _generate_recommendations(
        self,
        pattern: ArchitecturePattern,
        modules: List[ModuleInfo],
        violations: List[ArchitectureViolation],
        metrics: Dict[str, float],
    ) -> List[str]:
        """
        生成架构建议

        Args:
            pattern: 检测到的架构模式
            modules: 模块列表
            violations: 违规列表
            metrics: 指标

        Returns:
            建议列表
        """
        recommendations = []

        # 基于架构模式的建议
        if pattern == ArchitecturePattern.UNKNOWN:
            recommendations.append(
                "建议采用明确的架构模式（如MVC、整洁架构等），以提高代码的可维护性"
            )

        # 基于指标的建议
        if metrics.get("avg_coupling", 0) > 0.7:
            recommendations.append(
                "模块间耦合度过高，建议通过依赖注入、事件驱动等方式降低耦合"
            )

        if metrics.get("avg_cohesion", 0) < 0.3:
            recommendations.append(
                "模块内聚度过低，建议将相关功能聚合到同一模块中"
            )

        # 基于违规的建议
        high_severity_violations = [
            v for v in violations if v.severity in ["high", "critical"]
        ]
        if high_severity_violations:
            recommendations.append(
                f"存在 {len(high_severity_violations)} 个高严重度违规，建议优先修复"
            )

        # 通用建议
        if not recommendations:
            recommendations.append(
                "架构整体良好，建议持续监控和优化"
            )

        return recommendations

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
        if query_type == "assess":
            project_structure = data.get("project_structure", {})
            code_files = data.get("code_files", {})
            dependencies = data.get("dependencies", {})
            result = await self.assess_architecture(
                project_structure, code_files, dependencies
            )
            return result.to_dict()
        elif query_type == "capabilities":
            return [cap.value for cap in self.capabilities]
        else:
            raise ValueError(f"不支持的查询类型: {query_type}")
