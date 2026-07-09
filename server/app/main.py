"""萝莉dao FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.ai_client import aiClient
from app.config import DOUBAO_IMAGE_MODEL, HOST, PORT, STATIC_DIR
from app.database import Base, SessionLocal, engine
from app.routers import apiRouter
from app.seed import seedDatabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：初始化数据库。"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seedDatabase(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="萝莉dao API",
    description="今天的兄弟还会是兄弟吗？嘿嘿~",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apiRouter)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def healthCheck():
    """健康检查，含豆包生图模型状态。"""
    doubaoOk, doubaoMsg = await aiClient.checkDoubaoImageModel()
    return {
        "status": "ok",
        "message": "萝莉dao 服务运行中~ 嘿嘿",
        "imageGen": {
            "provider": "doubao",
            "model": DOUBAO_IMAGE_MODEL,
            "ready": doubaoOk,
            "detail": doubaoMsg if not doubaoOk else "生图模型可用",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
