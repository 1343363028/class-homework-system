from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    student_id: str
    name: str
    role: str = "student"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class HomeworkBase(BaseModel):
    title: str
    description: str = ""
    due_date: Optional[datetime] = None


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkOut(HomeworkBase):
    id: int
    created_by: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HomeworkDetail(HomeworkOut):
    creator_name: Optional[str] = None
    submitted_count: int = 0
    total_count: int = 0


class SubmissionOut(BaseModel):
    id: int
    homework_id: int
    user_id: int
    student_name: Optional[str] = None
    student_id: Optional[str] = None
    status: str
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmissionBatchCreate(BaseModel):
    homework_id: int
    user_ids: list[int]
    status: str = "submitted"


class LoginRequest(BaseModel):
    student_id: str
    password: str
