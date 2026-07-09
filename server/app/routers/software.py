"""软件信息 API。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import getDb
from app.models import SoftwareInfo
from app.schemas import SoftwareInfoOut

router = APIRouter()


@router.get("/software", response_model=SoftwareInfoOut)
def getSoftware(db: Session = Depends(getDb)):
    """获取软件信息。"""
    info = db.query(SoftwareInfo).first()
    if not info:
        return SoftwareInfoOut(name="萝莉dao", slogan="", version="1.0.0", description="")
    return info
