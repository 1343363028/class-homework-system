"""作业路由：增删改查、按日期查询、倒计时"""
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from ..database import get_db
from ..models import User, Homework, Subject, RoleEnum, DuePeriodEnum
from ..schemas import (
    HomeworkCreate, HomeworkUpdate, HomeworkOut,
    HomeworkListByDate, CountdownResponse, CountdownItem,
    MessageResponse,
)
from ..auth import get_current_user, require_role

router = APIRouter(prefix="/api/homeworks", tags=["作业"])


@router.get("", response_model=List[HomeworkOut])
def list_homeworks(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Homework).filter(
        Homework.class_id == current_user.class_id
    ).options(selectinload(Homework.subject))
    if start_date:
        q = q.filter(Homework.assigned_date >= start_date)
    if end_date:
        q = q.filter(Homework.due_date <= end_date)
    return q.order_by(Homework.due_date.asc()).all()


@router.get("/by-date/{query_date}", response_model=HomeworkListByDate)
def get_by_date(
    query_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(Homework).filter(
        Homework.class_id == current_user.class_id,
        (Homework.assigned_date == query_date) | (Homework.due_date == query_date),
    ).options(selectinload(Homework.subject)).all()
    return HomeworkListByDate(date=query_date, homeworks=items)


@router.get("/countdown", response_model=CountdownResponse)
def countdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """倒计时：返回未截止的作业，按剩余天数升序"""
    today = date.today()
    items = db.query(Homework).filter(
        Homework.class_id == current_user.class_id,
        Homework.due_date >= today,
    ).options(selectinload(Homework.subject)).order_by(Homework.due_date.asc()).all()

    result = []
    for hw in items:
        days_left = (hw.due_date - today).days
        result.append(CountdownItem(
            homework_id=hw.id,
            title=hw.title,
            subject_name=hw.subject.name if hw.subject else "未知",
            subject_color=hw.subject.color if hw.subject else "#5A6B7D",
            due_date=hw.due_date,
            due_period=hw.due_period,
            days_left=days_left,
            is_overdue=days_left < 0,
        ))
    return CountdownResponse(items=result)


@router.post("", response_model=HomeworkOut, status_code=201)
def create_homework(
    req: HomeworkCreate,
    current_user: User = Depends(require_role(RoleEnum.commissary)),
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(
        Subject.id == req.subject_id,
        Subject.class_id == current_user.class_id,
    ).first()
    if not subject:
        raise HTTPException(status_code=400, detail="科目不存在")
    if req.due_date < req.assigned_date:
        raise HTTPException(status_code=400, detail="截止日期不能早于布置日期")

    hw = Homework(
        class_id=current_user.class_id,
        created_by=current_user.id,
        **req.model_dump(),
    )
    db.add(hw)
    db.commit()
    db.refresh(hw)
    return hw


@router.put("/{homework_id}", response_model=HomeworkOut)
def update_homework(
    homework_id: int,
    req: HomeworkUpdate,
    current_user: User = Depends(require_role(RoleEnum.commissary)),
    db: Session = Depends(get_db),
):
    hw = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.class_id == current_user.class_id,
    ).first()
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")

    update_data = req.model_dump(exclude_unset=True)
    new_assigned = update_data.get("assigned_date", hw.assigned_date)
    new_due = update_data.get("due_date", hw.due_date)
    if new_due < new_assigned:
        raise HTTPException(status_code=400, detail="截止日期不能早于布置日期")

    for k, v in update_data.items():
        setattr(hw, k, v)
    db.commit()
    db.refresh(hw)
    return hw


@router.delete("/{homework_id}", response_model=MessageResponse)
def delete_homework(
    homework_id: int,
    current_user: User = Depends(require_role(RoleEnum.commissary)),
    db: Session = Depends(get_db),
):
    hw = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.class_id == current_user.class_id,
    ).first()
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    db.delete(hw)
    db.commit()
    return MessageResponse(message="作业已删除")
