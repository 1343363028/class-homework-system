"""SQLAlchemy 数据模型"""
import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Boolean,
    ForeignKey, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from .database import Base


class RoleEnum(str, enum.Enum):
    student = "student"
    commissary = "commissary"


class DuePeriodEnum(str, enum.Enum):
    """截止时段：中午 / 晚上"""
    noon = "noon"      # 中午（12:00）
    evening = "evening"  # 晚上（23:59）


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("User", back_populates="class_", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="class_", cascade="all, delete-orphan")
    homeworks = relationship("Homework", back_populates="class_", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(32), nullable=False, unique=True, index=True, comment="学号")
    name = Column(String(64), nullable=False, comment="姓名")
    password_hash = Column(String(256), nullable=True, comment="密码哈希（学生为空）")
    role = Column(SAEnum(RoleEnum), nullable=False, default=RoleEnum.student)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    class_ = relationship("Class", back_populates="users")


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    name = Column(String(64), nullable=False)
    color = Column(String(16), nullable=False, default="#2E86C1")
    icon = Column(String(64), nullable=False, default="book", comment="图标标识，支持自定义文本/emoji")
    created_at = Column(DateTime, default=datetime.utcnow)
    class_ = relationship("Class", back_populates="subjects")
    homeworks = relationship("Homework", back_populates="subject")


class Homework(Base):
    __tablename__ = "homeworks"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    assigned_date = Column(Date, nullable=False, comment="布置日期")
    due_date = Column(Date, nullable=False, comment="截止日期")
    due_period = Column(SAEnum(DuePeriodEnum), nullable=False, default=DuePeriodEnum.evening,
                        comment="截止时段：noon中午 / evening晚上")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    class_ = relationship("Class", back_populates="homeworks")
    subject = relationship("Subject", back_populates="homeworks")
    creator = relationship("User")
