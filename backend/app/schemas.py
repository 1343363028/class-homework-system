"""Pydantic 请求/响应模型"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from .models import RoleEnum, DuePeriodEnum


# ---------- 认证 ----------
class LoginRequest(BaseModel):
    student_id: str = Field(..., description="学号")
    password: Optional[str] = Field(None, description="密码（学委必填，学生可空）")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum
    name: str
    student_id: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: str
    name: str
    role: RoleEnum
    class_id: int


# ---------- 科目 ----------
class SubjectBase(BaseModel):
    name: str = Field(..., max_length=64)
    color: str = Field("#2E86C1", max_length=16)
    icon: str = Field("book", max_length=64)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=64)
    color: Optional[str] = Field(None, max_length=16)
    icon: Optional[str] = Field(None, max_length=64)


class SubjectOut(SubjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    class_id: int


# ---------- 作业 ----------
class HomeworkBase(BaseModel):
    subject_id: int
    title: str = Field(..., max_length=200)
    content: Optional[str] = None
    assigned_date: date
    due_date: date
    due_period: DuePeriodEnum = DuePeriodEnum.evening


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkUpdate(BaseModel):
    subject_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    assigned_date: Optional[date] = None
    due_date: Optional[date] = None
    due_period: Optional[DuePeriodEnum] = None


class HomeworkOut(HomeworkBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    class_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    subject: Optional[SubjectOut] = None


class HomeworkListByDate(BaseModel):
    date: date
    homeworks: List[HomeworkOut]


# ---------- 倒计时 ----------
class CountdownItem(BaseModel):
    homework_id: int
    title: str
    subject_name: str
    subject_color: str
    due_date: date
    due_period: DuePeriodEnum
    days_left: int = Field(..., description="剩余天数，负数表示已截止")
    is_overdue: bool = Field(..., description="是否已截止")


class CountdownResponse(BaseModel):
    items: List[CountdownItem]


# ---------- 通用 ----------
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
