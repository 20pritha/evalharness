"""SQLite storage backend. Ground truth never leaves this layer to the answering side."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_name TEXT NOT NULL,
    question TEXT NOT NULL,
    expected_answer TEXT,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_set ON questions(set_name);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_name TEXT NOT NULL,
    question_set TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    question_id INTEGER NOT NULL REFERENCES questions(id),
    answer TEXT NOT NULL,
    context TEXT,
    scores TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(run_id, question_id)
);
"""


class Storage:
    """SQLite-backed storage with strict ground-truth isolation."""

    def __init__(self, db_path: str | Path = "./evalharness.db"):
        self.db_path = Path(db_path)
        self._init_schema()

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._conn() as c:
            c.executescript(SCHEMA)

    # ----- Questions -----

    def load_questions(self, set_name: str, questions: list[dict]) -> int:
        """Bulk-insert questions into a named set. Returns count inserted."""
        with self._conn() as c:
            rows = [
                (set_name, q["question"], q.get("expected_answer"),
                 json.dumps(q.get("metadata", {})))
                for q in questions
            ]
            c.executemany(
                "INSERT INTO questions (set_name, question, expected_answer, metadata) "
                "VALUES (?, ?, ?, ?)",
                rows,
            )
            return len(rows)

    def fetch_questions_for_agent(self, set_name: str) -> list[dict]:
        """Return questions WITHOUT expected answers. For the answering side."""
        with self._conn() as c:
            rows = c.execute(
                "SELECT id, question FROM questions WHERE set_name = ?",
                (set_name,),
            ).fetchall()
            return [dict(r) for r in rows]

    def fetch_questions_for_judge(self, set_name: str) -> list[dict]:
        """Return questions WITH expected answers. For scoring only."""
        with self._conn() as c:
            rows = c.execute(
                "SELECT id, question, expected_answer FROM questions WHERE set_name = ?",
                (set_name,),
            ).fetchall()
            return [dict(r) for r in rows]

    # ----- Runs -----

    def create_run(self, pipeline_name: str, question_set: str) -> int:
        """Create a new run, return atomic auto-incremented run_id."""
        with self._conn() as c:
            cursor = c.execute(
                "INSERT INTO runs (pipeline_name, question_set) VALUES (?, ?)",
                (pipeline_name, question_set),
            )
            return cursor.lastrowid

    def complete_run(self, run_id: int) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE runs SET status = 'completed', completed_at = CURRENT_TIMESTAMP "
                "WHERE id = ?",
                (run_id,),
            )

    # ----- Results -----

    def persist_result(
        self, run_id: int, question_id: int, answer: str, context: list[str]
    ) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO results (run_id, question_id, answer, context) "
                "VALUES (?, ?, ?, ?)",
                (run_id, question_id, answer, json.dumps(context)),
            )

    def fetch_results_for_judge(self, run_id: int) -> list[dict]:
        """Join results with expected answers — judging-side only."""
        with self._conn() as c:
            rows = c.execute(
                """
                SELECT r.id as result_id, r.question_id, r.answer, r.context,
                       q.question, q.expected_answer
                FROM results r
                JOIN questions q ON q.id = r.question_id
                WHERE r.run_id = ?
                """,
                (run_id,),
            ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["context"] = json.loads(d["context"]) if d["context"] else []
                results.append(d)
            return results

    def write_scores(self, result_id: int, scores: dict[str, Any]) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE results SET scores = ? WHERE id = ?",
                (json.dumps(scores), result_id),
            )

    def summarize_run(self, run_id: int) -> dict:
        """Aggregate scores across all results in a run."""
        with self._conn() as c:
            rows = c.execute(
                "SELECT scores FROM results WHERE run_id = ? AND scores IS NOT NULL",
                (run_id,),
            ).fetchall()
            if not rows:
                return {"run_id": run_id, "n": 0, "metrics": {}}

            all_scores = [json.loads(r["scores"]) for r in rows]
            metric_names = set()
            for s in all_scores:
                metric_names.update(s.keys())

            summary = {"run_id": run_id, "n": len(all_scores), "metrics": {}}
            for name in metric_names:
                values = [s[name] for s in all_scores if name in s and isinstance(s[name], (int, float))]
                if values:
                    mean = sum(values) / len(values)
                    var = sum((v - mean) ** 2 for v in values) / len(values)
                    summary["metrics"][name] = {
                        "mean": round(mean, 3),
                        "std": round(var ** 0.5, 3),
                        "n": len(values),
                    }
            return summary
