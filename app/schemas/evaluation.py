from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

class EvaluationBase(BaseModel):
    contestant_id: str = Field(..., min_length=1)
    judge_id: str = Field(..., min_length=1)
    score: int = Field(..., ge=0, le=100)
    notes: str = Field(..., min_length=1)

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationPut(EvaluationBase):
    pass


class EvaluationResponse(EvaluationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EvaluationSummary(BaseModel):
    evaluations: list[EvaluationResponse]
    summary: str | None = None
    summary_error: str | None = None
    overall_score: int | None = None
