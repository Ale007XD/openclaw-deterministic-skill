# OpenClaw Deterministic Skill

## Core Model

```
S_{t+1} = δ(S_t, E_t)
```

δ — чистая функция. Нет внешних зависимостей, нет env-переменных в теле.

## Event

```
E_t = {
  id,            # транспортный UUID, не участвует в сравнении
  type,
  payload,
  metadata,
  timestamp,     # транспортный, не участвует в сравнении
  source,
  causation_id,
  correlation_id,
  event_hash     # H(type, payload, causation_id) — детерминированная идентичность
}
```

`Event.__eq__` работает по `event_hash`. Два независимо созданных события
с одинаковым `type`, `payload` и `causation_id` считаются равными.

## FSM States

```
idle → processing → waiting_tool → processing → idle
```

Инварианты, enforced в δ:
- `tool_result` без предшествующего `tool_call` → `ValueError`
- `tool_call` при непустом `pending_tool_call` → `ValueError`
- `tool_result.tool_name ≠ pending.tool_name` → `ValueError`
- неизвестный `event.type` при `strict_mode=True` → `ValueError`

## StateContext

```python
StateContext(
    schema_version=1,
    state="idle",
    messages=[],
    iteration=0,
    tool_results=[],
    pending_tool_call=None,
    strict_mode=True,   # P1: конфигурация живёт в состоянии, не в env
)
```

## Guarantees

- Deterministic FSM: `δ(S, E)` зависит только от `S` и `E`
- Event Sourcing: каждое изменение — событие в `EventLog`
- Replayable: `Replay(E₀..Eₙ) = Sₙ`, идемпотентно
- No hidden state: нет глобальных переменных в δ
- FSM completeness: все известные переходы валидируются локально

## Run

```bash
python -m py_compile skill/*.py skill/providers/*.py
python tests/run_all.py
```
