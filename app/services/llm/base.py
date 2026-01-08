from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def summarize(self, text: str) -> str:
        """Generating a summary from the provided text."""
        pass
