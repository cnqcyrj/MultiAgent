#!/usr/bin/env python
"""
MultiAgent-CodeForge 启动脚本

快速运行示例分析
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


async def main():
    """主函数"""
    try:
        from src.agents.orchestrator import OrchestratorAgent

        print("=" * 60)
        print("MultiAgent-CodeForge 代码分析系统")
        print("=" * 60)
        print()

        # 示例代码
        sample_code = '''
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


class Calculator:
    """计算器类"""

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
'''

        print("正在初始化Agent系统...")
        orchestrator = OrchestratorAgent()
        await orchestrator.on_start()

        try:
            print("正在分析代码...")
            print()

            workflow = await orchestrator.execute_workflow(
                source_code=sample_code,
                file_path="example.py",
                workflow_type="quick_analysis",
            )

            # 打印结果
            print("-" * 60)
            print("分析完成!")
            print("-" * 60)

            summary = workflow.results.get("result_aggregation", {}).get("summary", {})
            metrics = summary.get("metrics", {})

            print(f"\n代码行数: {metrics.get('lines_of_code', 0)}")
            print(f"函数数量: {metrics.get('function_count', 0)}")
            print(f"类数量: {metrics.get('class_count', 0)}")

            findings = summary.get("key_findings", [])
            if findings:
                print("\n关键发现:")
                for finding in findings:
                    print(f"  - {finding}")

            recommendations = summary.get("recommendations", [])
            if recommendations:
                print("\n优化建议:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"  {i}. {rec}")

            print()
            print("=" * 60)

        finally:
            await orchestrator.on_stop()

    except ImportError as e:
        print(f"导入错误: {e}")
        print("\n请先安装依赖:")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
