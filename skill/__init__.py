"""
OpenClaw Deterministic Skill — Core Package

Canonical public API.

Exports:
- StateContext      : FSM state container
- Event             : Fully specified event (with identity & causality)
- StepResult        : Canonical transition unit (S_t, E_t, S_{t+1})
- StepBuilder       : Controlled StepResult construction
- ExecutionEngine   : Stateless step runner
- EventLog          : Event sourcing + replay
"""

from .models import StateContext
from .events import Event
from .step_result import StepResult
from .step_builder import StepBuilder
from .engine import ExecutionEngine
from .event_log import EventLog
from .loop import run, LoopResult

__all__ = (
    "StateContext",
    "Event",
    "StepResult",
    "StepBuilder",
    "ExecutionEngine",
    "EventLog",
    "run",
    "LoopResult",
)
