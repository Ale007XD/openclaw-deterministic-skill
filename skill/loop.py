"""
Execution Loop — связующий цикл агента.

Алгоритм:
  1. user_input → δ → state=processing
  2. Пока state == "processing" и iteration < max_iter:
     a. вызов provider.chat(messages, tools)
     b. map_response_to_events → List[Event]
     c. каждый Event прогоняем через δ и пишем в EventLog
     d. если в ответе есть tool_call — вызываем executor(tool_name, arguments)
        результат оборачиваем в tool_result Event → δ → EventLog
  3. Остановка: state == "idle" | "waiting_tool" без executor | max_iter
  4. Возвращаем (итоговый текст ответа, EventLog)

Гарантии:
  - δ остаётся чистой функцией: loop не трогает delta.py
  - causation_id каждого события = id триггерного события
  - correlation_id фиксируется один раз — id первого user_input Event
  - ToolExecutor — протокол, не ABC: duck typing, легко мокируется в тестах
"""

from __future__ import annotations

import uuid
from typing import Callable, Awaitable, Any, Dict, List, Optional

from .models import StateContext
from .events import Event
from .event_log import EventLog
from .delta import step
from .providers.base_provider import BaseProvider
from .providers.mapper import map_response_to_events


# ToolExecutor: async callable (tool_name, arguments) → result (Any)
ToolExecutor = Callable[[str, Dict[str, Any]], Awaitable[Any]]


class LoopResult:
    """Итог выполнения loop.run()."""

    def __init__(
        self,
        final_state: StateContext,
        log: EventLog,
        reply: Optional[str],
        stop_reason: str,
    ) -> None:
        self.final_state = final_state
        self.log = log
        self.reply = reply          # последний llm_response.text или None
        self.stop_reason = stop_reason  # "idle" | "max_iter" | "no_executor"


async def run(
    user_text: str,
    provider: BaseProvider,
    *,
    tools: Optional[List[Dict]] = None,
    executor: Optional[ToolExecutor] = None,
    initial_state: Optional[StateContext] = None,
    max_iter: int = 10,
) -> LoopResult:
    """
    Запускает агентный цикл.

    Параметры
    ---------
    user_text     : текст пользователя (первый event)
    provider      : реализация BaseProvider (async chat)
    tools         : схемы инструментов для провайдера (опционально)
    executor      : async callable для выполнения tool_call (опционально)
    initial_state : начальный StateContext (по умолчанию — чистый)
    max_iter      : защита от бесконечного цикла

    Возвращает
    ----------
    LoopResult с final_state, EventLog, reply, stop_reason
    """
    state = initial_state if initial_state is not None else StateContext()
    log = EventLog()

    # --- 1. user_input -------------------------------------------------------
    user_event = Event(
        type="user_input",
        payload={"text": user_text},
        source="user",
    )
    correlation_id = user_event.id   # фиксируем на всю сессию

    state = step(state, user_event)
    log.append(user_event)

    reply: Optional[str] = None
    stop_reason = "max_iter"

    # --- 2. Основной цикл ----------------------------------------------------
    for _ in range(max_iter):
        if state.state != "processing":
            stop_reason = "idle"
            break

        # 2a. Вызов провайдера
        response = await provider.chat(state.messages, tools=tools)
        causation_id = log.events[-1].id   # последнее записанное событие

        # 2b. ProviderResponse → Events
        llm_events = map_response_to_events(
            response,
            causation_id=causation_id,
            correlation_id=correlation_id,
        )

        if not llm_events:
            # Провайдер вернул пустой ответ — выходим
            stop_reason = "idle"
            break

        # 2c. Применяем события LLM к состоянию
        for ev in llm_events:
            state = step(state, ev)
            log.append(ev)

            if ev.type == "llm_response":
                reply = ev.payload.get("text")

        # 2d. Обработка tool_call
        if state.state == "waiting_tool":
            if executor is None:
                stop_reason = "no_executor"
                break

            pending = state.pending_tool_call
            tool_name = pending["tool_name"]
            call_id = pending.get("call_id", str(uuid.uuid4()))
            arguments = pending.get("arguments", {})

            raw_result = await executor(tool_name, arguments)

            tool_result_event = Event(
                type="tool_result",
                payload={
                    "tool_name": tool_name,
                    "call_id": call_id,
                    "result": raw_result,
                },
                source="tool",
                causation_id=log.events[-1].id,
                correlation_id=correlation_id,
            )

            state = step(state, tool_result_event)
            log.append(tool_result_event)
            # После tool_result state = "processing" → следующая итерация
    else:
        stop_reason = "max_iter"

    if state.state == "idle" and stop_reason == "max_iter":
        stop_reason = "idle"

    return LoopResult(
        final_state=state,
        log=log,
        reply=reply,
        stop_reason=stop_reason,
    )
