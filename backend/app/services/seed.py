from datetime import datetime, timezone
import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_password
from app.models import Execution, ExecutionLog, IntegrationConnection, User, Workflow, WorkflowStep


def seed_demo_data(db: Session) -> None:
    user = db.scalar(select(User).where(User.email == settings.demo_email))
    legacy_user = db.scalar(select(User).where(User.email == "demo@syncraft.local"))
    if not user and legacy_user:
        # Upgrade Docker volumes created by older portfolio builds instead of
        # forcing the user to delete their database volume.
        legacy_user.email = settings.demo_email
        user = legacy_user
        db.commit()
    if not user:
        user = User(email=settings.demo_email, full_name="Nikita", password_hash=hash_password(settings.demo_password), is_admin=True)
        db.add(user)
        db.flush()
    else:
        # Keep the documented local demo credentials reliable across rebuilds
        # even when a Docker volume from an older portfolio build already exists.
        user.full_name = "Nikita"
        user.password_hash = hash_password(settings.demo_password)
        user.is_admin = True
        db.commit()

    if db.scalar(select(Workflow).where(Workflow.owner_id == user.id)):
        return

    demos = [
        ("Shop Order Processing", "Receive an order, normalize the payload and create an audit event.", "webhook", [
            ("trigger", "Incoming order", {"source": "webhook"}),
            ("transform", "Normalize order", {"set": {"processed_by": "Syncraft", "priority": "normal"}}),
            ("log", "Audit event", {"message": "Order processed successfully"}),
        ]),
        ("Daily Data Sync", "Prepare a daily sync payload and keep a detailed execution trail.", "schedule", [
            ("trigger", "Every 60 minutes", {"source": "schedule"}),
            ("transform", "Add sync metadata", {"set": {"sync": True, "source": "scheduled"}}),
            ("delay", "Small processing delay", {"milliseconds": 150}),
            ("log", "Sync complete", {"message": "Data sync pipeline completed"}),
        ]),
        ("Telegram Alert", "Format an alert payload for a Telegram notification step.", "manual", [
            ("trigger", "Manual trigger", {"source": "manual"}),
            ("transform", "Build alert", {"set": {"severity": "info"}}),
            ("telegram", "Send Telegram message", {"message": "Syncraft demo alert: {{message}}"}),
        ]),
    ]

    for index, (name, desc, trigger, steps) in enumerate(demos):
        wf = Workflow(owner_id=user.id, name=name, description=desc, trigger_type=trigger, active=True,
                      webhook_token=secrets.token_urlsafe(24), schedule_minutes=60 if trigger == "schedule" else None)
        db.add(wf); db.flush()
        for pos, (step_type, step_name, config) in enumerate(steps):
            db.add(WorkflowStep(workflow_id=wf.id, position=pos, step_type=step_type, name=step_name, config=config))
        for eindex in range(3 if index == 0 else 2):
            status = "failed" if index == 2 and eindex == 0 else "success"
            ex = Execution(workflow_id=wf.id, trigger=trigger, status=status, duration_ms=840 + index * 520 + eindex * 120,
                           input_data={"demo": True}, output_data={"ok": status == "success"},
                           error_message="Telegram connection is not configured" if status == "failed" else "",
                           finished_at=datetime.now(timezone.utc))
            db.add(ex); db.flush()
            db.add(ExecutionLog(execution_id=ex.id, step_name="Syncraft", level="error" if status == "failed" else "info",
                                message=ex.error_message or "Execution completed", payload={"demo": True}))

    providers = [
        ("telegram", "Telegram", "Send messages and alerts to Telegram chats."),
        ("discord", "Discord", "Post workflow notifications to Discord channels."),
        ("github", "GitHub", "React to repository events and automate developer workflows."),
        ("google_sheets", "Google Sheets", "Move structured data into spreadsheet workflows."),
        ("notion", "Notion", "Create pages and records from automated workflows."),
        ("generic_http", "HTTP API", "Connect any REST API using the built-in HTTP step."),
    ]
    for provider, label, _ in providers:
        db.add(IntegrationConnection(owner_id=user.id, provider=provider, display_name=label, connected=provider == "generic_http", config={}))
    db.commit()
