"""Pydantic 请求/响应模型。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SoftwareInfoOut(BaseModel):
    """软件信息响应。"""

    name: str
    slogan: str
    version: str
    description: str


class SoftwareInfoUpdate(BaseModel):
    """软件信息更新。"""

    name: Optional[str] = None
    slogan: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None


class SchemeOut(BaseModel):
    """方案响应。"""

    id: int
    level: str
    title: str
    markdown: str
    prompt_template: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SchemeUpdate(BaseModel):
    """方案更新。"""

    title: Optional[str] = None
    markdown: Optional[str] = None
    prompt_template: Optional[str] = None


class FeedbackCreate(BaseModel):
    """创建反馈。"""

    level: str = Field(default="")
    is_valid: Optional[bool] = None
    content: str = Field(default="")
    image_path: str = Field(default="")


class FeedbackOut(BaseModel):
    """反馈响应。"""

    id: int
    level: str
    is_valid: Optional[bool]
    content: str
    image_path: str
    processed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackProcess(BaseModel):
    """标记反馈已处理。"""

    processed: bool = True


class LevelStatOut(BaseModel):
    """等级统计响应。"""

    level: str
    label: str
    select_count: int
    generate_count: int


class AdminLogin(BaseModel):
    """管理员登录。"""

    password: str


class AdminLoginOut(BaseModel):
    """登录结果。"""

    success: bool
    token: str = ""


class GenerateOut(BaseModel):
    """图片生成响应。"""

    success: bool
    image_url: str = ""
    image_path: str = ""
    image_base64: str = ""
    message: str = ""


class MessageOut(BaseModel):
    """通用消息响应。"""

    success: bool
    message: str = ""
