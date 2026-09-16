from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Execution, User, Workflow
from app.schemas.workflow import ExecuteRequest, ExecutionOut
from app.services.engine import execute_workflow

router = APIRouter(prefix="/api/v1/executions", tags=["executions"])


def execution_to_out(execution: Execution) -> ExecutionOut:
    return ExecutionOut.model_validate({
        "id": execution.id, "workflow_id": execution.workflow_id, "workflow_name": execution.workflow.name if execution.workflow else None,
        "trigger": execution.trigger, "status": execution.status, "duration_ms": execution.duration_ms,
        "input_data": execution.input_data or {}, "output_data": execution.output_data or {}, "error_message": execution.error_message,
        "started_at": execution.started_at, "finished_at": execution.finished_at, "logs": execution.logs,
    })


@router.get("", response_model=list[ExecutionOut])
def list_executions(limit: int = 50, status: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = (select(Execution).join(Workflow).options(selectinload(Execution.logs), selectinload(Execution.workflow))
             .where(Workflow.owner_id == user.id).order_by(Execution.started_at.desc()).limit(min(max(limit, 1), 200)))
    if status: query = query.where(Execution.status == status)
    return [execution_to_out(item) for item in db.scalars(query).unique().all()]


@router.get("/{execution_id}", response_model=ExecutionOut)
def get_execution(execution_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ex = db.scalar(select(Execution).join(Workflow).options(selectinload(Execution.logs), selectinload(Execution.workflow))
                   .where(Execution.id == execution_id, Workflow.owner_id == user.id))
    if not ex: raise HTTPException(status_code=404, detail="Execution not found")
    return execution_to_out(ex)


@router.post("/workflow/{workflow_id}/run", response_model=ExecutionOut)
async def run_workflow(workflow_id: int, payload: ExecuteRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    wf = db.scalar(select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.id == workflow_id, Workflow.owner_id == user.id))
    if not wf: raise HTTPException(status_code=404, detail="Workflow not found")
    ex = await execute_workflow(db, wf, payload.payload, trigger="manual")
    ex = db.scalar(select(Execution).options(selectinload(Execution.logs), selectinload(Execution.workflow)).where(Execution.id == ex.id))
    return execution_to_out(ex)
