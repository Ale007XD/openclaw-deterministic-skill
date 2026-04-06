from typing import List
from .events import Event
from .models import StateContext
from .delta import step


class EventLog:

    def __init__(self):
        self.events: List[Event] = []

    def append(self, event: Event):
        self.events.append(event)

    def replay(self, initial_state: StateContext) -> StateContext:
        state = initial_state
        for e in self.events:
            state = step(state, e)
        return state
