from skill.models import StateContext
from skill.events import Event
from skill.delta import step


def test_hash_stable_across_instances():
    """Два независимых Event с одинаковым содержимым — event_hash совпадает."""
    e1 = Event(type="user_input", payload={"text": "x"})
    e2 = Event(type="user_input", payload={"text": "x"})
    assert e1.id != e2.id           # транспортные поля разные
    assert e1.event_hash == e2.event_hash  # семантика одинакова


def test_event_eq_by_hash():
    """Event.__eq__ работает по event_hash, не по id/timestamp."""
    e1 = Event(type="user_input", payload={"text": "x"})
    e2 = Event(type="user_input", payload={"text": "x"})
    assert e1 == e2


def test_event_neq_different_payload():
    """Разные payload — разные события."""
    e1 = Event(type="user_input", payload={"text": "x"})
    e2 = Event(type="user_input", payload={"text": "y"})
    assert e1 != e2


def test_payload_key_order_invariant():
    """Порядок ключей в payload не влияет на event_hash."""
    e1 = Event(type="tool_call", payload={"b": 2, "a": 1})
    e2 = Event(type="tool_call", payload={"a": 1, "b": 2})
    assert e1.event_hash == e2.event_hash


def test_nested_key_order_invariant():
    """sort_keys рекурсивен — вложенные dict тоже стабильны."""
    e1 = Event(type="tool_call", payload={"args": {"z": 9, "a": 1}})
    e2 = Event(type="tool_call", payload={"args": {"a": 1, "z": 9}})
    assert e1.event_hash == e2.event_hash


def test_step_deterministic():
    """δ(S, E) = δ(S, E) для двух независимых E с одинаковым содержимым."""
    s = StateContext()
    e1 = Event(type="user_input", payload={"text": "x"})
    e2 = Event(type="user_input", payload={"text": "x"})
    s1 = step(s, e1)
    s2 = step(s, e2)
    assert s1 == s2


test_hash_stable_across_instances()
test_event_eq_by_hash()
test_event_neq_different_payload()
test_payload_key_order_invariant()
test_nested_key_order_invariant()
test_step_deterministic()
