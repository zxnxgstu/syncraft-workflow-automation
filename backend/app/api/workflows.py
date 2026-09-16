import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User, Workflow, WorkflowStep
from app.schemas.workflow import WorkflowCreate, WorkflowOut, WorkflowUpdate

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


def owned_query(user_id: int):
    return select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.owner_id == user_id)


def get_owned(db: Session, user: User, workflow_id: int) -> Workflow:
    workflow = db.scalar(owned_query(user.id).where(Workflow.id == workflow_id))
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


def replace_steps(db: Session, workflow: Workflow, steps):
    workflow.steps.clear(); db.flush()
    for index, step in enumerate(steps):
        db.add(WorkflowStep(workflow_id=workflow.id, position=index, step_type=step.step_type, name=step.name, config=step.config))


@router.get("", response_model=list[WorkflowOut])
def list_workflows(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(owned_query(user.id).order_by(Workflow.updated_at.desc())).all()


@router.post("", response_model=WorkflowOut, status_code=status.HTTP_201_CREATED)
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workflow = Workflow(owner_id=user.id, name=payload.name, description=payload.description, trigger_type=payload.trigger_type,
                        active=payload.active, schedule_minutes=payload.schedule_minutes, webhook_token=secrets.token_urlsafe(24))
    db.add(workflow); db.flush(); replace_steps(db, workflow, payload.steps); db.commit()
    return get_owned(db, user, workflow.id)


@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow(workflow_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_owned(db, user, workflow_id)


@router.patch("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(workflow_id: int, payload: WorkflowUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workflow = get_owned(db, user, workflow_id)
    data = payload.model_dump(exclude_unset=True, exclude={"steps"})
    for key, value in data.items(): setattr(workflow, key, value)
    if payload.steps is not None: replace_steps(db, workflow, payload.steps)
    db.commit()
    return get_owned(db, user, workflow_id)


@router.post("/{workflow_id}/clone", response_model=WorkflowOut, status_code=201)
def clone_workflow(workflow_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    source = get_owned(db, user, workflow_id)
    clone = Workflow(owner_id=user.id, name=f"{source.name} Copy", description=source.description, trigger_type=source.trigger_type,
                     active=False, schedule_minutes=source.schedule_minutes, webhook_token=secrets.token_urlsafe(24))
    db.add(clone); db.flush()
    for step in source.steps:
        db.add(WorkflowStep(workflow_id=clone.id, position=step.position, step_type=step.step_type, name=step.name, config=step.config))
    db.commit(); return get_owned(db, user, clone.id)


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workflow = get_owned(db, user, workflow_id); db.delete(workflow); db.commit()
