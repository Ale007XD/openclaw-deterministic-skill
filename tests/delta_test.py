from skill.models import StateContext
from skill.events import Event
from skill.delta import step


def test_delta():
    s = StateContext()

    e = Event(type="user_input", payload={"text": "hi"})
    s2 = step(s, e)

    assert s2.messages[-1]["content"] == "hi"
    assert s2.state == "processing"


test_delta()
