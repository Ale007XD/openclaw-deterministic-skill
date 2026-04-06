from skill.events import Event


def test_causality_chain():
    """causation_id / correlation_id корректно связывают события."""
    e1 = Event(type="user_input", payload={"text": "hello"})
    e2 = Event(type="llm_response", payload={"text": "hi"},
               causation_id=e1.id, correlation_id=e1.id)

    assert e2.causation_id == e1.id
    assert e2.correlation_id == e1.id


def test_causation_affects_hash():
    """causation_id входит в event_hash — разные причины = разные события."""
    e1 = Event(type="llm_response", payload={"text": "hi"}, causation_id="aaa")
    e2 = Event(type="llm_response", payload={"text": "hi"}, causation_id="bbb")
    assert e1.event_hash != e2.event_hash


def test_no_causation_stable():
    """causation_id=None стабильно хэшируется."""
    e1 = Event(type="user_input", payload={"text": "x"}, causation_id=None)
    e2 = Event(type="user_input", payload={"text": "x"}, causation_id=None)
    assert e1.event_hash == e2.event_hash


test_causality_chain()
test_causation_affects_hash()
test_no_causation_stable()
