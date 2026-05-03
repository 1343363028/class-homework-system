from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Homework, User, Submission, SubmissionStatus
from app.schemas import HomeworkCreate, HomeworkOut, HomeworkDetail
from app.auth import get_current_user, require_committee

router = APIRouter()


@router.get("/", response_model=list[HomeworkDetail])
def list_homework(
    current_user: User = Depends(get_current_user),
    include_status: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Homework).order_by(Homework.created_at.desc())
    results = []
    for hw in q:
        total = db.query(User).filter(User.role == "student").count()
        submitted = db.query(Submission).filter(Submission.homework_id == hw.id).count()

        detail = HomeworkDetail(
            id=hw.id,
            title=hw.title,
            description=hw.description,
            due_date=hw.due_date,
            created_by=hw.created_by,
            created_at=hw.created_at,
            creator_name=hw.creator.name if hw.creator else None,
            submitted_count=submitted,
            total_count=total,
        )

        if include_status and current_user.role == "student":
            sub = db.query(Submission).filter(
                Submission.homework_id == hw.id,
                Submission.user_id == current_user.id,
            ).first()
            detail.submitted_count = 1 if sub else 0
            detail.total_count = 1

        results.append(detail)
    return results


@router.post("/", response_model=HomeworkOut)
def create_homework(
    hw: HomeworkCreate,
    _committee: User = Depends(require_committee),
    db: Session = Depends(get_db),
):
    db_hw = Homework(
        title=hw.title,
        description=hw.description,
        due_date=hw.due_date,
        created_by=_committee.id,
    )
    db.add(db_hw)
    db.commit()
    db.refresh(db_hw)
    return db_hw


@router.delete("/{homework_id}")
def delete_homework(
    homework_id: int,
    _committee: User = Depends(require_committee),
    db: Session = Depends(get_db),
):
    hw = db.query(Homework).filter(Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    db.query(Submission).filter(Submission.homework_id == homework_id).delete()
    db.delete(hw)
    db.commit()
    return {"detail": "删除成功"}


@router.get("/{homework_id}/submissions")
def get_submissions(
    homework_id: int,
    _committee: User = Depends(require_committee),
    db: Session = Depends(get_db),
):
    all_students = db.query(User).filter(User.role == "student").all()
    submitted_ids = {
        s.user_id for s in db.query(Submission).filter(Submission.homework_id == homework_id).all()
    }

    submissions = []
    for student in all_students:
        if student.id in submitted_ids:
            sub = db.query(Submission).filter(
                Submission.homework_id == homework_id,
                Submission.user_id == student.id,
            ).first()
            submissions.append({
                "id": sub.id,
                "user_id": student.id,
                "student_id": student.student_id,
                "student_name": student.name,
                "status": sub.status.value,
                "submitted_at": sub.submitted_at,
                "is_submitted": True,
            })
        else:
            submissions.append({
                "id": None,
                "user_id": student.id,
                "student_id": student.student_id,
                "student_name": student.name,
                "status": "not_submitted",
                "submitted_at": None,
                "is_submitted": False,
            })

    return submissions


@router.get("/{homework_id}/unsubmitted")
def get_unsubmitted(
    homework_id: int,
    _committee: User = Depends(require_committee),
    db: Session = Depends(get_db),
):
    submitted_ids = {
        s.user_id for s in db.query(Submission).filter(Submission.homework_id == homework_id).all()
    }
    unsubmitted = db.query(User).filter(
        User.role == "student",
        User.id.notin_(submitted_ids),
    ).all()
    return [
        {"id": u.id, "student_id": u.student_id, "name": u.name}
        for u in unsubmitted
    ]
