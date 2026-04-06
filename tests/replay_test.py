from skill.models import StateContext
from skill.events import Event
from skill.event_log import EventLog


def test_replay():
    log = EventLog()

    e1 = Event(type="user_input", payload={"text": "hello"})
    e2 = Event(
        type="llm_response",
        payload={"text": "hi"},
        causation_id=e1.id,
        correlation_id=e1.id
    )

    log.append(e1)
    log.append(e2)

    final_state = log.replay(StateContext())

    assert len(final_state.messages) == 2


test_replay()
