from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import time
import hashlib
import json


def compute_event_hash(
    type: str,
    payload: Dict[str, Any],
    causation_id: Optional[str]
) -> str:
    # детерминированная сериализация
    data = {
        "type": type,
        "payload": payload,
        "causation_id": causation_id,
    }

    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    payload: Dict[str, Any]

    metadata: Dict[str, Any] = Field(default_factory=dict)

    timestamp: float = Field(default_factory=lambda: time.time())
    source: str = "system"

    causation_id: Optional[str] = None
    correlation_id: Optional[str] = None

    # P0: детерминированный hash
    event_hash: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        # вычисляем только если не задан
        if self.event_hash is None:
            self.event_hash = compute_event_hash(
                self.type,
                self.payload,
                self.causation_id
            )
