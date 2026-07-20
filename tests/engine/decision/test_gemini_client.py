"""GeminiLLMClient의 구조만 검증한다 — 실제 API 키가 없어 decide_batch()는 호출하지 않는다."""
from engine.decision.client import LLMClient
from engine.decision.gemini_client import GeminiLLMClient


def test_gemini_client_implements_llm_client_interface():
    client = GeminiLLMClient(api_key="dummy-key-for-structural-test-only")

    assert isinstance(client, LLMClient)
