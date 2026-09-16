import asyncio
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, dashboard, executions, health, integrations, templates, webhooks, workflows
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.scheduler import scheduler_loop
from app.services.seed import seed_demo_data
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo_data(db)
    stop_event = asyncio.Event()
    task = asyncio.create_task(scheduler_loop(stop_event))
    yield
    stop_event.set()
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


app = FastAPI(title=settings.app_name, version="1.2.0", description="Workflow automation & API integration platform", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
for router in [health.router, auth.router, workflows.router, executions.router, dashboard.router, integrations.router, templates.router, webhooks.router]:
    app.include_router(router)
