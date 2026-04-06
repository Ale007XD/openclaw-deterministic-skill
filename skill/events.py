from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import time


class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    payload: Dict[str, Any]

    metadata: Dict[str, Any] = Field(default_factory=dict)

    timestamp: float = Field(default_factory=lambda: time.time())
    source: str = "system"

    causation_id: Optional[str] = None
    correlation_id: Optional[str] = None
