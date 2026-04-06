from .models import StateContext
from .events import Event
from .delta import step as delta
from .step_builder import StepBuilder
from .step_result import StepResult


class ExecutionEngine:

    def step(self, state: StateContext, event: Event) -> StepResult:
        new_state = delta(state, event)
        return StepBuilder.build(state, event, new_state)
