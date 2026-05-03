from fastapi import FastAPI
from fastapi.middleware.cors import CORS

from app.database import engine, Base
from app.api import auth, homework, submission, user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="作业登记系统", version="1.0.0")

app.add_middleware(
    CORS,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(homework.router, prefix="/api/homework", tags=["homework"])
app.include_router(submission.router, prefix="/api/submission", tags=["submission"])
app.include_router(user.router, prefix="/api/users", tags=["users"])


@app.get("/")
def root():
    return {"message": "作业登记系统 API", "version": "1.0.0"}
