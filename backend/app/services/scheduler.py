from __future__ import annotations
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Workflow
from app.services.engine import execute_workflow


async def scheduler_loop(stop_event: asyncio.Event):
    while not stop_event.is_set():
        with SessionLocal() as db:
            now = datetime.now(timezone.utc)
            workflows = db.scalars(select(Workflow).where(Workflow.active.is_(True), Workflow.trigger_type == "schedule", Workflow.schedule_minutes.is_not(None))).all()
            for workflow in workflows:
                last = workflow.last_scheduled_at
                if last is not None and last.tzinfo is None:
                    last = last.replace(tzinfo=timezone.utc)
                due = not last or now - last >= timedelta(minutes=workflow.schedule_minutes or 60)
                if due:
                    workflow.last_scheduled_at = now
                    db.commit()
                    await execute_workflow(db, workflow, {"scheduled_at": now.isoformat()}, trigger="schedule")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=30)
        except asyncio.TimeoutError:
            pass
