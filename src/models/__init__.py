"""
数据模型模块 - 定义数据模型
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


class AnalysisRequest(BaseModel):
    """分析请求模型"""

    source_code: str = Field(..., description="源代码内容")
    file_path: str = Field(default="<string>", description="文件路径")
    language: str = Field(default="python", description="编程语言")
    workflow_type: str = Field(default="full_analysis", description="工作流类型")
    options: Dict[str, Any] = Field(default_factory=dict, description="选项")


class AnalysisResponse(BaseModel):
    """分析响应模型"""

    success: bool = Field(..., description="是否成功")
    workflow_id: Optional[str] = Field(None, description="工作流ID")
    data: Optional[Dict[str, Any]] = Field(None, description="结果数据")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(default=0.0, description="执行时间（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class WorkflowStatus(BaseModel):
    """工作流状态模型"""

    workflow_id: str = Field(..., description="工作流ID")
    status: str = Field(..., description="状态")
    current_stage: Optional[str] = Field(None, description="当前阶段")
    progress: float = Field(default=0.0, description="进度")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    error: Optional[str] = Field(None, description="错误信息")


class AgentInfo(BaseModel):
    """Agent信息模型"""

    agent_id: str = Field(..., description="Agent标识")
    name: str = Field(..., description="Agent名称")
    status: str = Field(..., description="状态")
    capabilities: List[str] = Field(default_factory=list, description="能力列表")
    current_tasks: int = Field(default=0, description="当前任务数")


class SystemStatus(BaseModel):
    """系统状态模型"""

    status: str = Field(..., description="系统状态")
    agents: List[AgentInfo] = Field(default_factory=list, description="Agent列表")
    active_workflows: int = Field(default=0, description="活动工作流数")
    total_tasks: int = Field(default=0, description="总任务数")
    uptime: float = Field(default=0.0, description="运行时间（秒）")
