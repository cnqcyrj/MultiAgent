"""
测试配置文件

提供测试夹具和配置
"""

import asyncio
import pytest
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_python_code() -> str:
    """示例Python代码"""
    return '''
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


@pytest.fixture
def sample_project_structure() -> dict:
    """示例项目结构"""
    return {
        "directories": ["models", "views", "controllers"],
        "modules": [
            {"name": "models", "path": "models"},
            {"name": "views", "path": "views"},
            {"name": "controllers", "path": "controllers"},
        ],
    }


@pytest.fixture
def sample_code_analysis() -> dict:
    """示例代码分析结果"""
    return {
        "file_path": "test.py",
        "language": "python",
        "loc": 50,
        "functions": [
            {
                "name": "fibonacci",
                "params": ["n"],
                "return_type": "list",
                "complexity": 4,
            },
            {
                "name": "is_prime",
                "params": ["num"],
                "return_type": "bool",
                "complexity": 3,
            },
        ],
        "classes": [
            {
                "name": "Calculator",
                "methods": ["add", "subtract"],
                "attributes": ["history"],
            }
        ],
        "complexity": {
            "total": 7,
            "average": 3.5,
            "max": 4,
        },
        "tech_debts": [],
        "metrics": {
            "maintainability_index": 75.5,
            "function_count": 2,
            "class_count": 1,
        },
    }
