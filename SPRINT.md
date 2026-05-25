# 3-Week Sprint Plan

Internal planning doc — for tracking what's done and what's next. **Delete or rename before pushing publicly if you'd rather not show the timeline.**

## Status legend
- [x] Done — scaffolded and ready to wire up
- [ ] To do — needs real implementation
- 🔥 Critical path
- 💎 Polish (do last)

---

## Week 1 — Get end-to-end working on a toy dataset

**Goal:** A single MCP client (Claude Desktop) can run a full eval against the mock pipeline using one judge.

- [x] Repo scaffold, README, LICENSE, gitignore, CI
- [x] Pipeline registry (`pipelines.py`)
- [x] SQLite storage layer with ground-truth isolation
- [x] Base judge interface + OpenAI/Gemini/Anthropic stubs
- [x] Base metric interface + 4 built-in metrics
- [x] FastMCP server with the 4 orchestration tools
- [x] CLI (`load-questions`, `serve`, `info`)
- [ ] 🔥 Verify `fastmcp` is actually installed and the server runs (`evalharness serve`)
- [ ] 🔥 Hook up Claude Desktop config and run the full demo
- [ ] 🔥 Record a 15-second screen recording of the demo working
- [ ] Drop the screen recording into the README as a GIF

## Week 2 — Make it usable for someone else

**Goal:** Anyone could clone the repo and reproduce the demo in under 5 minutes.

- [ ] 🔥 Write `examples/quickstart.md` with a step-by-step
- [ ] Add `--judge` and `--metrics` flags to CLI for non-MCP usage
- [ ] Add `evalharness summarize <run_id>` CLI command for inspection
- [ ] Add a real benchmark notebook: run eval against a small open-source RAG (e.g. one from the LlamaIndex examples) and report numbers
- [ ] 💎 HTML report generator (`reports/run_<id>.html` with charts)
- [ ] 💎 Add OpenTelemetry span emission per tool call (subtle flex — matches your QCG resume bullet)

## Week 3 — Polish and ship

**Goal:** Looks professional enough that a senior engineer would star it.

- [ ] 🔥 Hero GIF at the top of README
- [ ] 🔥 Architecture diagram (use Excalidraw or Mermaid)
- [ ] 🔥 Write a blog post or LinkedIn write-up: "Why I built an MCP server for RAG eval"
- [ ] 💎 Add Mermaid sequence diagram to `docs/architecture.md`
- [ ] 💎 Publish to PyPI (`pip install evalharness` should work)
- [ ] 💎 Pin the repo on your GitHub profile
- [ ] 💎 Add a CHANGELOG.md

## Stretch (only if time permits)

- [ ] Ollama / local judge support
- [ ] Parallel judge dispatch (asyncio)
- [ ] Streaming progress updates back to the MCP client
- [ ] W&B / MLflow exporters

---

## Daily checklist (commit hygiene)

- One meaningful commit per session (not a giant dump at the end)
- Each commit message: imperative verb + what + why (e.g. "Add ground-truth isolation test for storage layer")
- Push at the end of every session even if mid-feature (use `wip:` prefix)
- Recruiters look at the commit graph as much as the code

## What "done" looks like for Week 3

When you can paste this into a recruiter DM and feel good about it:

> Hi — I built an open-source MCP server for RAG evaluation, based on a production system I shipped at Tiger Analytics. It exposes 4 orchestration tools that let an LLM agent run a full eval (fetch questions → invoke pipeline → score with LLM-as-judge) from a single chat phrase. 27 stars, CI passing, available on PyPI. Repo: github.com/prixie/evalharness
