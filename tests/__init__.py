import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_API_KEY"] = "dummy"
