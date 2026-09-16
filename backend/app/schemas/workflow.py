from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class StepIn(BaseModel):
    id: int | None = None
    position: int = 0
    step_type: str = Field(pattern="^(trigger|transform|http|log|delay|telegram)$")
    name: str = Field(min_length=1, max_length=120)
    config: dict[str, Any] = Field(default_factory=dict)


class StepOut(StepIn):
    id: int
    model_config = {"from_attributes": True}


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=1000)
    trigger_type: str = Field(default="manual", pattern="^(manual|webhook|schedule)$")
    active: bool = True
    schedule_minutes: int | None = Field(default=None, ge=1, le=10080)
    steps: list[StepIn] = Field(default_factory=list)


class WorkflowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    trigger_type: str | None = Field(default=None, pattern="^(manual|webhook|schedule)$")
    active: bool | None = None
    schedule_minutes: int | None = Field(default=None, ge=1, le=10080)
    steps: list[StepIn] | None = None


class WorkflowOut(BaseModel):
    id: int
    name: str
    description: str
    trigger_type: str
    active: bool
    webhook_token: str
    schedule_minutes: int | None
    created_at: datetime
    updated_at: datetime
    steps: list[StepOut]
    model_config = {"from_attributes": True}


class ExecuteRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class ExecutionLogOut(BaseModel):
    id: int
    step_name: str
    level: str
    message: str
    payload: dict[str, Any]
    created_at: datetime
    model_config = {"from_attributes": True}


class ExecutionOut(BaseModel):
    id: int
    workflow_id: int
    workflow_name: str | None = None
    trigger: str
    status: str
    duration_ms: int
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    error_message: str
    started_at: datetime
    finished_at: datetime | None
    logs: list[ExecutionLogOut] = Field(default_factory=list)
