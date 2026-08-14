"""科目路由：查看、添加、修改、删除、初始化预置"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Subject, RoleEnum
from ..schemas import SubjectCreate, SubjectUpdate, SubjectOut, MessageResponse
from ..auth import get_current_user, require_role
from ..config import PRESET_SUBJECTS

router = APIRouter(prefix="/api/subjects", tags=["科目"])


@router.get("", response_model=List[SubjectOut])
def list_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Subject).filter(Subject.class_id == current_user.class_id).all()


@router.post("", response_model=SubjectOut, status_code=201)
def create_subject(
    req: SubjectCreate,
    current_user: User = Depends(require_role(RoleEnum.commissary)),
    db: Session = Depends(get_db),
):
    exists = db.query(Subject).filter(
        Subject.class_id == current_user.class_id,
        Subject.name == req.name,
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="该科目已存在")
    subject = Subject(class_id=current_user.class_id, **req.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    req: SubjectUpdate,
    current_user: User = Depends(require_role(RoleEnum.commissary)),
    db: Session = Depends(get_db),
):
    """修改科目属性（名称、颜色、图标均支持自定义）"""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.class_id == current_user.class_id,
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在")

    update_data = req.model_dump(exclude_unset=True)
    # 若改了名称，检查重名
    if "name" in update_data and update_data["name"] != subject.name:
        dup = db.query(Subject).filter(
            Subject.class_id == current_user.class_id,
            Subject.name == update_data["name"],
        ).first()
        if dup:
            raise HTTPException(status_code=400, detail="该科目名称已存在")

    for k, v in update_data.items():
        setattr(subject, k, v)
    db.commit()
    db.refresh(subject)
    return subject


@router.post("/init-preset", response_model=MessageResponse)
def init_preset_subjects(
    current_user: User = Depends(require_role(RoleEnum.commissary)),
    db: Session = Depends(get_db),
):
    created = []
    for item in PRESET_SUBJECTS:
        exists = db.query(Subject).filter(
            Subject.class_id == current_user.class_id,
            Subject.name == item["name"],
        ).first()
        if not exists:
            db.add(Subject(class_id=current_user.class_id, **item))
            created.append(item["name"])
    db.commit()
    return MessageResponse(
        message=f"已初始化 {len(created)} 门预置科目",
        detail=f"新增：{', '.join(created) if created else '无（均已存在）'}",
    )


@router.delete("/{subject_id}", response_model=MessageResponse)
def delete_subject(
    subject_id: int,
    current_user: User = Depends(require_role(RoleEnum.commissary)),
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.class_id == current_user.class_id,
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在")
    db.delete(subject)
    db.commit()
    return MessageResponse(message="科目已删除")
