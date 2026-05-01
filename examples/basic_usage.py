"""
MultiAgent-CodeForge 基本使用示例

本示例展示如何使用多Agent协作系统进行代码分析。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.orchestrator import OrchestratorAgent
from src.core.task import Task


# 示例Python代码
SAMPLE_CODE = '''
def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]

    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib


def is_prime(num):
    """判断是否为素数"""
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True


class MathUtils:
    """数学工具类"""

    @staticmethod
    def factorial(n):
        """计算阶乘"""
        if n < 0:
            raise ValueError("负数没有阶乘")
        if n <= 1:
            return 1
        return n * MathUtils.factorial(n - 1)

    @staticmethod
    def gcd(a, b):
        """计算最大公约数"""
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def lcm(a, b):
        """计算最小公倍数"""
        return a * b // MathUtils.gcd(a, b)
'''


async def main():
    """主函数"""
    print("=" * 60)
    print("MultiAgent-CodeForge 代码分析系统")
    print("=" * 60)
    print()

    # 创建编排Agent
    orchestrator = OrchestratorAgent()

    # 启动Agent
    await orchestrator.on_start()

    try:
        # 执行完整分析工作流
        print("正在执行代码分析...")
        print()

        workflow = await orchestrator.execute_workflow(
            source_code=SAMPLE_CODE,
            file_path="math_utils.py",
            workflow_type="full_analysis",
            options={
                "language": "python",
                "optimization_scope": ["code_quality", "performance"],
                "test_types": ["unit", "edge_case"],
                "test_framework": "pytest",
            },
        )

        # 打印结果摘要
        print("分析完成!")
        print()
        print("-" * 60)
        print("结果摘要:")
        print("-" * 60)

        summary = workflow.results.get("result_aggregation", {}).get("summary", {})

        # 基本指标
        metrics = summary.get("metrics", {})
        print(f"\n代码行数: {metrics.get('lines_of_code', 0)}")
        print(f"函数数量: {metrics.get('function_count', 0)}")
        print(f"类数量: {metrics.get('class_count', 0)}")
        print(f"总复杂度: {metrics.get('complexity', 0)}")

        # 关键发现
        findings = summary.get("key_findings", [])
        if findings:
            print("\n关键发现:")
            for finding in findings:
                print(f"  - {finding}")

        # 建议
        recommendations = summary.get("recommendations", [])
        if recommendations:
            print("\n优化建议:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")

        # 生成的测试数量
        test_gen = workflow.results.get("test_generation", {})
        test_suite = test_gen.get("test_suite", {})
        test_cases = test_suite.get("test_cases", [])
        if test_cases:
            print(f"\n生成测试用例: {len(test_cases)} 个")
            print(f"目标覆盖率: {test_suite.get('coverage_target', 0)}%")

        print()
        print("=" * 60)
        print("分析完成!")
        print("=" * 60)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 停止Agent
        await orchestrator.on_stop()


if __name__ == "__main__":
    asyncio.run(main())
