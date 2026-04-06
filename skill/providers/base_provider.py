from abc import ABC, abstractmethod
from typing import List, Dict

from .provider_response import ProviderResponse


class BaseProvider(ABC):
    """
    Canonical Provider interface.
    """

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict],
        tools: list | None = None,
    ) -> ProviderResponse:
        """
        MUST return normalized ProviderResponse.
        """
        pass
