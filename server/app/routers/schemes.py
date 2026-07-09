"""方案管理 API。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import LEVELS, LEVEL_LABELS
from app.database import getDb
from app.models import LevelStat, Scheme
from app.schemas import MessageOut, SchemeOut

router = APIRouter()


@router.get("/schemes", response_model=list[SchemeOut])
def listSchemes(db: Session = Depends(getDb)):
    """获取所有等级方案列表。"""
    return db.query(Scheme).order_by(Scheme.level).all()


@router.get("/schemes/{level}", response_model=SchemeOut)
def getScheme(level: str, db: Session = Depends(getDb)):
    """按等级获取方案详情。"""
    if level not in LEVELS:
        raise HTTPException(status_code=404, detail=f"等级 {level} 不存在")
    scheme = db.query(Scheme).filter(Scheme.level == level).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="方案未找到")
    return scheme


@router.post("/schemes/{level}/select", response_model=MessageOut)
def selectLevel(level: str, db: Session = Depends(getDb)):
    """记录等级选择次数。"""
    if level not in LEVELS:
        raise HTTPException(status_code=404, detail=f"等级 {level} 不存在")
    stat = db.query(LevelStat).filter(LevelStat.level == level).first()
    if stat:
        stat.select_count += 1
    else:
        db.add(LevelStat(level=level, select_count=1, generate_count=0))
    db.commit()
    return MessageOut(success=True, message=f"已选择 {LEVEL_LABELS.get(level, level)}")
