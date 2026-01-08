import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from app.main import app as main_app
from app.db.session import Base, get_db
from app.services.llm.manager import LLMFactory
from app.services.llm.base import LLMProvider
from app.schemas.evaluation import EvaluationPut

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(class_=AsyncSession, autoflush=False, expire_on_commit=False, bind=engine_test)

@pytest_asyncio.fixture()
async def db_session():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture()
async def client(db_session):
    async def override_get_db():
        yield db_session

    main_app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=main_app, base_url="http://test") as c:
        yield c
    main_app.dependency_overrides.clear()

# Mock LLM Provider
class MockLLM(LLMProvider):
    async def summarize(self, text: str) -> str:
        return "Mock Summary"

@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    def mock_get_provider():
        return MockLLM()
    monkeypatch.setattr(LLMFactory, "get_provider", mock_get_provider)
