"""
验证器模块 - 提供数据验证功能

本模块提供：
- 源代码验证
- 文件路径验证
- 配置验证
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class ValidationError(Exception):
    """验证错误"""

    def __init__(self, message: str, field: str = None, details: dict = None):
        """
        初始化验证错误

        Args:
            message: 错误信息
            field: 字段名
            details: 详细信息
        """
        super().__init__(message)
        self.field = field
        self.details = details or {}


def validate_source_code(
    source_code: str,
    language: str = "python",
    max_size: int = 1024 * 1024,  # 1MB
) -> Tuple[bool, Optional[str]]:
    """
    验证源代码

    Args:
        source_code: 源代码
        language: 编程语言
        max_size: 最大大小（字节）

    Returns:
        (是否有效, 错误信息)
    """
    # 检查是否为空
    if not source_code or not source_code.strip():
        return False, "源代码不能为空"

    # 检查大小
    if len(source_code.encode("utf-8")) > max_size:
        return False, f"源代码大小超过限制 ({max_size} bytes)"

    # 语言特定验证
    if language == "python":
        return validate_python_source(source_code)

    return True, None


def validate_python_source(source_code: str) -> Tuple[bool, Optional[str]]:
    """
    验证Python源代码

    Args:
        source_code: Python源代码

    Returns:
        (是否有效, 错误信息)
    """
    import ast

    try:
        ast.parse(source_code)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: 行 {e.lineno}, {e.msg}"


def validate_file_path(
    file_path: str,
    must_exist: bool = False,
    allowed_extensions: Optional[List[str]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    验证文件路径

    Args:
        file_path: 文件路径
        must_exist: 是否必须存在
        allowed_extensions: 允许的扩展名列表

    Returns:
        (是否有效, 错误信息)
    """
    # 检查是否为空
    if not file_path or not file_path.strip():
        return False, "文件路径不能为空"

    path = Path(file_path)

    # 检查是否为绝对路径（可选）
    # if not path.is_absolute():
    #     return False, "文件路径必须是绝对路径"

    # 检查是否存在
    if must_exist and not path.exists():
        return False, f"文件不存在: {file_path}"

    # 检查扩展名
    if allowed_extensions:
        ext = path.suffix.lstrip(".").lower()
        if ext not in allowed_extensions:
            return False, f"不支持的文件扩展名: {ext}"

    return True, None


def validate_language(language: str) -> Tuple[bool, Optional[str]]:
    """
    验证编程语言

    Args:
        language: 编程语言

    Returns:
        (是否有效, 错误信息)
    """
    supported_languages = ["python"]
    if language.lower() not in supported_languages:
        return False, f"不支持的语言: {language}，支持: {supported_languages}"
    return True, None


def validate_workflow_type(workflow_type: str) -> Tuple[bool, Optional[str]]:
    """
    验证工作流类型

    Args:
        workflow_type: 工作流类型

    Returns:
        (是否有效, 错误信息)
    """
    valid_types = [
        "full_analysis",
        "quick_analysis",
        "architecture_review",
        "test_generation",
    ]
    if workflow_type not in valid_types:
        return False, f"无效的工作流类型: {workflow_type}，有效: {valid_types}"
    return True, None


def validate_agent_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证Agent配置

    Args:
        config: 配置字典

    Returns:
        (是否有效, 错误信息)
    """
    # 检查必需字段
    required_fields = []
    for field in required_fields:
        if field not in config:
            return False, f"缺少必需字段: {field}"

    # 检查类型
    if "max_concurrent_tasks" in config:
        if not isinstance(config["max_concurrent_tasks"], int):
            return False, "max_concurrent_tasks 必须是整数"
        if config["max_concurrent_tasks"] < 1:
            return False, "max_concurrent_tasks 必须大于 0"

    if "timeout" in config:
        if not isinstance(config["timeout"], (int, float)):
            return False, "timeout 必须是数字"
        if config["timeout"] < 0:
            return False, "timeout 不能为负数"

    return True, None


def validate_task_input(
    task_input: Dict[str, Any],
    required_fields: Optional[List[str]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    验证任务输入

    Args:
        task_input: 任务输入
        required_fields: 必需字段列表

    Returns:
        (是否有效, 错误信息)
    """
    if not isinstance(task_input, dict):
        return False, "任务输入必须是字典"

    if required_fields:
        for field in required_fields:
            if field not in task_input:
                return False, f"缺少必需字段: {field}"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    清理文件名

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(illegal_chars, "_", filename)

    # 移除前后空格和点
    sanitized = sanitized.strip(". ")

    # 确保不为空
    if not sanitized:
        sanitized = "unnamed"

    return sanitized
