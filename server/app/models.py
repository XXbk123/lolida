"""数据库模型定义。"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcNow() -> datetime:
    """返回当前 UTC 时间。"""
    return datetime.now(timezone.utc)


class SoftwareInfo(Base):
    """软件信息表。"""

    __tablename__ = "software_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), default="萝莉dao")
    slogan: Mapped[str] = mapped_column(String(200), default="")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    description: Mapped[str] = mapped_column(Text, default="")


class Scheme(Base):
    """安装方案表，按等级唯一。"""

    __tablename__ = "schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(100), default="")
    markdown: Mapped[str] = mapped_column(Text, default="")
    prompt_template: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcNow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcNow, onupdate=_utcNow)


class Feedback(Base):
    """用户反馈表。"""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[str] = mapped_column(String(10), default="")
    is_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    content: Mapped[str] = mapped_column(Text, default="")
    image_path: Mapped[str] = mapped_column(String(500), default="")
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcNow)


class LevelStat(Base):
    """等级选择次数统计。"""

    __tablename__ = "level_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    select_count: Mapped[int] = mapped_column(Integer, default=0)
    generate_count: Mapped[int] = mapped_column(Integer, default=0)
