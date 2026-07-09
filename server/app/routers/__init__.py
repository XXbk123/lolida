"""API 路由汇总。"""

from fastapi import APIRouter

from app.routers import admin, feedback, generate, schemes, software, stats

apiRouter = APIRouter(prefix="/api")

apiRouter.include_router(software.router, tags=["software"])
apiRouter.include_router(schemes.router, tags=["schemes"])
apiRouter.include_router(generate.router, tags=["generate"])
apiRouter.include_router(feedback.router, tags=["feedback"])
apiRouter.include_router(stats.router, tags=["stats"])
apiRouter.include_router(admin.router, prefix="/admin", tags=["admin"])
