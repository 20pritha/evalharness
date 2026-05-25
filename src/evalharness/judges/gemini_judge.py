"""Google Gemini judge implementation (uses the new google-genai SDK)."""

import os

from evalharness.judges.base import BaseJudge, register_judge


@register_judge("gemini")
class GeminiJudge(BaseJudge):
    def __init__(self, model: str = "gemini-2.5-flash", api_key: str | None = None):
        try:
            from google import genai
        except ImportError as e:
            raise ImportError(
                "Gemini judge requires `pip install evalharness[gemini]`"
            ) from e

        self.client = genai.Client(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
        self.model = model

    def score(self, prompt: str) -> str:
        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
            },
        )
        return resp.text or "{}"
