"""
测试生成Agent - 自动生成单元测试

本模块实现：
- 测试用例生成
- 测试覆盖率分析
- 测试代码生成
- 测试策略建议
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.agent import AgentCapability, AgentConfig, BaseAgent
from ..core.exceptions import TestGenerationError
from ..core.message import Message, MessageType
from ..core.task import Task, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class TestType(str, Enum):
    """测试类型"""

    UNIT = "unit"  # 单元测试
    INTEGRATION = "integration"  # 集成测试
    FUNCTIONAL = "functional"  # 功能测试
    EDGE_CASE = "edge_case"  # 边界测试
    ERROR_HANDLING = "error_handling"  # 错误处理测试
    PERFORMANCE = "performance"  # 性能测试


class TestFramework(str, Enum):
    """测试框架"""

    PYTEST = "pytest"
    UNITTEST = "unittest"
    MOCK = "mock"
    PYTEST_MOCK = "pytest-mock"


@dataclass
class TestCase:
    """测试用例"""

    name: str
    test_type: TestType
    target_function: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Any
    assertions: List[str]
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: int = 1  # 1-5, 1为最高


@dataclass
class TestSuite:
    """测试套件"""

    name: str
    target_module: str
    test_cases: List[TestCase]
    framework: TestFramework
    imports: List[str]
    fixtures: List[str]
    coverage_target: float  # 目标覆盖率
    generation_time: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "target_module": self.target_module,
            "test_cases": [
                {
                    "name": tc.name,
                    "test_type": tc.test_type.value,
                    "target_function": tc.target_function,
                    "description": tc.description,
                    "input_data": tc.input_data,
                    "expected_output": tc.expected_output,
                    "assertions": tc.assertions,
                    "tags": tc.tags,
                    "priority": tc.priority,
                }
                for tc in self.test_cases
            ],
            "framework": self.framework.value,
            "imports": self.imports,
            "fixtures": self.fixtures,
            "coverage_target": self.coverage_target,
            "generation_time": self.generation_time,
        }

    def generate_code(self) -> str:
        """
        生成测试代码

        Returns:
            测试代码字符串
        """
        lines = []

        # 添加导入
        lines.append("# 自动生成的测试代码")
        lines.append(f"# 生成时间: {self.timestamp.isoformat()}")
        lines.append("")
        for imp in self.imports:
            lines.append(f"import {imp}")
        lines.append("")
        lines.append("")

        # 添加fixtures
        if self.fixtures:
            lines.append("# Fixtures")
            for fixture in self.fixtures:
                lines.append(fixture)
            lines.append("")

        # 按目标函数分组
        grouped_cases = {}
        for tc in self.test_cases:
            if tc.target_function not in grouped_cases:
                grouped_cases[tc.target_function] = []
            grouped_cases[tc.target_function].append(tc)

        # 生成测试类
        for func_name, cases in grouped_cases.items():
            class_name = f"Test{func_name.capitalize()}"
            lines.append(f"class {class_name}:")
            lines.append(f'    """测试 {func_name} 函数"""')
            lines.append("")

            for tc in cases:
                # 生成测试方法
                lines.append(f"    def {tc.name}(self):")
                lines.append(f'        """')
                lines.append(f"        {tc.description}")
                lines.append(f'        """')

                # Setup
                if tc.setup_code:
                    lines.append(f"        # Setup")
                    lines.append(f"        {tc.setup_code}")
                    lines.append("")

                # 准备输入
                if tc.input_data:
                    lines.append(f"        # 准备输入")
                    for key, value in tc.input_data.items():
                        lines.append(f"        {key} = {repr(value)}")
                    lines.append("")

                # 执行测试
                lines.append(f"        # 执行")
                if tc.input_data:
                    args = ", ".join(tc.input_data.keys())
                    lines.append(f"        result = {tc.target_function}({args})")
                else:
                    lines.append(f"        result = {tc.target_function}()")
                lines.append("")

                # 断言
                lines.append(f"        # 断言")
                for assertion in tc.assertions:
                    lines.append(f"        {assertion}")
                lines.append("")

                # Teardown
                if tc.teardown_code:
                    lines.append(f"        # Teardown")
                    lines.append(f"        {tc.teardown_code}")
                    lines.append("")

                lines.append("")

        return "\n".join(lines)


class TestGeneratorAgent(BaseAgent):
    """
    测试生成Agent

    负责：
    - 分析函数签名和行为
    - 生成测试用例
    - 生成测试代码
    - 评估测试覆盖率
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        message_bus=None,
        task_manager=None,
    ):
        """
        初始化测试生成Agent

        Args:
            agent_id: Agent标识
            config: 配置
            message_bus: 消息总线
            task_manager: 任务管理器
        """
        super().__init__(
            agent_id=agent_id,
            name="TestGeneratorAgent",
            description="测试生成Agent，自动生成单元测试",
            capabilities={
                AgentCapability.TEST_GENERATION,
            },
            config=config,
            message_bus=message_bus,
            task_manager=task_manager,
        )

        # 测试模板库
        self._test_templates = self._init_test_templates()

        # 断言模式库
        self._assertion_patterns = self._init_assertion_patterns()

        logger.info("测试生成Agent已初始化")

    def _init_test_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化测试模板库"""
        return {
            "basic": {
                "description": "基本功能测试",
                "template": "test_{function}_basic",
            },
            "edge_case": {
                "description": "边界情况测试",
                "template": "test_{function}_edge_case",
            },
            "error": {
                "description": "错误处理测试",
                "template": "test_{function}_error",
            },
            "performance": {
                "description": "性能测试",
                "template": "test_{function}_performance",
            },
        }

    def _init_assertion_patterns(self) -> Dict[str, List[str]]:
        """初始化断言模式库"""
        return {
            "equality": [
                "assert result == expected",
                "assert result is not None",
            ],
            "type_check": [
                "assert isinstance(result, expected_type)",
            ],
            "exception": [
                "with pytest.raises(ExceptionType):",
                "    function()",
            ],
            "collection": [
                "assert len(result) == expected_length",
                "assert item in result",
            ],
            "boolean": [
                "assert result is True",
                "assert result is False",
            ],
        }

    async def execute_task(self, task: Task) -> TaskResult:
        """
        执行测试生成任务

        Args:
            task: 任务

        Returns:
            任务结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始执行测试生成任务: {task.id}")

        try:
            # 提取任务参数
            code_analysis = task.input_data.get("code_analysis", {})
            target_functions = task.input_data.get("target_functions", [])
            test_types = task.input_data.get("test_types", ["unit", "edge_case"])
            framework = task.input_data.get("framework", "pytest")

            # 生成测试套件
            suite = await self.generate_test_suite(
                code_analysis, target_functions, test_types, framework
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                success=True,
                data={
                    "test_suite": suite.to_dict(),
                    "generated_code": suite.generate_code(),
                },
                execution_time=execution_time,
                metadata={
                    "agent_id": self.agent_id,
                    "task_id": task.id,
                },
            )

        except Exception as e:
            self.logger.error(f"测试生成失败: {e}", exc_info=True)
            return TaskResult(
                success=False,
                error=str(e),
            )

    async def generate_test_suite(
        self,
        code_analysis: Dict[str, Any],
        target_functions: List[str],
        test_types: List[str],
        framework: str = "pytest",
    ) -> TestSuite:
        """
        生成测试套件

        Args:
            code_analysis: 代码分析结果
            target_functions: 目标函数列表
            test_types: 测试类型列表
            framework: 测试框架

        Returns:
            测试套件
        """
        start_time = datetime.now()

        # 解析框架
        test_framework = TestFramework(framework)

        # 生成测试用例
        test_cases = []
        for func_name in target_functions:
            # 获取函数信息
            func_info = self._get_function_info(code_analysis, func_name)
            if not func_info:
                continue

            # 生成各类测试用例
            for test_type in test_types:
                cases = await self._generate_test_cases(
                    func_name, func_info, TestType(test_type), test_framework
                )
                test_cases.extend(cases)

        # 生成导入
        imports = self._generate_imports(test_framework, code_analysis)

        # 生成fixtures
        fixtures = self._generate_fixtures(test_cases, test_framework)

        # 计算目标覆盖率
        coverage_target = self._calculate_coverage_target(test_cases, target_functions)

        execution_time = (datetime.now() - start_time).total_seconds()

        return TestSuite(
            name=f"TestSuite_{code_analysis.get('file_path', 'unknown')}",
            target_module=code_analysis.get("file_path", ""),
            test_cases=test_cases,
            framework=test_framework,
            imports=imports,
            fixtures=fixtures,
            coverage_target=coverage_target,
            generation_time=execution_time,
        )

    def _get_function_info(
        self,
        code_analysis: Dict[str, Any],
        func_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        获取函数信息

        Args:
            code_analysis: 代码分析结果
            func_name: 函数名

        Returns:
            函数信息或None
        """
        functions = code_analysis.get("functions", [])
        for func in functions:
            if func.get("name") == func_name:
                return func

        # 检查类方法
        classes = code_analysis.get("classes", [])
        for cls in classes:
            for method in cls.get("methods", []):
                if method.get("name") == func_name:
                    return method

        return None

    async def _generate_test_cases(
        self,
        func_name: str,
        func_info: Dict[str, Any],
        test_type: TestType,
        framework: TestFramework,
    ) -> List[TestCase]:
        """
        生成测试用例

        Args:
            func_name: 函数名
            func_info: 函数信息
            test_type: 测试类型
            framework: 测试框架

        Returns:
            测试用例列表
        """
        cases = []

        if test_type == TestType.UNIT:
            cases.extend(self._generate_unit_tests(func_name, func_info, framework))
        elif test_type == TestType.EDGE_CASE:
            cases.extend(self._generate_edge_case_tests(func_name, func_info, framework))
        elif test_type == TestType.ERROR_HANDLING:
            cases.extend(self._generate_error_tests(func_name, func_info, framework))
        elif test_type == TestType.PERFORMANCE:
            cases.extend(self._generate_performance_tests(func_name, func_info, framework))

        return cases

    def _generate_unit_tests(
        self,
        func_name: str,
        func_info: Dict[str, Any],
        framework: TestFramework,
    ) -> List[TestCase]:
        """
        生成单元测试

        Args:
            func_name: 函数名
            func_info: 函数信息
            framework: 测试框架

        Returns:
            测试用例列表
        """
        cases = []
        params = func_info.get("params", [])

        # 基本功能测试
        test_name = f"test_{func_name}_basic"
        input_data = self._generate_sample_input(params)
        assertions = self._generate_assertions(func_info, "success")

        cases.append(TestCase(
            name=test_name,
            test_type=TestType.UNIT,
            target_function=func_name,
            description=f"测试 {func_name} 的基本功能",
            input_data=input_data,
            expected_output="根据函数逻辑确定",
            assertions=assertions,
            tags=["basic", "unit"],
            priority=1,
        ))

        # 正常输入测试
        test_name = f"test_{func_name}_normal"
        input_data = self._generate_normal_input(params)
        assertions = self._generate_assertions(func_info, "success")

        cases.append(TestCase(
            name=test_name,
            test_type=TestType.UNIT,
            target_function=func_name,
            description=f"测试 {func_name} 的正常输入",
            input_data=input_data,
            expected_output="根据函数逻辑确定",
            assertions=assertions,
            tags=["normal", "unit"],
            priority=2,
        ))

        return cases

    def _generate_edge_case_tests(
        self,
        func_name: str,
        func_info: Dict[str, Any],
        framework: TestFramework,
    ) -> List[TestCase]:
        """
        生成边界测试

        Args:
            func_name: 函数名
            func_info: 函数信息
            framework: 测试框架

        Returns:
            测试用例列表
        """
        cases = []
        params = func_info.get("params", [])

        # 空值测试
        test_name = f"test_{func_name}_empty"
        input_data = {param: None for param in params}
        assertions = self._generate_assertions(func_info, "edge_case")

        cases.append(TestCase(
            name=test_name,
            test_type=TestType.EDGE_CASE,
            target_function=func_name,
            description=f"测试 {func_name} 的空值处理",
            input_data=input_data,
            expected_output="应返回None或抛出异常",
            assertions=assertions,
            tags=["edge_case", "null"],
            priority=2,
        ))

        # 边界值测试
        test_name = f"test_{func_name}_boundary"
        input_data = self._generate_boundary_input(params)
        assertions = self._generate_assertions(func_info, "edge_case")

        cases.append(TestCase(
            name=test_name,
            test_type=TestType.EDGE_CASE,
            target_function=func_name,
            description=f"测试 {func_name} 的边界值",
            input_data=input_data,
            expected_output="根据边界条件确定",
            assertions=assertions,
            tags=["edge_case", "boundary"],
            priority=2,
        ))

        return cases

    def _generate_error_tests(
        self,
        func_name: str,
        func_info: Dict[str, Any],
        framework: TestFramework,
    ) -> List[TestCase]:
        """
        生成错误处理测试

        Args:
            func_name: 函数名
            func_info: 函数信息
            framework: 测试框架

        Returns:
            测试用例列表
        """
        cases = []
        params = func_info.get("params", [])

        # 无效输入测试
        test_name = f"test_{func_name}_invalid_input"
        input_data = self._generate_invalid_input(params)
        assertions = self._generate_assertions(func_info, "error")

        cases.append(TestCase(
            name=test_name,
            test_type=TestType.ERROR_HANDLING,
            target_function=func_name,
            description=f"测试 {func_name} 的无效输入处理",
            input_data=input_data,
            expected_output="应抛出适当的异常",
            assertions=assertions,
            tags=["error", "invalid_input"],
            priority=2,
        ))

        return cases

    def _generate_performance_tests(
        self,
        func_name: str,
        func_info: Dict[str, Any],
        framework: TestFramework,
    ) -> List[TestCase]:
        """
        生成性能测试

        Args:
            func_name: 函数名
            func_info: 函数信息
            framework: 测试框架

        Returns:
            测试用例列表
        """
        cases = []

        test_name = f"test_{func_name}_performance"
        input_data = {"iterations": 1000}
        assertions = [
            "assert execution_time < 1.0, f'执行时间过长: {execution_time}秒'",
        ]

        cases.append(TestCase(
            name=test_name,
            test_type=TestType.PERFORMANCE,
            target_function=func_name,
            description=f"测试 {func_name} 的性能",
            input_data=input_data,
            expected_output="执行时间应在可接受范围内",
            assertions=assertions,
            setup_code="import time",
            tags=["performance"],
            priority=3,
        ))

        return cases

    def _generate_sample_input(self, params: List[str]) -> Dict[str, Any]:
        """
        生成示例输入

        Args:
            params: 参数列表

        Returns:
            输入数据字典
        """
        input_data = {}
        for param in params:
            # 根据参数名猜测类型
            if "name" in param.lower() or "str" in param.lower():
                input_data[param] = "test_value"
            elif "count" in param.lower() or "num" in param.lower() or "int" in param.lower():
                input_data[param] = 42
            elif "list" in param.lower() or "items" in param.lower():
                input_data[param] = [1, 2, 3]
            elif "dict" in param.lower() or "data" in param.lower():
                input_data[param] = {"key": "value"}
            elif "flag" in param.lower() or "bool" in param.lower():
                input_data[param] = True
            else:
                input_data[param] = "test"
        return input_data

    def _generate_normal_input(self, params: List[str]) -> Dict[str, Any]:
        """
        生成正常输入

        Args:
            params: 参数列表

        Returns:
            输入数据字典
        """
        return self._generate_sample_input(params)

    def _generate_boundary_input(self, params: List[str]) -> Dict[str, Any]:
        """
        生成边界输入

        Args:
            params: 参数列表

        Returns:
            输入数据字典
        """
        input_data = {}
        for param in params:
            if "name" in param.lower() or "str" in param.lower():
                input_data[param] = ""
            elif "count" in param.lower() or "num" in param.lower():
                input_data[param] = 0
            elif "list" in param.lower():
                input_data[param] = []
            else:
                input_data[param] = None
        return input_data

    def _generate_invalid_input(self, params: List[str]) -> Dict[str, Any]:
        """
        生成无效输入

        Args:
            params: 参数列表

        Returns:
            输入数据字典
        """
        input_data = {}
        for param in params:
            input_data[param] = None  # None通常是无效输入
        return input_data

    def _generate_assertions(
        self,
        func_info: Dict[str, Any],
        test_scenario: str,
    ) -> List[str]:
        """
        生成断言

        Args:
            func_info: 函数信息
            test_scenario: 测试场景

        Returns:
            断言列表
        """
        assertions = []

        if test_scenario == "success":
            assertions.append("assert result is not None")
            return_type = func_info.get("return_type")
            if return_type:
                assertions.append(f"assert isinstance(result, {return_type})")
        elif test_scenario == "edge_case":
            assertions.append("# 边界情况可能返回None或抛出异常")
        elif test_scenario == "error":
            assertions.append("with pytest.raises(Exception):")
            assertions.append(f"    {func_info.get('name', 'function')}(**invalid_input)")

        return assertions

    def _generate_imports(
        self,
        framework: TestFramework,
        code_analysis: Dict[str, Any],
    ) -> List[str]:
        """
        生成导入语句

        Args:
            framework: 测试框架
            code_analysis: 代码分析结果

        Returns:
            导入列表
        """
        imports = []

        if framework == TestFramework.PYTEST:
            imports.append("import pytest")
        elif framework == TestFramework.UNITTEST:
            imports.append("import unittest")

        imports.append("from unittest.mock import MagicMock, patch")

        # 添加被测模块
        file_path = code_analysis.get("file_path", "")
        if file_path:
            module_name = file_path.replace("/", ".").replace(".py", "")
            imports.append(f"from {module_name} import *")

        return imports

    def _generate_fixtures(
        self,
        test_cases: List[TestCase],
        framework: TestFramework,
    ) -> List[str]:
        """
        生成fixtures

        Args:
            test_cases: 测试用例列表
            framework: 测试框架

        Returns:
            fixtures列表
        """
        fixtures = []

        if framework == TestFramework.PYTEST:
            # 收集需要的fixtures
            needed_fixtures = set()
            for tc in test_cases:
                for key in tc.input_data.keys():
                    if "db" in key.lower() or "database" in key.lower():
                        needed_fixtures.add("database")
                    elif "client" in key.lower():
                        needed_fixtures.add("client")
                    elif "file" in key.lower():
                        needed_fixtures.add("temp_file")

            # 生成fixtures
            if "database" in needed_fixtures:
                fixtures.append("""@pytest.fixture
def database():
    \"\"\"数据库fixture\"\"\"
    db = create_test_database()
    yield db
    db.cleanup()""")

            if "client" in needed_fixtures:
                fixtures.append("""@pytest.fixture
def client():
    \"\"\"客户端fixture\"\"\"
    return TestClient(app)""")

            if "temp_file" in needed_fixtures:
                fixtures.append("""@pytest.fixture
def temp_file():
    \"\"\"临时文件fixture\"\"\"
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        yield f.name
    import os
    os.unlink(f.name)""")

        return fixtures

    def _calculate_coverage_target(
        self,
        test_cases: List[TestCase],
        target_functions: List[str],
    ) -> float:
        """
        计算目标覆盖率

        Args:
            test_cases: 测试用例列表
            target_functions: 目标函数列表

        Returns:
            目标覆盖率百分比
        """
        if not target_functions:
            return 0.0

        # 计算每个函数的测试数量
        func_test_count = {}
        for tc in test_cases:
            func = tc.target_function
            func_test_count[func] = func_test_count.get(func, 0) + 1

        # 计算覆盖率
        covered_functions = len(func_test_count)
        coverage = covered_functions / len(target_functions) * 100

        # 根据测试数量调整
        avg_tests = sum(func_test_count.values()) / max(covered_functions, 1)
        if avg_tests >= 3:
            coverage = min(coverage * 1.1, 100)

        return round(coverage, 2)

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
        if query_type == "generate":
            code_analysis = data.get("code_analysis", {})
            target_functions = data.get("target_functions", [])
            test_types = data.get("test_types", ["unit", "edge_case"])
            framework = data.get("framework", "pytest")
            suite = await self.generate_test_suite(
                code_analysis, target_functions, test_types, framework
            )
            return {
                "test_suite": suite.to_dict(),
                "generated_code": suite.generate_code(),
            }
        elif query_type == "capabilities":
            return [cap.value for cap in self.capabilities]
        else:
            raise ValueError(f"不支持的查询类型: {query_type}")
