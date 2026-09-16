from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.db.session import get_db
from app.models import Workflow
from app.services.engine import execute_workflow

router = APIRouter(prefix="/api/v1/hooks", tags=["webhooks"])


@router.post("/{token}")
async def receive_webhook(token: str, request: Request, db: Session = Depends(get_db)):
    wf = db.scalar(select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.webhook_token == token, Workflow.active.is_(True)))
    if not wf: raise HTTPException(status_code=404, detail="Webhook not found")
    try: payload = await request.json()
    except Exception: payload = {"raw": (await request.body()).decode(errors="replace")}
    ex = await execute_workflow(db, wf, payload if isinstance(payload, dict) else {"data": payload}, trigger="webhook")
    return {"accepted": True, "execution_id": ex.id, "status": ex.status}
