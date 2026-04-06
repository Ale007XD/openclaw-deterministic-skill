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

    Ограничение: параллельные tool_calls (len > 1) не поддерживаются.
    FSM допускает не более одного pending_tool_call одновременно.
    При получении нескольких tool_calls в одном ответе поднимается
    NotImplementedError — это предпочтительнее необработанного ValueError
    из delta на второй итерации.
    """

    # D3: guard — FSM не поддерживает параллельные tool_calls
    if len(response.tool_calls) > 1:
        names = [c.tool_name for c in response.tool_calls]
        raise NotImplementedError(
            f"Parallel tool_calls not supported (got {len(response.tool_calls)}:"
            f" {names}). FSM allows at most one pending_tool_call."
        )

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
