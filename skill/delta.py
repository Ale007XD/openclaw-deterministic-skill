from .models import StateContext
from .events import Event
from .config import STRICT_MODE
from .tool_merge import merge_tool_results


def step(state: StateContext, event: Event) -> StateContext:
    new_state = state.model_copy(deep=True)

    if event.type == "user_input":
        new_state.messages.append({"role": "user", "content": event.payload["text"]})
        new_state.state = "processing"

    elif event.type == "llm_response":
        new_state.messages.append({"role": "assistant", "content": event.payload["text"]})
        new_state.state = "idle"

    elif event.type == "tool_result":
        new_state.tool_results = merge_tool_results(
            new_state.tool_results + [event.payload]
        )
        new_state.state = "processing"

    else:
        if STRICT_MODE:
            raise ValueError(f"Unknown event type: {event.type}")

    new_state.iteration += 1
    return new_state
