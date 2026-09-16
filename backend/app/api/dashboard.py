from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Execution, User, Workflow

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    completed = db.execute(
        select(Execution.id, Execution.status, Execution.duration_ms, Execution.started_at)
        .join(Workflow)
        .where(Workflow.owner_id == user.id, Execution.status.in_(("success", "failed")))
        .order_by(Execution.started_at.asc())
    ).all()
    success = sum(row.status == "success" for row in completed)
    failed = sum(row.status == "failed" for row in completed)
    total = success + failed
    average = sum(row.duration_ms for row in completed) / total if total else 0
    workflows = db.scalar(select(func.count()).select_from(Workflow).where(Workflow.owner_id == user.id)) or 0
    active = db.scalar(select(func.count()).select_from(Workflow).where(Workflow.owner_id == user.id, Workflow.active.is_(True))) or 0
    recent = db.execute(select(Execution.id, Execution.status, Execution.duration_ms, Execution.started_at, Workflow.name)
                        .join(Workflow).where(Workflow.owner_id == user.id, Execution.status.in_(("success", "failed")))
                        .order_by(Execution.started_at.desc()).limit(8)).all()
    daily: dict[str, dict[str, int | str]] = {}
    for row in completed:
        day = str(row.started_at.date())
        bucket = daily.setdefault(day, {"day": day, "success": 0, "failed": 0})
        bucket[row.status] = int(bucket[row.status]) + 1
    return {
        "metrics": {"total_executions": total, "success_executions": success,
                    "success_rate": round((success / total * 100) if total else 0, 1),
                    "failed_executions": failed, "average_duration_ms": int(average), "workflows": workflows, "active_workflows": active},
        "recent_executions": [{"id": r.id, "workflow_name": r.name, "status": r.status, "duration_ms": r.duration_ms, "started_at": r.started_at} for r in recent],
        "chart": list(daily.values()),
        # Raw timestamps let the client group by the viewer's local calendar day/hour
        # without inventing missing history or introducing timezone boundary errors.
        "execution_activity": [{"id": r.id, "status": r.status, "started_at": r.started_at} for r in completed],
    }
