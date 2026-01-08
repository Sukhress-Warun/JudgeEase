from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.endpoints import evaluations
from app.db.session import engine, Base
from app.exceptions.handlers import database_exception_handler, generic_exception_handler, custom_exception_handler
from app.exceptions.customExceptions.client_exceptions import CustomException


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Judge Evaluation API", lifespan=lifespan)

# Exception Handlers
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
app.include_router(evaluations.router, prefix="/api/v1", tags=["evaluations"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
