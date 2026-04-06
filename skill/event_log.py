from typing import List
from .events import Event
from .models import StateContext
from .delta import step

# Версии схемы, которые replay умеет воспроизводить.
# При добавлении миграционного кода — расширять этот набор.
_SUPPORTED_SCHEMA_VERSIONS: frozenset = frozenset({1})


class EventLog:

    def __init__(self):
        self.events: List[Event] = []

    def append(self, event: Event):
        self.events.append(event)

    def replay(self, initial_state: StateContext) -> StateContext:
        """
        Воспроизводит лог событий поверх initial_state.

        Поднимает ValueError если schema_version initial_state не поддерживается —
        это предотвращает молчаливое применение старых событий к несовместимой схеме.
        """
        # D1: schema_version guard
        if initial_state.schema_version not in _SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(
                f"Unsupported schema_version: {initial_state.schema_version}. "
                f"Supported: {sorted(_SUPPORTED_SCHEMA_VERSIONS)}"
            )
        state = initial_state
        for e in self.events:
            state = step(state, e)
        return state
