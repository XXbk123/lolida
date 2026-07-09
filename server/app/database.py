"""数据库连接与会话管理。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 基类。"""

    pass


def getDb():
    """获取数据库会话依赖。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
