from .step_result import StepResult
from .models import StateContext
from .events import Event


class StepBuilder:

    @staticmethod
    def build(
        state_before: StateContext,
        event: Event,
        state_after: StateContext,
        metadata: dict = None,
    ) -> StepResult:
        return StepResult(
            state_before=state_before,
            event=event,
            state_after=state_after,
            metadata=metadata or {},
        )
