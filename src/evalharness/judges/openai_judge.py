"""OpenAI judge implementation."""

import os

from evalharness.judges.base import BaseJudge, register_judge


@register_judge("openai")
class OpenAIJudge(BaseJudge):
    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError(
                "OpenAI judge requires `pip install evalharness[openai]`"
            ) from e

        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self.model = model

    def score(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content or "{}"
