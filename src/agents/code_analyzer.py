"""
代码分析Agent - 负责解析代码结构、识别技术债

本模块实现：
- 代码结构解析
- 复杂度分析
- 技术债识别
- 代码质量评估
"""

import ast
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path

from ..core.agent import AgentCapability, AgentConfig, BaseAgent
from ..core.exceptions import AnalysisError, CodeParsingError
from ..core.message import Message, MessageType
from ..core.task import Task, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class CodeMetric(str, Enum):
    """代码度量指标"""

    LOC = "lines_of_code"  # 代码行数
    COMPLEXITY = "cyclomatic_complexity"  # 圈复杂度
    COGNITIVE_COMPLEXITY = "cognitive_complexity"  # 认知复杂度
    MAINTAINABILITY = "maintainability_index"  # 可维护性指数
    DUPLICATION = "code_duplication"  # 代码重复率
    TEST_COVERAGE = "test_coverage"  # 测试覆盖率


class TechDebtType(str, Enum):
    """技术债类型"""

    CODE_SMELL = "code_smell"  # 代码异味
    COMPLEXITY = "complexity"  # 复杂度过高
    DUPLICATION = "duplication"  # 代码重复
    DEAD_CODE = "dead_code"  # 死代码
    LONG_METHOD = "long_method"  # 方法过长
    LARGE_CLASS = "large_class"  # 类过大
    FEATURE_ENVY = "feature_envy"  # 功能依恋
    DATA_CLUMP = "data_clump"  # 数据泥团
    PRIMITIVE_OBSESSION = "primitive_obsession"  # 基本类型偏执
    SWITCH_STATEMENT = "switch_statement"  # 过多的switch语句


@dataclass
class CodeLocation:
    """代码位置"""

    file_path: str
    start_line: int
    end_line: int
    column: int = 0


@dataclass
class TechDebt:
    """技术债务"""

    debt_type: TechDebtType
    severity: str  # low, medium, high, critical
    location: CodeLocation
    description: str
    suggestion: str
    effort_hours: float = 0.0


@dataclass
class FunctionInfo:
    """函数信息"""

    name: str
    start_line: int
    end_line: int
    params: List[str]
    return_type: Optional[str]
    complexity: int
    docstring: Optional[str]
    is_method: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """类信息"""

    name: str
    start_line: int
    end_line: int
    methods: List[FunctionInfo]
    attributes: List[str]
    base_classes: List[str]
    docstring: Optional[str]
    decorators: List[str] = field(default_factory=list)


@dataclass
class CodeAnalysisResult:
    """代码分析结果"""

    file_path: str
    language: str
    loc: int
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[str]
    complexity: Dict[str, int]
    tech_debts: List[TechDebt]
    metrics: Dict[str, float]
    analysis_time: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "loc": self.loc,
            "functions": [
                {
                    "name": f.name,
                    "start_line": f.start_line,
                    "end_line": f.end_line,
                    "params": f.params,
                    "complexity": f.complexity,
                }
                for f in self.functions
            ],
            "classes": [
                {
                    "name": c.name,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "methods_count": len(c.methods),
                    "attributes": c.attributes,
                }
                for c in self.classes
            ],
            "imports": self.imports,
            "complexity": self.complexity,
            "tech_debts": [
                {
                    "type": d.debt_type.value,
                    "severity": d.severity,
                    "location": {
                        "file": d.location.file_path,
                        "start_line": d.location.start_line,
                        "end_line": d.location.end_line,
                    },
                    "description": d.description,
                    "suggestion": d.suggestion,
                }
                for d in self.tech_debts
            ],
            "metrics": self.metrics,
            "analysis_time": self.analysis_time,
        }


class PythonCodeParser:
    """Python代码解析器"""

    def __init__(self):
        """初始化解析器"""
        self._tree = None
        self._source = ""

    def parse(self, source: str, file_path: str = "<string>") -> ast.AST:
        """
        解析Python源代码

        Args:
            source: 源代码
            file_path: 文件路径

        Returns:
            AST树

        Raises:
            CodeParsingError: 解析失败
        """
        self._source = source
        try:
            self._tree = ast.parse(source, filename=file_path)
            return self._tree
        except SyntaxError as e:
            raise CodeParsingError(
                f"语法错误: {e}",
                file_path=file_path,
                details={"line": e.lineno, "offset": e.offset},
            )

    def get_functions(self) -> List[FunctionInfo]:
        """
        获取所有函数信息

        Returns:
            函数信息列表
        """
        if not self._tree:
            return []

        functions = []
        for node in ast.walk(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = FunctionInfo(
                    name=node.name,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    params=self._get_params(node),
                    return_type=self._get_return_type(node),
                    complexity=self._calculate_complexity(node),
                    docstring=ast.get_docstring(node),
                    is_method=self._is_method(node),
                    decorators=[self._get_decorator_name(d) for d in node.decorator_list],
                )
                functions.append(func_info)

        return functions

    def get_classes(self) -> List[ClassInfo]:
        """
        获取所有类信息

        Returns:
            类信息列表
        """
        if not self._tree:
            return []

        classes = []
        for node in ast.walk(self._tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                attributes = []

                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(FunctionInfo(
                            name=item.name,
                            start_line=item.lineno,
                            end_line=item.end_lineno or item.lineno,
                            params=self._get_params(item),
                            return_type=self._get_return_type(item),
                            complexity=self._calculate_complexity(item),
                            docstring=ast.get_docstring(item),
                            is_method=True,
                        ))
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attributes.append(target.id)

                class_info = ClassInfo(
                    name=node.name,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    methods=methods,
                    attributes=attributes,
                    base_classes=self._get_base_classes(node),
                    docstring=ast.get_docstring(node),
                    decorators=[self._get_decorator_name(d) for d in node.decorator_list],
                )
                classes.append(class_info)

        return classes

    def get_imports(self) -> List[str]:
        """
        获取所有导入

        Returns:
            导入列表
        """
        if not self._tree:
            return []

        imports = []
        for node in ast.walk(self._tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name if not alias.asname else f"{alias.name} as {alias.asname}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)

        return imports

    def _get_params(self, node: ast.FunctionDef) -> List[str]:
        """获取函数参数"""
        params = []
        for arg in node.args.args:
            if arg.arg != "self" and arg.arg != "cls":
                params.append(arg.arg)
        return params

    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """获取返回类型"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None

    def _is_method(self, node: ast.FunctionDef) -> bool:
        """判断是否为方法"""
        for parent in ast.walk(self._tree):
            if isinstance(parent, ast.ClassDef):
                if node in ast.walk(parent):
                    return True
        return False

    def _get_base_classes(self, node: ast.ClassDef) -> List[str]:
        """获取基类"""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{ast.dump(base)}")
        return bases

    def _get_decorator_name(self, node: ast.expr) -> str:
        """获取装饰器名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{ast.dump(node)}"
        return str(node)

    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        计算圈复杂度

        Args:
            node: AST节点

        Returns:
            圈复杂度
        """
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity

    def get_loc(self) -> int:
        """获取代码行数"""
        return len(self._source.splitlines())


class CodeAnalyzerAgent(BaseAgent):
    """
    代码分析Agent

    负责：
    - 解析代码结构
    - 计算代码度量
    - 识别技术债务
    - 评估代码质量
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        message_bus=None,
        task_manager=None,
    ):
        """
        初始化代码分析Agent

        Args:
            agent_id: Agent标识
            config: 配置
            message_bus: 消息总线
            task_manager: 任务管理器
        """
        super().__init__(
            agent_id=agent_id,
            name="CodeAnalyzerAgent",
            description="代码分析Agent，负责解析代码结构、识别技术债",
            capabilities={
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.CODE_PARSING,
                AgentCapability.COMPLEXITY_ANALYSIS,
            },
            config=config,
            message_bus=message_bus,
            task_manager=task_manager,
        )

        # 初始化解析器
        self._parsers = {
            "python": PythonCodeParser(),
        }

        # 技术债检测规则
        self._debt_rules = self._init_debt_rules()

        logger.info("代码分析Agent已初始化")

    def _init_debt_rules(self) -> Dict[TechDebtType, Dict[str, Any]]:
        """初始化技术债检测规则"""
        return {
            TechDebtType.LONG_METHOD: {
                "threshold": 50,
                "severity": "medium",
                "description": "方法过长，建议拆分",
            },
            TechDebtType.COMPLEXITY: {
                "threshold": 10,
                "severity": "high",
                "description": "圈复杂度过高，建议重构",
            },
            TechDebtType.LARGE_CLASS: {
                "threshold": 200,
                "severity": "medium",
                "description": "类过大，建议拆分",
            },
        }

    async def execute_task(self, task: Task) -> TaskResult:
        """
        执行分析任务

        Args:
            task: 任务

        Returns:
            任务结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始执行代码分析任务: {task.id}")

        try:
            # 提取任务参数
            source_code = task.input_data.get("source_code", "")
            file_path = task.input_data.get("file_path", "<string>")
            language = task.input_data.get("language", "python")

            if not source_code:
                return TaskResult(
                    success=False,
                    error="缺少源代码",
                )

            # 执行分析
            result = await self.analyze_code(source_code, file_path, language)

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
            self.logger.error(f"代码分析失败: {e}", exc_info=True)
            return TaskResult(
                success=False,
                error=str(e),
            )

    async def analyze_code(
        self,
        source_code: str,
        file_path: str = "<string>",
        language: str = "python",
    ) -> CodeAnalysisResult:
        """
        分析代码

        Args:
            source_code: 源代码
            file_path: 文件路径
            language: 编程语言

        Returns:
            分析结果

        Raises:
            AnalysisError: 分析失败
        """
        start_time = datetime.now()

        # 获取解析器
        parser = self._parsers.get(language)
        if not parser:
            raise AnalysisError(f"不支持的语言: {language}")

        try:
            # 解析代码
            tree = parser.parse(source_code, file_path)

            # 获取代码结构
            functions = parser.get_functions()
            classes = parser.get_classes()
            imports = parser.get_imports()
            loc = parser.get_loc()

            # 计算复杂度
            complexity = self._calculate_file_complexity(functions, classes)

            # 检测技术债务
            tech_debts = await self._detect_tech_debts(
                source_code, file_path, functions, classes
            )

            # 计算度量指标
            metrics = self._calculate_metrics(
                loc, functions, classes, complexity, tech_debts
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return CodeAnalysisResult(
                file_path=file_path,
                language=language,
                loc=loc,
                functions=functions,
                classes=classes,
                imports=imports,
                complexity=complexity,
                tech_debts=tech_debts,
                metrics=metrics,
                analysis_time=execution_time,
            )

        except CodeParsingError:
            raise
        except Exception as e:
            raise AnalysisError(
                f"分析代码时发生错误: {e}",
                file_path=file_path,
            )

    def _calculate_file_complexity(
        self,
        functions: List[FunctionInfo],
        classes: List[ClassInfo],
    ) -> Dict[str, int]:
        """
        计算文件复杂度

        Args:
            functions: 函数列表
            classes: 类列表

        Returns:
            复杂度字典
        """
        total_complexity = 0
        max_complexity = 0
        function_complexities = {}

        for func in functions:
            function_complexities[func.name] = func.complexity
            total_complexity += func.complexity
            max_complexity = max(max_complexity, func.complexity)

        for cls in classes:
            for method in cls.methods:
                function_complexities[f"{cls.name}.{method.name}"] = method.complexity
                total_complexity += method.complexity
                max_complexity = max(max_complexity, method.complexity)

        return {
            "total": total_complexity,
            "average": total_complexity / max(len(functions), 1),
            "max": max_complexity,
            "functions": function_complexities,
        }

    async def _detect_tech_debts(
        self,
        source_code: str,
        file_path: str,
        functions: List[FunctionInfo],
        classes: List[ClassInfo],
    ) -> List[TechDebt]:
        """
        检测技术债务

        Args:
            source_code: 源代码
            file_path: 文件路径
            functions: 函数列表
            classes: 类列表

        Returns:
            技术债务列表
        """
        debts = []

        # 检测长方法
        for func in functions:
            method_length = func.end_line - func.start_line + 1
            rule = self._debt_rules[TechDebtType.LONG_METHOD]
            if method_length > rule["threshold"]:
                debts.append(TechDebt(
                    debt_type=TechDebtType.LONG_METHOD,
                    severity=rule["severity"],
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=func.start_line,
                        end_line=func.end_line,
                    ),
                    description=f"方法 {func.name} 有 {method_length} 行，超过阈值 {rule['threshold']}",
                    suggestion=f"建议将方法 {func.name} 拆分为更小的函数",
                    effort_hours=method_length / 50,
                ))

        # 检测高复杂度
        for func in functions:
            rule = self._debt_rules[TechDebtType.COMPLEXITY]
            if func.complexity > rule["threshold"]:
                debts.append(TechDebt(
                    debt_type=TechDebtType.COMPLEXITY,
                    severity=rule["severity"],
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=func.start_line,
                        end_line=func.end_line,
                    ),
                    description=f"方法 {func.name} 的圈复杂度为 {func.complexity}，超过阈值 {rule['threshold']}",
                    suggestion=f"建议重构方法 {func.name} 以降低复杂度",
                    effort_hours=func.complexity / 5,
                ))

        # 检测大类
        for cls in classes:
            class_length = cls.end_line - cls.start_line + 1
            rule = self._debt_rules[TechDebtType.LARGE_CLASS]
            if class_length > rule["threshold"]:
                debts.append(TechDebt(
                    debt_type=TechDebtType.LARGE_CLASS,
                    severity=rule["severity"],
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=cls.start_line,
                        end_line=cls.end_line,
                    ),
                    description=f"类 {cls.name} 有 {class_length} 行，超过阈值 {rule['threshold']}",
                    suggestion=f"建议将类 {cls.name} 拆分为更小的类",
                    effort_hours=class_length / 100,
                ))

        # 检测死代码（未使用的导入）
        unused_imports = self._detect_unused_imports(source_code, functions, classes)
        for import_name in unused_imports:
            debts.append(TechDebt(
                debt_type=TechDebtType.DEAD_CODE,
                severity="low",
                location=CodeLocation(
                    file_path=file_path,
                    start_line=1,
                    end_line=1,
                ),
                description=f"导入 {import_name} 可能未被使用",
                suggestion=f"建议移除未使用的导入: {import_name}",
                effort_hours=0.1,
            ))

        return debts

    def _detect_unused_imports(
        self,
        source_code: str,
        functions: List[FunctionInfo],
        classes: List[ClassInfo],
    ) -> List[str]:
        """
        检测未使用的导入

        Args:
            source_code: 源代码
            functions: 函数列表
            classes: 类列表

        Returns:
            未使用的导入列表
        """
        # 简单实现：检查导入的名称是否在代码中出现
        unused = []
        parser = self._parsers.get("python")
        if not parser:
            return unused

        imports = parser.get_imports()
        for imp in imports:
            # 提取导入的名称
            parts = imp.split(".")
            name = parts[-1] if parts else imp
            if name == "*":
                continue

            # 检查是否在代码中使用
            if name not in source_code:
                unused.append(imp)

        return unused

    def _calculate_metrics(
        self,
        loc: int,
        functions: List[FunctionInfo],
        classes: List[ClassInfo],
        complexity: Dict[str, int],
        tech_debts: List[TechDebt],
    ) -> Dict[str, float]:
        """
        计算代码度量指标

        Args:
            loc: 代码行数
            functions: 函数列表
            classes: 类列表
            complexity: 复杂度
            tech_debts: 技术债务

        Returns:
            度量指标字典
        """
        # 计算可维护性指数
        # 公式: MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC) + 50 * sin(sqrt(2.4 * C))
        import math

        v = loc * 0.1  # 简化的体积估算
        g = complexity.get("average", 1)
        c = len(tech_debts)

        mi = max(0, min(100, 171 - 5.2 * math.log(max(v, 1)) - 0.23 * g - 16.2 * math.log(max(loc, 1)) + 50 * math.sin(math.sqrt(2.4 * c))))

        # 计算代码密度
        function_count = len(functions)
        class_count = len(classes)
        avg_function_size = loc / max(function_count, 1)

        return {
            "maintainability_index": round(mi, 2),
            "function_count": function_count,
            "class_count": class_count,
            "avg_function_size": round(avg_function_size, 2),
            "complexity_score": complexity.get("total", 0),
            "tech_debt_score": sum(
                {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(d.severity, 0)
                for d in tech_debts
            ),
        }

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
        if query_type == "analyze":
            source_code = data.get("source_code", "")
            file_path = data.get("file_path", "<string>")
            result = await self.analyze_code(source_code, file_path)
            return result.to_dict()
        elif query_type == "capabilities":
            return [cap.value for cap in self.capabilities]
        else:
            raise ValueError(f"不支持的查询类型: {query_type}")
