"""Gemini 구현체. 제공사를 바꿀 때는 이 파일만 교체하면 된다 (DECISIONS D10)."""
from __future__ import annotations

import time

from google import genai
from google.genai import types
from google.genai.errors import ServerError

from engine.decision.client import LLMClient
from engine.decision.models import DecisionRequest, DecisionResult
from engine.decision.prompt import build_batch_prompt

DEFAULT_MODEL = "gemini-2.5-flash-lite"

# Gemini가 "일시적으로 수요 과다(503)"를 실제로 자주 반환해서(SDK 자체 재시도로도
# 해결 안 되는 경우를 겪음) 여기서 한 번 더 지수 백오프로 재시도한다.
MAX_RETRIES = 4
INITIAL_BACKOFF_SEC = 5.0


class GeminiLLMClient(LLMClient):
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None) -> None:
        self._client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self._model = model

    def decide_batch(self, requests: list[DecisionRequest]) -> list[DecisionResult]:
        if not requests:
            return []

        backoff = INITIAL_BACKOFF_SEC
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=build_batch_prompt(requests),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=list[DecisionResult],
                    ),
                )
                return response.parsed
            except ServerError:
                if attempt == MAX_RETRIES:
                    raise
                time.sleep(backoff)
                backoff *= 2
