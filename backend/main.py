from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from app.db.sqlite import init_sqlite_db, close_sqlite_db
from app.routes import business_scenes, rules, audit_items, audit_tasks, templates, config, upload

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_sqlite_db()
    yield
    await close_sqlite_db()

app = FastAPI(
    title="AI Reviewer API",
    description="基于规则的大模型多模态智能审核平台API",
    version="1.0.0",
    lifespan=lifespan
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:5174").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(business_scenes.router, prefix="/api/scenes", tags=["业务场景"])
app.include_router(rules.router, prefix="/api/rules", tags=["规则管理"])
app.include_router(audit_items.router, prefix="/api/audit-items", tags=["审核项管理"])
app.include_router(audit_tasks.router, prefix="/api/tasks", tags=["审核任务"])
app.include_router(templates.router, prefix="/api/templates", tags=["版式库管理"])
app.include_router(config.router, tags=["配置管理"])
app.include_router(upload.router, prefix="/api", tags=["文件上传"])

@app.get("/")
async def root():
    return {"message": "AI Reviewer API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)