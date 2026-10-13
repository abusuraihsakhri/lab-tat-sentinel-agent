"""
Deterministic mock adapter; external model provider integrations are not implemented.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Lab Tat Sentinel Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} deterministic mock]: Received query: '{prompt[:60]}...'. No model inference or clinical verification was performed."


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Lab Tat Sentinel Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError(
            f"Provider '{provider}' is not implemented. Use 'mock' for deterministic responses."
        )
