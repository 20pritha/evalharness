"""Command-line interface for evalharness."""

import json
from pathlib import Path

import click
from rich.console import Console

from evalharness.server import build_server
from evalharness.storage import Storage

console = Console()


@click.group()
@click.version_option()
def main():
    """evalharness — agentic LLM evaluation harness."""


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--name", required=True, help="Name for the question set")
@click.option("--db", default="./evalharness.db", help="Path to SQLite DB")
def load_questions(file: str, name: str, db: str):
    """Load questions from a JSONL file into a named test set.

    File format (one JSON object per line):
        {"question": "...", "expected_answer": "...", "metadata": {...}}
    """
    storage = Storage(db)
    questions = []
    with open(file) as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    count = storage.load_questions(name, questions)
    console.print(f"[green]✓[/green] Loaded {count} questions into set [bold]'{name}'[/bold]")


@main.command()
@click.option("--db", default="./evalharness.db", help="Path to SQLite DB")
def serve(db: str):
    """Start the MCP server (stdio transport)."""
    console.print(f"[cyan]Starting evalharness MCP server (db={db})...[/cyan]")
    server = build_server(db)
    server.run()


@main.command()
@click.option("--db", default="./evalharness.db", help="Path to SQLite DB")
def info(db: str):
    """Show registered pipelines, judges, and metrics."""
    from evalharness.judges import list_judges
    from evalharness.metrics import list_metrics
    from evalharness.pipelines import list_pipelines

    console.print("[bold cyan]evalharness[/bold cyan]")
    console.print(f"  DB: {Path(db).absolute()}")
    console.print(f"  Pipelines: {list_pipelines() or '[dim](none registered)[/dim]'}")
    console.print(f"  Judges:    {list_judges() or '[dim](none — install [openai|gemini|anthropic])[/dim]'}")
    console.print(f"  Metrics:   {list_metrics()}")


if __name__ == "__main__":
    main()
