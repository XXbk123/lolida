"""数据库连接与会话管理。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

# SQLite 需要 check_same_thread；PostgreSQL（Supabase）不需要
_connectArgs = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=_connectArgs,
    pool_pre_ping=True,
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
