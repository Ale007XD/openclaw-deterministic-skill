from .models import StateContext
from .events import Event
from .tool_merge import merge_tool_results


def step(state: StateContext, event: Event) -> StateContext:
    new_state = state.model_copy(deep=True)

    if event.type == "user_input":
        new_state.messages.append({
            "role": "user",
            "content": event.payload["text"]
        })
        new_state.state = "processing"

    elif event.type == "llm_response":
        new_state.messages.append({
            "role": "assistant",
            "content": event.payload["text"]
        })
        new_state.state = "idle"

    elif event.type == "tool_call":
        # guard: второй tool_call без tool_result — нарушение инварианта
        if new_state.pending_tool_call is not None:
            raise ValueError(
                f"tool_call while pending: "
                f"{new_state.pending_tool_call.get('tool_name')}"
            )
        new_state.pending_tool_call = event.payload
        new_state.state = "waiting_tool"

    elif event.type == "tool_result":
        # валидация соответствия tool_call → tool_result
        if new_state.pending_tool_call is None:
            raise ValueError("tool_result without pending_tool_call")

        expected_tool = new_state.pending_tool_call.get("tool_name")
        actual_tool = event.payload.get("tool_name")

        if expected_tool != actual_tool:
            raise ValueError(
                f"Tool mismatch: expected {expected_tool}, got {actual_tool}"
            )

        new_state.tool_results = merge_tool_results(
            new_state.tool_results + [event.payload]
        )
        new_state.pending_tool_call = None
        new_state.state = "processing"

    else:
        # P1: env больше не нужен — strict_mode живёт в StateContext
        if new_state.strict_mode:
            raise ValueError(f"Unknown event type: {event.type}")

    new_state.iteration += 1
    return new_state
