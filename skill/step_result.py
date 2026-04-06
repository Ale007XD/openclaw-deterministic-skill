from pydantic import BaseModel
from typing import Dict, Any
from .models import StateContext
from .events import Event


class StepResult(BaseModel):
    state_before: StateContext
    event: Event
    state_after: StateContext
    metadata: Dict[str, Any] = {}
