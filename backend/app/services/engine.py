from __future__ import annotations
import asyncio
import re
import time
from datetime import datetime, timezone
from typing import Any
import httpx
from sqlalchemy.orm import Session
from app.models import Execution, ExecutionLog, Workflow

TEMPLATE_RE = re.compile(r"{{\s*([\w.]+)\s*}}")


def _lookup(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return ""
        current = current.get(part, "")
    return current


def render(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return TEMPLATE_RE.sub(lambda m: str(_lookup(context, m.group(1))), value)
    if isinstance(value, dict):
        return {k: render(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [render(v, context) for v in value]
    return value


def add_log(db: Session, execution: Execution, step_name: str, message: str, payload: dict | None = None, level: str = "info"):
    log = ExecutionLog(execution_id=execution.id, step_name=step_name, level=level, message=message, payload=payload or {})
    db.add(log); db.flush()


async def execute_workflow(db: Session, workflow: Workflow, payload: dict[str, Any], trigger: str = "manual") -> Execution:
    start = time.perf_counter()
    execution = Execution(workflow_id=workflow.id, trigger=trigger, status="running", input_data=payload, output_data={})
    db.add(execution); db.flush()
    context: dict[str, Any] = dict(payload)
    add_log(db, execution, "Trigger", f"Workflow started via {trigger}", {"input": payload})
    try:
        for step in sorted(workflow.steps, key=lambda s: s.position):
            cfg = render(step.config or {}, context)
            if step.step_type == "trigger":
                add_log(db, execution, step.name, "Trigger accepted")
                continue
            if step.step_type == "transform":
                additions = cfg.get("set", {})
                if not isinstance(additions, dict):
                    raise ValueError("Transform step requires a 'set' object")
                context.update(additions)
                add_log(db, execution, step.name, "Data transformed", {"set": additions})
            elif step.step_type == "log":
                message = str(cfg.get("message", "Workflow log"))
                add_log(db, execution, step.name, message, {"context": context})
            elif step.step_type == "delay":
                milliseconds = max(0, min(int(cfg.get("milliseconds", 100)), 3000))
                await asyncio.sleep(milliseconds / 1000)
                add_log(db, execution, step.name, f"Waited {milliseconds} ms")
            elif step.step_type == "http":
                url = str(cfg.get("url", ""))
                if not url.startswith(("http://", "https://")):
                    raise ValueError("HTTP step requires an http:// or https:// URL")
                method = str(cfg.get("method", "GET")).upper()
                headers = cfg.get("headers", {}) if isinstance(cfg.get("headers", {}), dict) else {}
                body = cfg.get("body", context)
                timeout = float(cfg.get("timeout", 8))
                async with httpx.AsyncClient(timeout=min(max(timeout, 1), 20), follow_redirects=True) as client:
                    response = await client.request(method, url, headers=headers, json=body if method not in {"GET", "HEAD"} else None)
                    response.raise_for_status()
                    ctype = response.headers.get("content-type", "")
                    result = response.json() if "application/json" in ctype else {"text": response.text[:2000]}
                    context["http"] = {"status": response.status_code, "data": result}
                    add_log(db, execution, step.name, f"HTTP {method} returned {response.status_code}", {"url": url})
            elif step.step_type == "telegram":
                # Portfolio-friendly behavior: a real Telegram call can be made if both values are supplied.
                bot_token = str(cfg.get("bot_token", "")).strip()
                chat_id = str(cfg.get("chat_id", "")).strip()
                message = str(cfg.get("message", "Syncraft notification"))
                if bot_token and chat_id:
                    async with httpx.AsyncClient(timeout=10) as client:
                        response = await client.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": message})
                        response.raise_for_status()
                    add_log(db, execution, step.name, "Telegram message sent")
                else:
                    context["telegram_preview"] = message
                    add_log(db, execution, step.name, "Telegram step ran in preview mode (credentials not configured)", {"preview": message})
            else:
                raise ValueError(f"Unsupported step type: {step.step_type}")

        execution.status = "success"
        execution.output_data = context
        add_log(db, execution, "Syncraft", "Workflow completed successfully", {"output": context})
    except Exception as exc:
        execution.status = "failed"
        execution.error_message = str(exc)
        execution.output_data = context
        add_log(db, execution, "Syncraft", f"Execution failed: {exc}", level="error")
    finally:
        execution.duration_ms = int((time.perf_counter() - start) * 1000)
        execution.finished_at = datetime.now(timezone.utc)
        db.commit(); db.refresh(execution)
    return execution
