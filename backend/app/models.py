from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class Role(str, enum.Enum):
    STUDENT = "student"
    COMMITTEE = "committee"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(SAEnum(Role), default=Role.STUDENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="user")


class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    due_date = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User")
    submissions = relationship("Submission", back_populates="homework")


class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    LATE = "late"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homework.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(SubmissionStatus), default=SubmissionStatus.SUBMITTED, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    homework = relationship("Homework", back_populates="submissions")
    user = relationship("User", back_populates="submissions")

    __table_args__ = (
        UniqueConstraint('homework_id', 'user_id', name='uq_homework_user'),
    )
