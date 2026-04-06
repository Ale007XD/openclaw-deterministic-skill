"""
loop_test.py — тесты Execution Loop.

Инварианты:
  L1. text-only ответ: stop_reason="idle", reply установлен, log содержит user_input + llm_response
  L2. tool_call цикл: executor вызывается, tool_result добавляется в log, final state="idle"
  L3. max_iter: loop завершается при исчерпании итераций, stop_reason="max_iter"
  L4. no_executor: tool_call без executor → stop_reason="no_executor", state="waiting_tool"
  L5. causation_id / correlation_id: все события связаны через correlation_id первого user_input
"""

import asyncio
from typing import List, Dict, Any, Optional

from skill.models import StateContext
from skill.events import Event
from skill.providers.base_provider import BaseProvider
from skill.providers.provider_response import ProviderResponse, ToolCall
from skill.loop import run


# ---------------------------------------------------------------------------
# Вспомогательные провайдеры-заглушки
# ---------------------------------------------------------------------------

class TextOnlyProvider(BaseProvider):
    """Всегда возвращает фиксированный текстовый ответ."""

    def __init__(self, text: str = "Hello from LLM"):
        self._text = text

    async def chat(self, messages: List[Dict], tools=None) -> ProviderResponse:
        return ProviderResponse(text=self._text, tool_calls=[])


class SingleToolProvider(BaseProvider):
    """
    Первый вызов → tool_call("search", {"q": "test"}).
    Второй вызов → текстовый ответ (после tool_result).
    """

    def __init__(self):
        self._call_count = 0

    async def chat(self, messages: List[Dict], tools=None) -> ProviderResponse:
        self._call_count += 1
        if self._call_count == 1:
            return ProviderResponse(
                text=None,
                tool_calls=[ToolCall(
                    tool_name="search",
                    call_id="c42",
                    arguments={"q": "test"},
                )],
            )
        return ProviderResponse(text="Found it!", tool_calls=[])


class InfiniteProvider(BaseProvider):
    """Всегда возвращает текст, но state никогда не станет idle
    если мы не остановимся — имитируем через provider который всегда
    отвечает текстом (state идёт idle после каждого llm_response).
    Для max_iter нужен провайдер который всегда даёт processing.
    Используем tool_call без executor — другой тест.
    Вместо этого: провайдер возвращает user_input типа события не существует,
    поэтому strict_mode=False + unknown event будет игнорироваться...
    Проще: провайдер возвращает пустой tool_calls и text=None → llm_events пустой → idle.
    Реальный max_iter: нужна цепочка. Используем провайдер с счётчиком.
    """

    async def chat(self, messages: List[Dict], tools=None) -> ProviderResponse:
        # Возвращает tool_call каждый раз — без executor → no_executor на 1-й итерации
        # Для max_iter нужен другой сценарий: цикл tool_call + executor бесконечно
        return ProviderResponse(text="loop", tool_calls=[])


class CountingProvider(BaseProvider):
    """Возвращает текст N раз, но state после llm_response → idle,
    поэтому loop останавливается после первого ответа.
    Для теста max_iter нужен провайдер который держит state=processing.
    Единственный способ: tool_call с executor который ничего не делает,
    и провайдер снова отвечает tool_call → бесконечный цикл.
    """

    def __init__(self, max_calls: int):
        self._calls = 0
        self._max = max_calls

    async def chat(self, messages: List[Dict], tools=None) -> ProviderResponse:
        self._calls += 1
        # Всегда tool_call — с executor который возвращает "ok"
        return ProviderResponse(
            text=None,
            tool_calls=[ToolCall(
                tool_name="noop",
                call_id=f"c{self._calls}",
                arguments={},
            )],
        )


# ---------------------------------------------------------------------------
# Тесты
# ---------------------------------------------------------------------------

def test_text_only():
    """L1: text-only ответ → idle, reply установлен, 2 события в log."""
    provider = TextOnlyProvider("pong")
    result = asyncio.run(run("ping", provider))

    assert result.stop_reason == "idle", result.stop_reason
    assert result.reply == "pong"
    assert result.final_state.state == "idle"
    # user_input + llm_response
    assert len(result.log.events) == 2
    assert result.log.events[0].type == "user_input"
    assert result.log.events[1].type == "llm_response"


def test_tool_cycle():
    """L2: tool_call + executor → финальный reply, state=idle, 4 события."""
    provider = SingleToolProvider()
    call_log = []

    async def executor(tool_name: str, arguments: Dict) -> Any:
        call_log.append((tool_name, arguments))
        return "search_result_42"

    result = asyncio.run(run("search something", provider, executor=executor))

    assert result.stop_reason == "idle", result.stop_reason
    assert result.reply == "Found it!"
    assert result.final_state.state == "idle"
    assert result.final_state.pending_tool_call is None
    # user_input, tool_call, tool_result, llm_response
    assert len(result.log.events) == 4
    types = [e.type for e in result.log.events]
    assert types == ["user_input", "tool_call", "tool_result", "llm_response"]
    assert call_log == [("search", {"q": "test"})]


def test_no_executor():
    """L4: tool_call без executor → stop_reason='no_executor', state='waiting_tool'."""

    class ToolProvider(BaseProvider):
        async def chat(self, messages, tools=None):
            return ProviderResponse(
                text=None,
                tool_calls=[ToolCall(tool_name="calc", call_id="x1", arguments={})],
            )

    result = asyncio.run(run("calculate", ToolProvider()))

    assert result.stop_reason == "no_executor"
    assert result.final_state.state == "waiting_tool"
    assert result.final_state.pending_tool_call is not None


def test_max_iter():
    """L3: бесконечный tool_call цикл с executor → остановка по max_iter."""
    provider = CountingProvider(max_calls=999)

    async def noop_executor(tool_name: str, arguments: Dict) -> Any:
        return "ok"

    result = asyncio.run(run(
        "loop forever",
        provider,
        executor=noop_executor,
        max_iter=3,
    ))

    assert result.stop_reason == "max_iter"
    # 3 итерации: каждая даёт tool_call + tool_result → 1 + 3*2 = 7 событий
    assert len(result.log.events) == 7


def test_correlation_id_propagation():
    """L5: все события имеют одинаковый correlation_id == id первого user_input."""

    class TwoStepProvider(BaseProvider):
        def __init__(self):
            self._n = 0

        async def chat(self, messages, tools=None):
            self._n += 1
            if self._n == 1:
                return ProviderResponse(
                    text=None,
                    tool_calls=[ToolCall(tool_name="ping", call_id="p1", arguments={})],
                )
            return ProviderResponse(text="done", tool_calls=[])

    async def executor(tool_name, arguments):
        return "pong"

    result = asyncio.run(run("start", TwoStepProvider(), executor=executor))

    first_event = result.log.events[0]
    assert first_event.type == "user_input"

    corr_id = first_event.id
    for ev in result.log.events[1:]:
        assert ev.correlation_id == corr_id, (
            f"{ev.type} имеет correlation_id={ev.correlation_id}, ожидался {corr_id}"
        )


test_text_only()
test_tool_cycle()
test_no_executor()
test_max_iter()
test_correlation_id_propagation()
