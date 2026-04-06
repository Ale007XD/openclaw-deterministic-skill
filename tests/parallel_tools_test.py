"""
parallel_tools_test.py — тесты D3: guard на параллельные tool_calls в mapper.

Инварианты:
  PT1. Один tool_call в ответе → маппируется без ошибок.
  PT2. Два tool_calls в одном ответе → NotImplementedError из mapper.
  PT3. Сообщение содержит количество и имена инструментов.
  PT4. Через loop.run() с провайдером возвращающим 2 tool_calls → NotImplementedError пробрасывается.
"""

import asyncio
import pytest
from typing import List, Dict

from skill.providers.mapper import map_response_to_events
from skill.providers.provider_response import ProviderResponse, ToolCall
from skill.providers.base_provider import BaseProvider
from skill.loop import run


def _make_response(*tool_names: str) -> ProviderResponse:
    return ProviderResponse(
        text=None,
        tool_calls=[
            ToolCall(tool_name=name, call_id=f"c{i}", arguments={})
            for i, name in enumerate(tool_names)
        ],
    )


def test_single_tool_call_ok():
    """PT1: один tool_call маппируется без ошибок."""
    resp = _make_response("search")
    events = map_response_to_events(resp, causation_id="x", correlation_id="y")
    assert len(events) == 1
    assert events[0].type == "tool_call"


def test_parallel_tool_calls_raises():
    """PT2: два tool_calls → NotImplementedError."""
    resp = _make_response("search", "calc")
    with pytest.raises(NotImplementedError):
        map_response_to_events(resp, causation_id="x", correlation_id="y")


def test_parallel_tool_calls_message():
    """PT3: сообщение содержит имена инструментов."""
    resp = _make_response("alpha", "beta")
    with pytest.raises(NotImplementedError, match="alpha"):
        map_response_to_events(resp, causation_id="x", correlation_id="y")


def test_parallel_tools_propagates_through_loop():
    """PT4: loop.run() с параллельными tool_calls → NotImplementedError пробрасывается."""

    class ParallelToolProvider(BaseProvider):
        async def chat(self, messages: List[Dict], tools=None) -> ProviderResponse:
            return _make_response("tool_a", "tool_b")

    with pytest.raises(NotImplementedError):
        asyncio.run(run("go", ParallelToolProvider()))


test_single_tool_call_ok()
test_parallel_tool_calls_raises()
test_parallel_tools_message = test_parallel_tool_calls_message
test_parallel_tools_message()
test_parallel_tools_propagates_through_loop()
