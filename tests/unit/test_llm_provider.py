import pytest
import respx
from httpx import Response
from app.services.llm.generic_provider import HttpLLMProvider, openai_payload_builder, openai_response_parser

@pytest.mark.asyncio
async def test_openai_provider_success():
    provider = HttpLLMProvider(
        base_url="https://api.openai.com/v1/chat/completions",
        api_key="test-key",
        model="gpt-3.5-turbo",
        payload_builder=openai_payload_builder,
        response_parser=openai_response_parser
    )
    
    with respx.mock(base_url="https://api.openai.com") as respx_mock:
        respx_mock.post("/v1/chat/completions").mock(return_value=Response(
            200, 
            json={"choices": [{"message": {"content": "Summary result"}}]}
        ))
        
        result = await provider.summarize("test input")
        assert result == "Summary result"

@pytest.mark.asyncio
async def test_provider_missing_key():
    provider = HttpLLMProvider(
        base_url="...",
        api_key="",
        model="gpt-3.5-turbo",
        payload_builder=openai_payload_builder,
        response_parser=openai_response_parser
    )
    with pytest.raises(ValueError, match="API Key is missing"):
        await provider.summarize("test")

@pytest.mark.asyncio
async def test_custom_payload_builder():
    def custom_builder(text, model):
        return {"custom_prompt": text}
    
    def custom_parser(data):
        return data["result"]
        
    provider = HttpLLMProvider(
        base_url="https://custom.api",
        api_key="key",
        model="custom-model",
        payload_builder=custom_builder,
        response_parser=custom_parser
    )
    
    with respx.mock(base_url="https://custom.api") as respx_mock:
        route = respx_mock.post("/").mock(return_value=Response(
            200, json={"result": "Custom Summary"}
        ))
        
        result = await provider.summarize("Hello")
        assert result == "Custom Summary"
        assert route.called
        assert route.calls.last.request.content == b'{"custom_prompt": "Hello"}'
