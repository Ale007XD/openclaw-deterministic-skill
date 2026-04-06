from typing import List
from ..events import Event
from .provider_response import ProviderResponse


def map_response_to_events(
    response: ProviderResponse,
    causation_id: str,
    correlation_id: str,
) -> List[Event]:
    """
    Deterministic mapping:
    ProviderResponse → List[Event]
    """

    events: List[Event] = []

    # 1. LLM text → llm_response
    if response.text:
        events.append(
            Event(
                type="llm_response",
                payload={"text": response.text},
                source="llm",
                causation_id=causation_id,
                correlation_id=correlation_id,
            )
        )

    # 2. Tool calls → tool_call events
    for call in response.tool_calls:
        events.append(
            Event(
                type="tool_call",
                payload={
                    "tool_name": call.tool_name,
                    "call_id": call.call_id,
                    "arguments": call.arguments,
                },
                source="llm",
                causation_id=causation_id,
                correlation_id=correlation_id,
            )
        )

    return events
