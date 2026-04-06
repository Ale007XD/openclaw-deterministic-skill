from pydantic import BaseModel, Field
from typing import List, Dict, Any


class StateContext(BaseModel):
    state: str = "idle"
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    iteration: int = 0
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)
