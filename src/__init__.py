"""
MultiAgent-CodeForge - 多Agent协作的代码智能分析与优化系统

本包提供了一套完整的多Agent协作框架，用于代码分析、架构评估、优化建议和测试生成。
"""

__version__ = "1.0.0"
__author__ = "MultiAgent-CodeForge Team"
__description__ = "多Agent协作的代码智能分析与优化系统"

from .core.message import Message, MessageType
from .core.task import Task, TaskStatus
from .core.agent import BaseAgent
from .agents.orchestrator import OrchestratorAgent

__all__ = [
    "Message",
    "MessageType",
    "Task",
    "TaskStatus",
    "BaseAgent",
    "OrchestratorAgent",
]
