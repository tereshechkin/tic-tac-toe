from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.game_repository.models import LLMModel
from app.core.exceptions import NotFoundException

class LLMRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_model_by_id(self, model_id: UUID) -> LLMModel:
        stmt = select(LLMModel).where(LLMModel.id == model_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundException("LLM model not found")
        return model

    async def list_models(self, enabled_only: bool = True) -> List[LLMModel]:
        stmt = select(LLMModel)
        if enabled_only:
            stmt = stmt.where(LLMModel.enabled == True)
        stmt = stmt.order_by(LLMModel.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()
