from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, Token, UserCreate, UserOut
from app.password import hash_password, verify_password
from app.auth import create_access_token, get_current_user

router = APIRouter()


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == req.student_id).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="学号或密码错误")
    token = create_access_token({"user_id": user.id})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.student_id == user.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该学号已注册")
    db_user = User(
        student_id=user.student_id,
        name=user.name,
        password=hash_password(user.password),
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user
