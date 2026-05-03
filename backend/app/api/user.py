from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserOut
from app.auth import require_committee

router = APIRouter()


@router.get("/", response_model=list[UserOut])
def list_students(
    role: Optional[str] = Query(None),
    _committee: User = Depends(require_committee),
    db: Session = Depends(get_db),
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    return q.order_by(User.student_id).all()
