from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass
