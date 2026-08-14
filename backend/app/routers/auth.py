"""认证路由：登录、获取当前用户"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Class, RoleEnum
from ..schemas import LoginRequest, TokenResponse, UserOut
from ..auth import verify_password, create_access_token, get_current_user
from ..config import (
    is_valid_student_id, is_commissary_id,
    COMMISSARY_DEFAULT_PASSWORD,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """登录：学生免密，学委需密码"""
    student_id = req.student_id.strip().upper()

    # 1. 校验学号范围 U202512647 ~ U202512680
    if not is_valid_student_id(student_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="学号不在允许范围内（U202512647 ~ U202512680）",
        )

    # 2. 判断角色
    is_commissary = is_commissary_id(student_id)

    if is_commissary:
        # 学委必须提供密码
        if not req.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="学委账号需要输入密码",
            )
        # 查找或创建用户
        user = db.query(User).filter(User.student_id == student_id).first()
        if user is None:
            # 首次登录：用默认密码创建
            from ..auth import hash_password
            cls = _ensure_class(db)
            user = User(
                student_id=student_id,
                name=f"学委{student_id[-3:]}",
                password_hash=hash_password(COMMISSARY_DEFAULT_PASSWORD),
                role=RoleEnum.commissary,
                class_id=cls.id,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 校验密码
        if not user.password_hash or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="学委密码错误",
            )
    else:
        # 学生：免密登录，直接查找或创建
        user = db.query(User).filter(User.student_id == student_id).first()
        if user is None:
            cls = _ensure_class(db)
            user = User(
                student_id=student_id,
                name=f"同学{student_id[-3:]}",
                password_hash=None,
                role=RoleEnum.student,
                class_id=cls.id,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        # 学生若被设为非活跃，拒绝登录
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用",
            )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        role=user.role,
        name=user.name,
        student_id=user.student_id,
    )


def _ensure_class(db: Session) -> Class:
    """确保默认班级存在"""
    cls = db.query(Class).first()
    if cls is None:
        cls = Class(name="默认班级")
        db.add(cls)
        db.commit()
        db.refresh(cls)
    return cls


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
