"""Built-in evaluation metrics."""

from evalharness.metrics.base import BaseMetric, register_metric


@register_metric("faithfulness")
class Faithfulness(BaseMetric):
    """Does the answer follow from the retrieved context?"""

    def build_prompt(self, question, answer, context, expected):
        ctx = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(context))
        return f"""You are an expert evaluator. Rate how faithfully the answer is grounded in the provided context.

Question: {question}

Context:
{ctx}

Answer: {answer}

Score from 0.0 to 1.0:
- 1.0 = every claim in the answer is directly supported by the context
- 0.5 = some claims supported, some not
- 0.0 = answer contradicts or ignores the context

Respond with JSON only: {{"score": <float>, "reasoning": "<one sentence>"}}"""


@register_metric("relevance")
class AnswerRelevance(BaseMetric):
    """Does the answer actually address the question?"""

    def build_prompt(self, question, answer, context, expected):
        return f"""Rate how directly the answer addresses the question asked.

Question: {question}

Answer: {answer}

Score from 0.0 to 1.0:
- 1.0 = answer directly and completely addresses the question
- 0.5 = answer partially addresses or includes off-topic content
- 0.0 = answer is unrelated to the question

Respond with JSON only: {{"score": <float>, "reasoning": "<one sentence>"}}"""


@register_metric("hallucination")
class Hallucination(BaseMetric):
    """How much of the answer is NOT in the context? (Lower is better.)"""

    def build_prompt(self, question, answer, context, expected):
        ctx = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(context))
        return f"""Identify any claims in the answer that are NOT supported by the context.

Question: {question}

Context:
{ctx}

Answer: {answer}

Score from 0.0 to 1.0 (higher = more hallucination):
- 0.0 = every claim is grounded in the context
- 0.5 = mix of grounded and ungrounded claims
- 1.0 = answer is entirely fabricated relative to the context

Respond with JSON only: {{"score": <float>, "reasoning": "<one sentence>"}}"""


@register_metric("correctness")
class Correctness(BaseMetric):
    """Does the answer match the expected answer? Requires ground truth."""

    def build_prompt(self, question, answer, context, expected):
        if not expected:
            return ""  # signals: skip this metric
        return f"""Compare the predicted answer against the expected answer.

Question: {question}

Expected Answer: {expected}

Predicted Answer: {answer}

Score from 0.0 to 1.0:
- 1.0 = semantically equivalent (wording may differ)
- 0.5 = partially correct
- 0.0 = incorrect or contradicts expected

Respond with JSON only: {{"score": <float>, "reasoning": "<one sentence>"}}"""
