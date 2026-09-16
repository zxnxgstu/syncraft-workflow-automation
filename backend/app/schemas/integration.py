from pydantic import BaseModel, Field
from typing import Any


class IntegrationUpdate(BaseModel):
    connected: bool
    config: dict[str, Any] = Field(default_factory=dict)


class IntegrationOut(BaseModel):
    provider: str
    display_name: str
    description: str
    category: str
    connected: bool
    status_text: str
    config_hint: str
