import uuid
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evaluation import Evaluation
from app.schemas.evaluation import EvaluationCreate, EvaluationPut
from uuid import UUID

class EvaluationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, evaluation_in: EvaluationCreate) -> Evaluation:
        db_obj = Evaluation(**evaluation_in.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_contestant(self, contestant_id: str) -> list[Evaluation]:
        stmt = select(Evaluation).where(Evaluation.contestant_id == contestant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, id: uuid.UUID) -> Evaluation | None:
        stmt = select(Evaluation).where(Evaluation.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, evaluation_id: UUID, data: EvaluationPut) -> Evaluation | None:
        db_obj = await self.get(evaluation_id)
        if not db_obj:
            return None

        data_dict = data.model_dump(exclude_unset=True)
        for key, value in data_dict.items():
            setattr(db_obj, key, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, evaluation_id: uuid.UUID) -> bool:
        db_obj = await self.get(evaluation_id)
        if not db_obj:
            return False
        await self.session.delete(db_obj)
        await self.session.commit()
        return True