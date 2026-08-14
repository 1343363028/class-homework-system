"""FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, SessionLocal
from .models import Class, Subject
from .config import PRESET_SUBJECTS, CORS_ORIGINS
from .routers import api_router


def _seed_data():
    """初始化默认班级与预置科目"""
    db = SessionLocal()
    try:
        if not db.query(Class).first():
            cls = Class(name="默认班级")
            db.add(cls)
            db.commit()
            db.refresh(cls)
        else:
            cls = db.query(Class).first()

        for item in PRESET_SUBJECTS:
            exists = db.query(Subject).filter(
                Subject.class_id == cls.id,
                Subject.name == item["name"],
            ).first()
            if not exists:
                db.add(Subject(class_id=cls.id, **item))
        db.commit()
    finally:
        db.close()


def _init_db():
    """建表 + 种子数据（供 lifespan 与直接导入共用）"""
    Base.metadata.create_all(bind=engine)
    _seed_data()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_db()
    yield


# 模块导入时即初始化（兼容直接 uvicorn 启动与 TestClient）
_init_db()

app = FastAPI(
    title="班级作业查询系统 API",
    version="2.0.0",
    description="面向高校班级的作业查询与管理系统后端",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # 通配符 "*" 时必须为 False
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def health():
    return {"status": "ok", "service": "homework-system-api", "version": "2.0.0"}


@app.get("/api/health")
def api_health():
    return {"status": "ok"}
