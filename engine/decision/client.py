"""LLM 클라이언트 인터페이스. 제공사를 바꿀 때 이 인터페이스를 구현하는
파일 하나만 교체하면 되도록 프롬프트 생성(prompt.py)과 분리한다 (DECISIONS D10).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from engine.decision.models import DecisionRequest, DecisionResult


class LLMClient(ABC):
    @abstractmethod
    def decide_batch(self, requests: list[DecisionRequest]) -> list[DecisionResult]:
        """여러 시민의 전환점 판단을 한 번의 호출로 묶어 처리한다 (CLAUDE.md 원칙 2)."""
        raise NotImplementedError
