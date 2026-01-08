import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_API_KEY"] = "dummy"

from app.main import app as main_app
from app.db.session import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    class_=AsyncSession, 
    autoflush=False, 
    expire_on_commit=False, 
    bind=engine_test
)

@pytest_asyncio.fixture()
async def db_session():
    """
    Creates a fresh database session for a test.
    Dropping tables after ensuring isolation.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

from app.api.v1.endpoints.evaluations import get_llm_provider, get_db

@pytest_asyncio.fixture()
async def client(db_session):
    """
    AsyncClient fixture for FastAPI.
    Overrides the get_db dependency to use the test database session.
    Also overrides get_llm_provider to use a mock.
    """
    async def override_get_db():
        yield db_session

    class MockOllama:
        def __init__(self, *args, **kwargs):
            pass
        async def summarize(self, text: str) -> str:
            return "Mock Summary"

    def override_get_llm_provider():
        return MockOllama()

    main_app.dependency_overrides[get_db] = override_get_db
    main_app.dependency_overrides[get_llm_provider] = override_get_llm_provider
    
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    
    main_app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_llm_provider(monkeypatch):
    """
    Globally mock OllamaLLMProvider to avoid real network calls during tests.
    """
    class MockOllama:
        def __init__(self, *args, **kwargs):
            pass
        async def summarize(self, text: str) -> str:
            return "Mock Summary"

    monkeypatch.setattr("app.services.llm.OllamaLLMProvider.OllamaLLMProvider", MockOllama)
