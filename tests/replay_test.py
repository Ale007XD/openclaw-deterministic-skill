from skill.models import StateContext
from skill.events import Event
from skill.event_log import EventLog


def test_replay_basic():
    """Replay(E₀..Eₙ) = Sₙ — базовый случай."""
    log = EventLog()
    e1 = Event(type="user_input", payload={"text": "hello"})
    e2 = Event(type="llm_response", payload={"text": "hi"},
               causation_id=e1.id, correlation_id=e1.id)
    log.append(e1)
    log.append(e2)

    final = log.replay(StateContext())
    assert len(final.messages) == 2
    assert final.state == "idle"


def test_replay_idempotent():
    """Двойной replay одного лога даёт одинаковый результат."""
    log = EventLog()
    e1 = Event(type="user_input", payload={"text": "hello"})
    e2 = Event(type="llm_response", payload={"text": "hi"}, causation_id=e1.id)
    log.append(e1)
    log.append(e2)

    s1 = log.replay(StateContext())
    s2 = log.replay(StateContext())
    assert s1 == s2


def test_replay_tool_cycle():
    """Replay корректно воспроизводит полный tool_call → tool_result цикл."""
    log = EventLog()
    e1 = Event(type="user_input", payload={"text": "search"})
    e2 = Event(type="tool_call", payload={
        "tool_name": "search", "call_id": "c1", "arguments": {}
    }, causation_id=e1.id)
    e3 = Event(type="tool_result", payload={
        "tool_name": "search", "call_id": "c1", "result": "found"
    }, causation_id=e2.id)
    e4 = Event(type="llm_response", payload={"text": "here you go"},
               causation_id=e3.id)

    for e in [e1, e2, e3, e4]:
        log.append(e)

    final = log.replay(StateContext())
    assert final.state == "idle"
    assert len(final.messages) == 2
    assert len(final.tool_results) == 1
    assert final.pending_tool_call is None


test_replay_basic()
test_replay_idempotent()
test_replay_tool_cycle()
