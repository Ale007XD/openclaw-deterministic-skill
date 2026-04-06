from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import time
import hashlib
import json


def compute_event_hash(
    type: str,
    payload: Dict[str, Any],
    causation_id: Optional[str],
) -> str:
    """
    Детерминированный хэш события.
    Исключает нестабильные поля: id, timestamp, metadata, source.
    sort_keys=True рекурсивен — порядок ключей в payload не влияет.
    """
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

    event_hash: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if self.event_hash is None:
            self.event_hash = compute_event_hash(
                self.type,
                self.payload,
                self.causation_id,
            )

    def __eq__(self, other: object) -> bool:
        """
        Семантическое равенство по event_hash.
        id и timestamp намеренно исключены — они транспортные, не смысловые.
        """
        if not isinstance(other, Event):
            return NotImplemented
        return self.event_hash == other.event_hash

    def __hash__(self) -> int:
        return hash(self.event_hash)
