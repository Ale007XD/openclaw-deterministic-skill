# OpenClaw Deterministic Skill

## Core Model

S_{t+1} = δ(S_t, E_t)

## Event Definition

E_t = {
  id,
  type,
  payload,
  metadata,
  timestamp,
  source,
  causation_id,
  correlation_id
}

## Guarantees

- Deterministic FSM
- Event Sourcing
- Replayable execution
- No hidden state

## Replay Invariant

Replay(E₀..Eₙ) = Sₙ

## Run

```bash
python -m py_compile skill/*.py
python tests/run_all.py
