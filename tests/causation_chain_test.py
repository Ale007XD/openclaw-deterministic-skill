"""
causation_chain_test.py — тесты D2 и D6.

D2 — causation_id chain: при нескольких событиях в одном ответе провайдера
каждое событие ссылается на предыдущее, а не на общего предка.

D6 — stop_reason: определяется из итогового state, не из промежуточных флагов.

Инварианты:
  CC1. text-only: llm_response.causation_id == user_input.id (прямая цепочка).
  CC2. Будущий случай text+tool: tool_call.causation_id == llm_response.id (не user_input.id).
  CC3. stop_reason="idle" при state=idle (в т.ч. после max_iter если последний ответ — текст).
  CC4. stop_reason="no_executor" при state=waiting_tool и executor=None.
  CC5. stop_reason="max_iter" при исчерпании итераций без достижения idle.
"""

import asyncio
import pytest
from typing import List, Dict, Any

from skill.providers.base_provider import BaseProvider
from skill.providers.provider_response import ProviderResponse, ToolCall
from skill.loop import run


class TextOnlyProvider(BaseProvider):
    async def chat(self, messages: List[Dict], tools=None) -> ProviderResponse:
        return ProviderResponse(text="reply", tool_calls=[])


class ToolThenTextProvider(BaseProvider):
    """Первый вызов → tool_call. Второй → текст."""
    def __init__(self):
        self._n = 0

    async def chat(self, messages: List[Dict], tools=None) -> ProviderResponse:
        self._n += 1
        if self._n == 1:
            return ProviderResponse(
                text=None,
                tool_calls=[ToolCall(tool_name="ping", call_id="p1", arguments={})],
            )
        return ProviderResponse(text="done", tool_calls=[])


class AlwaysToolProvider(BaseProvider):
    """Всегда tool_call — для теста max_iter."""
    def __init__(self):
        self._n = 0

    async def chat(self, messages, tools=None):
        self._n += 1
        return ProviderResponse(
            text=None,
            tool_calls=[ToolCall(tool_name="noop", call_id=f"c{self._n}", arguments={})],
        )


# --- D2 тесты ---

def test_causation_chain_text_only():
    """CC1: llm_response.causation_id == user_input.id."""
    result = asyncio.run(run("hello", TextOnlyProvider()))
    events = result.log.events
    user_ev = events[0]
    llm_ev = events[1]
    assert user_ev.type == "user_input"
    assert llm_ev.type == "llm_response"
    assert llm_ev.causation_id == user_ev.id


def test_causation_chain_tool_cycle():
    """CC2: tool_call.causation_id == user_input.id, tool_result → tool_call, llm_response → tool_result."""
    async def executor(name, args):
        return "ok"

    result = asyncio.run(run("go", ToolThenTextProvider(), executor=executor))
    events = result.log.events
    # [user_input, tool_call, tool_result, llm_response]
    assert [e.type for e in events] == ["user_input", "tool_call", "tool_result", "llm_response"]

    user_ev, tool_call_ev, tool_result_ev, llm_ev = events

    # tool_call порождён user_input (первый llm_events после него)
    assert tool_call_ev.causation_id == user_ev.id
    # tool_result порождён tool_call (последнее событие в log перед его созданием)
    assert tool_result_ev.causation_id == tool_call_ev.id
    # llm_response порождён tool_result (последнее событие когда провайдер вызван второй раз)
    assert llm_ev.causation_id == tool_result_ev.id


# --- D6 тесты ---

def test_stop_reason_idle():
    """CC3: простой текстовый ответ → stop_reason=idle."""
    result = asyncio.run(run("ping", TextOnlyProvider()))
    assert result.stop_reason == "idle"
    assert result.final_state.state == "idle"


def test_stop_reason_no_executor():
    """CC4: tool_call без executor → no_executor."""
    class ToolProvider(BaseProvider):
        async def chat(self, messages, tools=None):
            return ProviderResponse(
                text=None,
                tool_calls=[ToolCall(tool_name="x", call_id="1", arguments={})],
            )

    result = asyncio.run(run("go", ToolProvider()))
    assert result.stop_reason == "no_executor"
    assert result.final_state.state == "waiting_tool"


def test_stop_reason_max_iter():
    """CC5: бесконечный tool_call с executor → max_iter."""
    async def noop(name, args):
        return "ok"

    result = asyncio.run(run("go", AlwaysToolProvider(), executor=noop, max_iter=2))
    assert result.stop_reason == "max_iter"


test_causation_chain_text_only()
test_causation_chain_tool_cycle()
test_stop_reason_idle()
test_stop_reason_no_executor()
test_stop_reason_max_iter()
