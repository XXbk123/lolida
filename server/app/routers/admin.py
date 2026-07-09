"""管理员 API。"""

import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.ai_client import aiClient
from app.config import ADMIN_PASSWORD, LEVEL_LABELS, LEVELS
from app.database import getDb
from app.models import Feedback, Scheme, SoftwareInfo
from app.schemas import (
    AdminLogin,
    AdminLoginOut,
    FeedbackOut,
    FeedbackProcess,
    MessageOut,
    SchemeOut,
    SchemeUpdate,
    SoftwareInfoOut,
    SoftwareInfoUpdate,
)

router = APIRouter()


def _createAdminToken() -> str:
    """生成无状态管理员 token（服务端重启后仍有效）。"""
    return hmac.new(ADMIN_PASSWORD.encode(), b"lolida_admin", hashlib.sha256).hexdigest()


def _verifyAdminToken(token: str) -> bool:
    """校验管理员 token。"""
    return hmac.compare_digest(token, _createAdminToken())


def _verifyAdmin(authorization: str | None = Header(default=None)) -> None:
    """验证管理员 token。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization[7:]
    if not _verifyAdminToken(token):
        raise HTTPException(status_code=401, detail="Token 无效，请重新登录")


@router.post("/login", response_model=AdminLoginOut)
def adminLogin(body: AdminLogin):
    """管理员密码登录。"""
    if body.password != ADMIN_PASSWORD:
        return AdminLoginOut(success=False)
    return AdminLoginOut(success=True, token=_createAdminToken())


@router.get("/schemes", response_model=list[SchemeOut])
def adminListSchemes(db: Session = Depends(getDb), _: None = Depends(_verifyAdmin)):
    """管理员获取所有方案。"""
    return db.query(Scheme).order_by(Scheme.level).all()


@router.put("/schemes/{level}", response_model=SchemeOut)
def adminUpdateScheme(
    level: str,
    body: SchemeUpdate,
    db: Session = Depends(getDb),
    _: None = Depends(_verifyAdmin),
):
    """管理员编辑方案。"""
    scheme = db.query(Scheme).filter(Scheme.level == level).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="方案未找到")
    if body.title is not None:
        scheme.title = body.title
    if body.markdown is not None:
        scheme.markdown = body.markdown
    if body.prompt_template is not None:
        scheme.prompt_template = body.prompt_template
    db.commit()
    db.refresh(scheme)
    return scheme


@router.delete("/schemes/{level}", response_model=MessageOut)
def adminDeleteScheme(
    level: str,
    db: Session = Depends(getDb),
    _: None = Depends(_verifyAdmin),
):
    """管理员删除方案（会重新种子）。"""
    scheme = db.query(Scheme).filter(Scheme.level == level).first()
    if scheme:
        db.delete(scheme)
        db.commit()
    return MessageOut(success=True, message=f"方案 {level} 已删除")


@router.post("/schemes/{level}/regenerate", response_model=SchemeOut)
async def adminRegenerateScheme(
    level: str,
    db: Session = Depends(getDb),
    _: None = Depends(_verifyAdmin),
):
    """AI 重新生成指定等级方案。"""
    if level not in LEVELS:
        raise HTTPException(status_code=404, detail="等级不存在")

    scheme = db.query(Scheme).filter(Scheme.level == level).first()
    if not scheme:
        scheme = Scheme(level=level)
        db.add(scheme)

    label = LEVEL_LABELS.get(level, level)
    try:
        markdown = await aiClient.generateSchemeMarkdown(level, label)
        prompt = await aiClient.generatePromptTemplate(level, label)
        scheme.markdown = markdown
        scheme.prompt_template = prompt
        scheme.title = f"{label} · AI 生成"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 生成失败: {str(e)}")

    db.commit()
    db.refresh(scheme)
    return scheme


@router.get("/feedback", response_model=list[FeedbackOut])
def adminListFeedback(db: Session = Depends(getDb), _: None = Depends(_verifyAdmin)):
    """管理员获取所有反馈。"""
    return db.query(Feedback).order_by(Feedback.created_at.desc()).all()


@router.patch("/feedback/{feedback_id}", response_model=FeedbackOut)
def adminProcessFeedback(
    feedback_id: int,
    body: FeedbackProcess,
    db: Session = Depends(getDb),
    _: None = Depends(_verifyAdmin),
):
    """标记反馈已处理。"""
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="反馈未找到")
    fb.processed = body.processed
    db.commit()
    db.refresh(fb)
    return fb


@router.get("/software", response_model=SoftwareInfoOut)
def adminGetSoftware(db: Session = Depends(getDb), _: None = Depends(_verifyAdmin)):
    """管理员获取软件信息。"""
    info = db.query(SoftwareInfo).first()
    return info or SoftwareInfoOut(name="萝莉dao", slogan="", version="1.0.0", description="")


@router.put("/software", response_model=SoftwareInfoOut)
def adminUpdateSoftware(
    body: SoftwareInfoUpdate,
    db: Session = Depends(getDb),
    _: None = Depends(_verifyAdmin),
):
    """管理员更新软件信息。"""
    info = db.query(SoftwareInfo).first()
    if not info:
        info = SoftwareInfo()
        db.add(info)
    if body.name is not None:
        info.name = body.name
    if body.slogan is not None:
        info.slogan = body.slogan
    if body.version is not None:
        info.version = body.version
    if body.description is not None:
        info.description = body.description
    db.commit()
    db.refresh(info)
    return info
