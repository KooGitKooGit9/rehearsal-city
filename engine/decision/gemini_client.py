"""Gemini 구현체. 제공사를 바꿀 때는 이 파일만 교체하면 된다 (DECISIONS D10)."""
from __future__ import annotations

from google import genai
from google.genai import types

from engine.decision.client import LLMClient
from engine.decision.models import DecisionRequest, DecisionResult
from engine.decision.prompt import build_batch_prompt

DEFAULT_MODEL = "gemini-2.5-flash-lite"


class GeminiLLMClient(LLMClient):
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None) -> None:
        self._client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self._model = model

    def decide_batch(self, requests: list[DecisionRequest]) -> list[DecisionResult]:
        if not requests:
            return []

        response = self._client.models.generate_content(
            model=self._model,
            contents=build_batch_prompt(requests),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[DecisionResult],
            ),
        )
        return response.parsed
