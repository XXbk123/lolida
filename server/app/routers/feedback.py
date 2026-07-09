"""用户反馈 API。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import getDb
from app.models import Feedback
from app.schemas import FeedbackCreate, FeedbackOut, MessageOut

router = APIRouter()


@router.post("/feedback", response_model=MessageOut)
def createFeedback(body: FeedbackCreate, db: Session = Depends(getDb)):
    """提交用户反馈。"""
    fb = Feedback(
        level=body.level,
        is_valid=body.is_valid,
        content=body.content,
        image_path=body.image_path,
    )
    db.add(fb)
    db.commit()
    return MessageOut(success=True, message="反馈已提交，感谢兄弟的宝贵意见~")


@router.get("/feedback", response_model=list[FeedbackOut])
def listFeedback(db: Session = Depends(getDb)):
    """获取所有反馈（公开列表）。"""
    return db.query(Feedback).order_by(Feedback.created_at.desc()).all()
