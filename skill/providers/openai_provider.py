from typing import List, Dict, Any
from .base_provider import BaseProvider
from .provider_response import ProviderResponse, ToolCall


class OpenAIProvider(BaseProvider):
    """
    Stub provider (no external dependency).
    Replace with real OpenAI SDK integration later.
    """

    async def chat(
        self,
        messages: List[Dict],
        tools: list | None = None,
    ) -> ProviderResponse:
        """
        Deterministic stub:
        Always echoes last user message.
        """

        last = messages[-1]["content"] if messages else ""

        return ProviderResponse(
            text=f"echo: {last}",
            tool_calls=[],
            raw={"stub": True},
        )
