from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ToolCall(BaseModel):
    tool_name: str
    call_id: str
    arguments: Dict[str, Any]


class ProviderResponse(BaseModel):
    """
    Normalized provider output.
    NO raw strings allowed outside this structure.
    """

    text: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)

    raw: Dict[str, Any] = Field(default_factory=dict)
