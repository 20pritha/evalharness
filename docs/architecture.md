# Architecture

## Design principles

1. **Agent-driven, not script-driven.** The evaluation flow is exposed as MCP tools, not a CLI runner. The agent decides the order.
2. **Ground truth never leaves the DB.** When the agent fetches questions, expected answers are projected out at the DB layer. The judging LLM gets them later, separately, never the answering agent.
3. **Atomic writes.** Every persisted run gets an auto-incremented ID. No race conditions even with parallel agents.
4. **Pluggable everything.** Judges, metrics, storage backends, pipelines — all behind interfaces.

## Component breakdown

### Server (`src/evalharness/server/`)

A FastMCP server exposing four tools. Each tool is a thin orchestration wrapper around storage + judge + metrics modules.

### Storage (`src/evalharness/storage/`)

SQLite by default. Three tables:
- `questions(id, set_name, question, expected_answer, metadata)`
- `runs(id, pipeline_name, started_at, completed_at, status)`
- `results(run_id, question_id, answer, context, scores_json)`

### Judges (`src/evalharness/judges/`)

`BaseJudge` interface — every provider implements `score(question, answer, context, expected) -> dict`. Implementations for OpenAI, Gemini, and Claude. Add a provider in ~20 lines.

### Metrics (`src/evalharness/metrics/`)

Each metric is a class with a `name`, a `prompt_template`, and a `parse_response` method. The judge runs the prompt; the metric parses the JSON score.

## Sequence: a full eval run

```
agent → server.fetch_questions(set_name)
   ← list of {id, question} (NO expected_answer)

for each question:
   agent → server.run_pipeline(pipeline_name, question_id)
       → calls user-registered pipeline callable
       ← {answer, context}
   agent → server.persist_run(run_id, question_id, answer, context)

agent → server.score_run(run_id, judge="gpt-4o", metrics=[...])
   → fetches expected_answers + results
   → calls judge.score(...) for each (metric, result) pair
   → writes scores back to results.scores_json
   ← aggregate summary
```

## Why ground truth isolation matters

If the answering pipeline ever sees the expected answer, your eval is poisoned. Even indirectly — through logs, debug output, or an over-eager retrieval system that scrapes your test DB. The DB-layer projection guarantees the answering side cannot accidentally cheat.
