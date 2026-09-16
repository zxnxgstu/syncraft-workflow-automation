from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import IntegrationConnection, User
from app.schemas.integration import IntegrationOut, IntegrationUpdate

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

CATALOG = {
    "telegram": ("Telegram", "Send messages and alerts to Telegram chats.", "Messaging", "Bot token + chat ID"),
    "discord": ("Discord", "Post workflow notifications to Discord channels.", "Messaging", "Webhook URL"),
    "github": ("GitHub", "React to repository events and automate developer workflows.", "Developer", "Personal access token"),
    "google_sheets": ("Google Sheets", "Move structured data into spreadsheet workflows.", "Productivity", "OAuth connection"),
    "notion": ("Notion", "Create pages and records from automated workflows.", "Productivity", "Integration token"),
    "generic_http": ("HTTP API", "Connect any REST API using the built-in HTTP step.", "Developer", "No connection required"),
}


def serialize(record: IntegrationConnection) -> IntegrationOut:
    name, desc, category, hint = CATALOG[record.provider]
    return IntegrationOut(provider=record.provider, display_name=name, description=desc, category=category,
                          connected=record.connected, status_text="Connected" if record.connected else "Not connected", config_hint=hint)


@router.get("", response_model=list[IntegrationOut])
def list_integrations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    records = {r.provider: r for r in db.scalars(select(IntegrationConnection).where(IntegrationConnection.owner_id == user.id)).all()}
    result=[]
    for provider, (label, *_rest) in CATALOG.items():
        record = records.get(provider)
        if not record:
            record = IntegrationConnection(owner_id=user.id, provider=provider, display_name=label, connected=provider == "generic_http", config={})
            db.add(record); db.flush()
        result.append(serialize(record))
    db.commit(); return result


@router.put("/{provider}", response_model=IntegrationOut)
def update_integration(provider: str, payload: IntegrationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if provider not in CATALOG: raise HTTPException(status_code=404, detail="Integration not found")
    record = db.scalar(select(IntegrationConnection).where(IntegrationConnection.owner_id == user.id, IntegrationConnection.provider == provider))
    if not record:
        record = IntegrationConnection(owner_id=user.id, provider=provider, display_name=CATALOG[provider][0]); db.add(record)
    record.connected = payload.connected; record.config = payload.config
    db.commit(); db.refresh(record); return serialize(record)
