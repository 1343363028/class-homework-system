from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Submission, Homework, User
from app.schemas import SubmissionBatchCreate
from app.auth import get_current_user, require_committee

router = APIRouter()


@router.post("/batch")
def batch_mark_submitted(
    data: SubmissionBatchCreate,
    _committee: User = Depends(require_committee),
    db: Session = Depends(get_db),
):
    hw = db.query(Homework).filter(Homework.id == data.homework_id).first()
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")

    for user_id in data.user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        existing = db.query(Submission).filter(
            Submission.homework_id == data.homework_id,
            Submission.user_id == user_id,
        ).first()
        if not existing:
            sub = Submission(homework_id=data.homework_id, user_id=user_id, status=data.status)
            db.add(sub)
    db.commit()
    return {"detail": f"已登记 {len(data.user_ids)} 名同学的提交状态"}


@router.delete("/{submission_id}")
def undo_submission(
    submission_id: int,
    _committee: User = Depends(require_committee),
    db: Session = Depends(get_db),
):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    db.delete(sub)
    db.commit()
    return {"detail": "已撤销提交记录"}


@router.post("/student/submit/{homework_id}")
def student_submit(
    homework_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="只有学生可以提交")

    hw = db.query(Homework).filter(Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")

    existing = db.query(Submission).filter(
        Submission.homework_id == homework_id,
        Submission.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已提交过该作业")

    sub = Submission(homework_id=homework_id, user_id=current_user.id)
    db.add(sub)
    db.commit()
    return {"detail": "提交成功"}
