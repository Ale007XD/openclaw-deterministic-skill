from skill.events import Event


def test_causality_chain():
    e1 = Event(type="user_input", payload={"text": "hello"})
    e2 = Event(
        type="llm_response",
        payload={"text": "hi"},
        causation_id=e1.id,
        correlation_id=e1.id
    )

    assert e2.causation_id == e1.id
    assert e2.correlation_id == e1.id


test_causality_chain()
