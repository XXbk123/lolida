"""统计数据 API。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import LEVEL_LABELS
from app.database import getDb
from app.models import LevelStat
from app.schemas import LevelStatOut

router = APIRouter()


@router.get("/stats", response_model=list[LevelStatOut])
def getStats(db: Session = Depends(getDb)):
    """获取各等级选择与生成的次数统计。"""
    stats = db.query(LevelStat).order_by(LevelStat.level).all()
    return [
        LevelStatOut(
            level=s.level,
            label=LEVEL_LABELS.get(s.level, s.level),
            select_count=s.select_count,
            generate_count=s.generate_count,
        )
        for s in stats
    ]
