"""Google Gemini judge implementation."""

import os

from evalharness.judges.base import BaseJudge, register_judge


@register_judge("gemini")
class GeminiJudge(BaseJudge):
    def __init__(self, model: str = "gemini-2.5-flash", api_key: str | None = None):
        try:
            import google.generativeai as genai
        except ImportError as e:
            raise ImportError(
                "Gemini judge requires `pip install evalharness[gemini]`"
            ) from e

        genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
        self.client = genai.GenerativeModel(model)
        self.model = model

    def score(self, prompt: str) -> str:
        resp = self.client.generate_content(
            prompt,
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
            },
        )
        return resp.text or "{}"
