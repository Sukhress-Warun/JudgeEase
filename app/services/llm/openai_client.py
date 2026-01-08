import httpx
from app.services.llm.base import LLMProvider
from app.config.settings import settings

class OpenAIProvider(LLMProvider):
    async def summarize(self, text: str) -> str:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
            
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            try:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "Start with 'Summary: '. Summarize the following judge evaluations concisely."},
                            {"role": "user", "content": text}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 150
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
                raise e
