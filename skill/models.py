from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class StateContext(BaseModel):
    schema_version: int = 1

    state: str = "idle"
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    iteration: int = 0
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)

    # P0: фиксируем ожидаемый tool_call
    pending_tool_call: Optional[Dict[str, Any]] = None

    # P1: strict_mode в состоянии — δ больше не зависит от env
    # False = неизвестные event.type игнорируются молча
    strict_mode: bool = True
