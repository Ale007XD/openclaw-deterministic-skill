from skill.models import StateContext
from skill.events import Event
from skill.delta import step


def test_user_input():
    s = StateContext()
    e = Event(type="user_input", payload={"text": "hi"})
    s2 = step(s, e)
    assert s2.messages[-1]["content"] == "hi"
    assert s2.state == "processing"


def test_tool_cycle():
    """tool_call → tool_result: полный цикл, pending очищается."""
    s = StateContext()
    s = step(s, Event(type="user_input", payload={"text": "go"}))
    s = step(s, Event(type="tool_call", payload={
        "tool_name": "search", "call_id": "c1", "arguments": {}
    }))
    assert s.state == "waiting_tool"
    assert s.pending_tool_call is not None

    s = step(s, Event(type="tool_result", payload={
        "tool_name": "search", "call_id": "c1", "result": "ok"
    }))
    assert s.state == "processing"
    assert s.pending_tool_call is None
    assert len(s.tool_results) == 1


def test_tool_result_without_pending_raises():
    """tool_result без предшествующего tool_call — ValueError."""
    s = StateContext()
    try:
        step(s, Event(type="tool_result", payload={
            "tool_name": "search", "call_id": "c1"
        }))
        assert False, "должен был упасть"
    except ValueError as e:
        assert "without pending" in str(e)


def test_tool_mismatch_raises():
    """tool_result с другим tool_name — ValueError."""
    s = StateContext()
    s = step(s, Event(type="user_input", payload={"text": "x"}))
    s = step(s, Event(type="tool_call", payload={
        "tool_name": "search", "call_id": "c1", "arguments": {}
    }))
    try:
        step(s, Event(type="tool_result", payload={
            "tool_name": "OTHER", "call_id": "c1"
        }))
        assert False, "должен был упасть"
    except ValueError as e:
        assert "mismatch" in str(e).lower()


def test_double_tool_call_raises():
    """Второй tool_call без tool_result между ними — ValueError."""
    s = StateContext()
    s = step(s, Event(type="user_input", payload={"text": "x"}))
    s = step(s, Event(type="tool_call", payload={
        "tool_name": "search", "call_id": "c1", "arguments": {}
    }))
    try:
        step(s, Event(type="tool_call", payload={
            "tool_name": "calc", "call_id": "c2", "arguments": {}
        }))
        assert False, "должен был упасть"
    except ValueError as e:
        assert "pending" in str(e)


def test_unknown_event_strict():
    """Неизвестный тип в strict_mode=True — ValueError."""
    s = StateContext(strict_mode=True)
    try:
        step(s, Event(type="unknown_type", payload={}))
        assert False, "должен был упасть"
    except ValueError:
        pass


def test_unknown_event_lenient():
    """Неизвестный тип в strict_mode=False — игнорируется, iteration растёт."""
    s = StateContext(strict_mode=False)
    s2 = step(s, Event(type="unknown_type", payload={}))
    assert s2.iteration == 1


test_user_input()
test_tool_cycle()
test_tool_result_without_pending_raises()
test_tool_mismatch_raises()
test_double_tool_call_raises()
test_unknown_event_strict()
test_unknown_event_lenient()
