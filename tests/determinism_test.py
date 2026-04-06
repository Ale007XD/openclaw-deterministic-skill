from skill.models import StateContext
from skill.events import Event
from skill.delta import step


def test_determinism():
    s = StateContext()
    e = Event(type="user_input", payload={"text": "x"})

    s1 = step(s, e)
    s2 = step(s, e)

    assert s1 == s2


test_determinism()
