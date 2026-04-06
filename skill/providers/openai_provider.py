from typing import List, Dict
from .base_provider import BaseProvider
from .provider_response import ProviderResponse


class OpenAIProvider(BaseProvider):

    async def chat(
        self,
        messages: List[Dict],
        tools: list | None = None,
    ) -> ProviderResponse:

        if tools is not None:
            raise NotImplementedError("Tool calling not implemented in stub")

        last = messages[-1]["content"] if messages else ""

        return ProviderResponse(
            text=f"echo: {last}",
            tool_calls=[],
            raw={"stub": True},
        )
