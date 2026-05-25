"""Example: a tiny mock RAG pipeline you can register and evaluate.

In a real project, this would do retrieval against a vector DB + LLM generation.
Here we just return a canned answer for demo purposes — the point is to show
the registration pattern.

Usage:
    from evalharness import register_pipeline

    @register_pipeline("my_rag")
    def my_rag(question: str) -> dict:
        ...
        return {"answer": "...", "context": ["...", "..."]}
"""

from evalharness import register_pipeline


@register_pipeline("mock_rag")
def mock_rag(question: str) -> dict:
    """A stub RAG pipeline. Replace with your real retrieval + generation."""
    # In reality:
    #   chunks = vectorstore.search(question, k=3)
    #   answer = llm.generate(question, context=chunks)
    #   return {"answer": answer, "context": [c.text for c in chunks]}

    canned = {
        "What is the capital of France?": {
            "answer": "Paris is the capital of France.",
            "context": [
                "France is a country in Western Europe. Its capital is Paris.",
                "Paris has been the capital of France since 987 AD.",
            ],
        },
        "Who wrote Hamlet?": {
            "answer": "William Shakespeare wrote Hamlet around 1600.",
            "context": [
                "Hamlet is a tragedy by William Shakespeare, written between 1599 and 1601.",
            ],
        },
    }

    return canned.get(
        question,
        {"answer": "I don't know.", "context": []},
    )
