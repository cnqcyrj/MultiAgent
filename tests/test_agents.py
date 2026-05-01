"""
Agent测试
"""

import asyncio
import pytest
from datetime import datetime

from src.agents.code_analyzer import CodeAnalyzerAgent
from src.agents.architecture import ArchitectureAgent
from src.agents.optimization import OptimizationAgent
from src.agents.test_generator import TestGeneratorAgent
from src.agents.orchestrator import OrchestratorAgent
from src.core.task import Task, TaskResult, TaskStatus


# 测试用的Python代码
SAMPLE_PYTHON_CODE = '''
def calculate_sum(numbers):
    """计算数字列表的和"""
    total = 0
    for num in numbers:
        total += num
    return total

def factorial(n):
    """计算阶乘"""
    if n < 0:
        raise ValueError("负数没有阶乘")
    if n <= 1:
        return 1
    return n * factorial(n - 1)

class Calculator:
    """计算器类"""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        """加法"""
        result = a + b
        self.history.append((a, b, '+', result))
        return result

    def subtract(self, a, b):
        """减法"""
        result = a - b
        self.history.append((a, b, '-', result))
        return result
'''


class TestCodeAnalyzerAgent:
    """代码分析Agent测试"""

    @pytest.mark.asyncio
    async def test_analyze_code(self):
        """测试代码分析"""
        agent = CodeAnalyzerAgent()

        result = await agent.analyze_code(
            SAMPLE_PYTHON_CODE,
            "test.py",
            "python"
        )

        assert result is not None
        assert result.file_path == "test.py"
        assert result.language == "python"
        assert result.loc > 0
        assert len(result.functions) > 0
        assert len(result.classes) > 0

    @pytest.mark.asyncio
    async def test_analyze_functions(self):
        """测试函数分析"""
        agent = CodeAnalyzerAgent()

        result = await agent.analyze_code(SAMPLE_PYTHON_CODE, "test.py")

        # 检查函数
        func_names = [f.name for f in result.functions]
        assert "calculate_sum" in func_names
        assert "factorial" in func_names

        # 检查函数参数
        for func in result.functions:
            if func.name == "calculate_sum":
                assert "numbers" in func.params
            elif func.name == "factorial":
                assert "n" in func.params

    @pytest.mark.asyncio
    async def test_analyze_classes(self):
        """测试类分析"""
        agent = CodeAnalyzerAgent()

        result = await agent.analyze_code(SAMPLE_PYTHON_CODE, "test.py")

        # 检查类
        class_names = [c.name for c in result.classes]
        assert "Calculator" in class_names

        # 检查方法
        calculator = next(c for c in result.classes if c.name == "Calculator")
        method_names = [m.name for m in calculator.methods]
        assert "add" in method_names
        assert "subtract" in method_names

    @pytest.mark.asyncio
    async def test_calculate_complexity(self):
        """测试复杂度计算"""
        agent = CodeAnalyzerAgent()

        result = await agent.analyze_code(SAMPLE_PYTHON_CODE, "test.py")

        assert "total" in result.complexity
        assert "average" in result.complexity
        assert "max" in result.complexity

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """测试执行任务"""
        agent = CodeAnalyzerAgent()

        task = Task(
            name="代码分析任务",
            input_data={
                "source_code": SAMPLE_PYTHON_CODE,
                "file_path": "test.py",
                "language": "python",
            },
        )

        result = await agent.execute_task(task)

        assert result.success is True
        assert result.data is not None
        assert "functions" in result.data
        assert "classes" in result.data


class TestArchitectureAgent:
    """架构评估Agent测试"""

    @pytest.mark.asyncio
    async def test_assess_architecture(self):
        """测试架构评估"""
        agent = ArchitectureAgent()

        project_structure = {
            "directories": ["models", "views", "controllers"],
            "modules": [
                {"name": "models", "path": "models"},
                {"name": "views", "path": "views"},
            ],
        }

        code_files = {
            "test.py": SAMPLE_PYTHON_CODE,
        }

        dependencies = {
            "models": ["views"],
        }

        result = await agent.assess_architecture(
            project_structure, code_files, dependencies
        )

        assert result is not None
        assert result.detected_pattern is not None
        assert len(result.modules) >= 0

    @pytest.mark.asyncio
    async def test_detect_pattern(self):
        """测试模式检测"""
        agent = ArchitectureAgent()

        # MVC模式
        mvc_structure = {
            "directories": ["models", "views", "controllers"],
        }

        pattern = agent._detect_pattern(mvc_structure, {})
        assert pattern.value == "mvc"

    @pytest.mark.asyncio
    async def test_check_design_principles(self):
        """测试设计原则检查"""
        agent = ArchitectureAgent()

        modules = []
        dependencies = []
        code_files = {"test.py": SAMPLE_PYTHON_CODE}

        violations = await agent._check_design_principles(
            modules, dependencies, code_files
        )

        assert isinstance(violations, list)


class TestOptimizationAgent:
    """优化建议Agent测试"""

    @pytest.mark.asyncio
    async def test_generate_optimization_plan(self):
        """测试生成优化计划"""
        agent = OptimizationAgent()

        code_analysis = {
            "functions": [
                {
                    "name": "test_func",
                    "complexity": 15,
                    "start_line": 1,
                    "end_line": 50,
                }
            ],
            "tech_debts": [
                {
                    "type": "long_method",
                    "severity": "medium",
                    "location": {"file": "test.py", "start_line": 1, "end_line": 50},
                    "description": "方法过长",
                }
            ],
            "metrics": {
                "maintainability_index": 60,
            },
        }

        architecture_assessment = {
            "violations": [],
            "metrics": {"avg_coupling": 0.5},
        }

        result = await agent.generate_optimization_plan(
            code_analysis, architecture_assessment, ["code_quality"]
        )

        assert result is not None
        assert len(result.items) > 0
        assert result.total_effort_hours >= 0

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """测试执行任务"""
        agent = OptimizationAgent()

        task = Task(
            name="优化任务",
            input_data={
                "code_analysis": {
                    "functions": [],
                    "tech_debts": [],
                    "metrics": {},
                },
                "architecture_assessment": {
                    "violations": [],
                    "metrics": {},
                },
                "scope": ["code_quality"],
            },
        )

        result = await agent.execute_task(task)

        assert result.success is True


class TestTestGeneratorAgent:
    """测试生成Agent测试"""

    @pytest.mark.asyncio
    async def test_generate_test_suite(self):
        """测试生成测试套件"""
        agent = TestGeneratorAgent()

        code_analysis = {
            "file_path": "test.py",
            "functions": [
                {
                    "name": "calculate_sum",
                    "params": ["numbers"],
                    "return_type": "int",
                    "complexity": 2,
                }
            ],
        }

        result = await agent.generate_test_suite(
            code_analysis,
            ["calculate_sum"],
            ["unit", "edge_case"],
            "pytest",
        )

        assert result is not None
        assert len(result.test_cases) > 0
        assert result.framework.value == "pytest"

    @pytest.mark.asyncio
    async def test_generate_code(self):
        """测试生成测试代码"""
        agent = TestGeneratorAgent()

        code_analysis = {
            "file_path": "test.py",
            "functions": [
                {
                    "name": "calculate_sum",
                    "params": ["numbers"],
                    "return_type": "int",
                }
            ],
        }

        suite = await agent.generate_test_suite(
            code_analysis,
            ["calculate_sum"],
            ["unit"],
            "pytest",
        )

        code = suite.generate_code()

        assert "import pytest" in code
        assert "def test_" in code
        assert "calculate_sum" in code


class TestOrchestratorAgent:
    """编排Agent测试"""

    @pytest.mark.asyncio
    async def test_initialize_agents(self):
        """测试初始化Agent"""
        orchestrator = OrchestratorAgent()

        await orchestrator.on_start()

        assert "code_analyzer" in orchestrator._agents
        assert "architecture" in orchestrator._agents
        assert "optimization" in orchestrator._agents
        assert "test_generator" in orchestrator._agents

        await orchestrator.on_stop()

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """测试执行工作流"""
        orchestrator = OrchestratorAgent()

        await orchestrator.on_start()

        try:
            workflow = await orchestrator.execute_workflow(
                source_code=SAMPLE_PYTHON_CODE,
                file_path="test.py",
                workflow_type="quick_analysis",
            )

            assert workflow is not None
            assert workflow.status.value == "completed"
            assert len(workflow.results) > 0

        finally:
            await orchestrator.on_stop()

    @pytest.mark.asyncio
    async def test_workflow_templates(self):
        """测试工作流模板"""
        orchestrator = OrchestratorAgent()

        templates = orchestrator._workflow_templates

        assert "full_analysis" in templates
        assert "quick_analysis" in templates
        assert "architecture_review" in templates
        assert "test_generation" in templates

    @pytest.mark.asyncio
    async def test_get_agent_stats(self):
        """测试获取Agent统计"""
        orchestrator = OrchestratorAgent()

        await orchestrator.on_start()

        stats = orchestrator.get_agent_stats()

        assert "orchestrator" in stats
        assert "agents" in stats
        assert "code_analyzer" in stats["agents"]

        await orchestrator.on_stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
