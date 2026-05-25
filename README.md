<div align="center">

# 🧪 evalharness

**A zero-touch agentic evaluation harness for RAG pipelines.**

Point it at your RAG system. Run one command. Get LLM-as-judge scores back across faithfulness, relevance, and hallucination — automatically.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io)

</div>

---

## Why this exists

Evaluating RAG pipelines is the unsexy bottleneck of every GenAI team. The usual setup involves:

- A spreadsheet of test questions
- A human running the pipeline manually
- Another human (or the same one) scoring outputs
- Results scattered across Notion, Slack, and Excel

**`evalharness` replaces all of that with a single chat phrase.** It's an MCP server that exposes 4 orchestration tools to your LLM agent — fetch questions, run your pipeline, persist results, score with LLM-as-judge — and lets you trigger a full evaluation run from any MCP-compatible client (Claude Desktop, Cursor, etc.).

## What it does

```bash
You: "Run eval on the QFI test set using GPT-4o as judge"

Agent: ✓ Fetched 78 questions from test_set_v2
       ✓ Ran QFI RAG pipeline (78/78 answered)
       ✓ Persisted with run_id=rag_eval_142
       ✓ Scored on faithfulness, relevance, hallucination
       
       Results:
       - Faithfulness:   0.84 ± 0.12
       - Relevance:      0.91 ± 0.08
       - Hallucination:  0.06 ± 0.04
       
       Full report: ./reports/rag_eval_142.html
```

## Architecture

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│  MCP Client     │      │  evalharness server  │      │  Your RAG       │
│  (Claude, etc.) │─────▶│  (FastMCP)           │─────▶│  pipeline       │
└─────────────────┘      └──────────┬───────────┘      └─────────────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  ▼                 ▼                 ▼
            ┌──────────┐     ┌──────────┐      ┌──────────┐
            │ SQLite   │     │ Judges   │      │ Metrics  │
            │ storage  │     │ OAI/Gem  │      │ faith /  │
            │          │     │ Claude   │      │ relev /  │
            └──────────┘     └──────────┘      │ halluc   │
                                                └──────────┘
```

**Four MCP tools** exposed to the agent:
| Tool | Purpose |
|------|---------|
| `fetch_questions` | Pull a test set from storage (ground truth hidden from the agent) |
| `run_pipeline` | Invoke a user-registered RAG callable with each question |
| `persist_run` | Atomic write of question/answer/context tuples with auto-incremented run IDs |
| `score_run` | Trigger LLM-as-judge scoring across configurable metrics |

## Install

```bash
pip install evalharness
```

Or from source:

```bash
git clone https://github.com/prixie/evalharness
cd evalharness
pip install -e .
```

## Quickstart

**1. Register your RAG pipeline:**

```python
# my_pipeline.py
from evalharness import register_pipeline

@register_pipeline("my_rag")
def my_rag(question: str) -> dict:
    # ... your retrieval + generation
    return {
        "answer": "The capital of France is Paris.",
        "context": ["France's capital city is Paris..."]
    }
```

**2. Load a test set:**

```bash
evalharness load-questions examples/sample_questions.jsonl --name qfi_v1
```

**3. Start the MCP server:**

```bash
evalharness serve
```

**4. Connect from your MCP client** (e.g. add to `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "evalharness": {
      "command": "evalharness",
      "args": ["serve"]
    }
  }
}
```

**5. Say one phrase to your agent:**

> Run eval on qfi_v1 using gemini as judge

That's it.

## Supported judges

- ✅ OpenAI (GPT-4o, GPT-4o-mini)
- ✅ Google Gemini (2.5 Flash, 2.5 Pro)
- ✅ Anthropic Claude (Sonnet 4.6, Haiku 4.5)
- 🚧 Ollama (local) — *coming soon*

## Built-in metrics

| Metric | What it measures |
|--------|------------------|
| **Faithfulness** | Does the answer follow from the retrieved context? |
| **Answer Relevance** | Does the answer address the actual question? |
| **Hallucination Rate** | Does the answer contain claims not in the context? |
| **Context Precision** | Are the retrieved chunks actually relevant? |

Custom metrics? Implement `BaseMetric` and register it. Three lines.

## Why MCP and not a script?

Because the agent should drive the eval — not the engineer. Engineers should write code. Agents should run eval loops. `evalharness` is what happens when you take that idea seriously.

## Roadmap

- [ ] Ollama / local judge support
- [ ] HTML report generation
- [ ] Weights & Biases / MLflow exporters
- [ ] Parallel judge dispatch (asyncio)
- [ ] Streaming progress updates back to the MCP client

## License

MIT. Use it, fork it, ship it.

---

<sub>Built by [Pritha Mishra](https://github.com/prixie) — based on a production system shipped at Tiger Analytics for a US private equity client.</sub>
