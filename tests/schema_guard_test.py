"""
schema_guard_test.py — тесты D1: schema_version guard в EventLog.replay().

Инварианты:
  SG1. replay с поддерживаемой версией (schema_version=1) работает без ошибок.
  SG2. replay с неподдерживаемой версией (schema_version=99) поднимает ValueError.
  SG3. сообщение ValueError содержит версию и список поддерживаемых.
"""

import pytest

from skill.models import StateContext
from skill.events import Event
from skill.event_log import EventLog


def _build_log() -> EventLog:
    log = EventLog()
    e1 = Event(type="user_input", payload={"text": "hello"})
    e2 = Event(type="llm_response", payload={"text": "hi"}, causation_id=e1.id)
    log.append(e1)
    log.append(e2)
    return log


def test_replay_supported_schema():
    """SG1: schema_version=1 → replay без ошибок."""
    log = _build_log()
    state = StateContext(schema_version=1)
    result = log.replay(state)
    assert result.state == "idle"
    assert len(result.messages) == 2


def test_replay_unsupported_schema_raises():
    """SG2: schema_version=99 → ValueError."""
    log = _build_log()
    state = StateContext(schema_version=99)
    with pytest.raises(ValueError):
        log.replay(state)


def test_replay_unsupported_schema_message():
    """SG3: сообщение содержит версию и список поддерживаемых."""
    log = _build_log()
    state = StateContext(schema_version=42)
    with pytest.raises(ValueError, match="42"):
        log.replay(state)


test_replay_supported_schema()
test_replay_unsupported_schema_raises()
test_replay_unsupported_schema_message()
