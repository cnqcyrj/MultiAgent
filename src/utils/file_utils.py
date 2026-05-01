"""
文件工具模块 - 提供文件操作功能

本模块提供：
- 文件读写
- 文件类型检测
- 路径处理
"""

import os
from pathlib import Path
from typing import Optional, List


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    读取文件内容

    Args:
        file_path: 文件路径
        encoding: 文件编码

    Returns:
        文件内容

    Raises:
        FileNotFoundError: 文件不存在
        IOError: 读取失败
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise IOError(f"读取文件失败: {e}")


def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True,
) -> None:
    """
    写入文件内容

    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码
        create_dirs: 是否创建目录

    Raises:
        IOError: 写入失败
    """
    path = Path(file_path)

    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"写入文件失败: {e}")


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名

    Args:
        file_path: 文件路径

    Returns:
        文件扩展名（小写，不含点号）
    """
    return Path(file_path).suffix.lstrip(".").lower()


def get_file_name(file_path: str) -> str:
    """
    获取文件名（不含扩展名）

    Args:
        file_path: 文件路径

    Returns:
        文件名
    """
    return Path(file_path).stem


def get_file_size(file_path: str) -> int:
    """
    获取文件大小（字节）

    Args:
        file_path: 文件路径

    Returns:
        文件大小

    Raises:
        FileNotFoundError: 文件不存在
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    return path.stat().st_size


def list_files(
    directory: str,
    extension: Optional[str] = None,
    recursive: bool = False,
) -> List[str]:
    """
    列出目录中的文件

    Args:
        directory: 目录路径
        extension: 文件扩展名过滤
        recursive: 是否递归

    Returns:
        文件路径列表
    """
    path = Path(directory)
    if not path.exists():
        return []

    files = []
    pattern = "**/*" if recursive else "*"

    for file_path in path.glob(pattern):
        if file_path.is_file():
            if extension is None or file_path.suffix == f".{extension}":
                files.append(str(file_path))

    return sorted(files)


def ensure_directory(directory: str) -> Path:
    """
    确保目录存在

    Args:
        directory: 目录路径

    Returns:
        目录路径对象
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_python_file(file_path: str) -> bool:
    """
    判断是否为Python文件

    Args:
        file_path: 文件路径

    Returns:
        是否为Python文件
    """
    return get_file_extension(file_path) == "py"


def get_relative_path(file_path: str, base_path: str) -> str:
    """
    获取相对路径

    Args:
        file_path: 文件路径
        base_path: 基础路径

    Returns:
        相对路径
    """
    try:
        return str(Path(file_path).relative_to(base_path))
    except ValueError:
        return file_path


def normalize_path(file_path: str) -> str:
    """
    标准化路径

    Args:
        file_path: 文件路径

    Returns:
        标准化后的路径
    """
    return str(Path(file_path).resolve())
