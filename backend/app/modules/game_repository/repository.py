from uuid import UUID
from typing import Optional, Tuple, List
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.game_repository.models import Game, GamePlayer


class GameDbRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_games(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        model_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Tuple[List[Game], int]:
        # Base query: games where user is a participant
        stmt = (
            select(Game)
            .join(GamePlayer, Game.id == GamePlayer.game_id)
            .where(GamePlayer.user_id == user_id)
        )

        # Apply filters
        if status:
            stmt = stmt.where(Game.game_status == status)
        if model_id:
            stmt = stmt.where(Game.model_id == model_id)
        if date_from:
            stmt = stmt.where(Game.created_at >= date_from)
        if date_to:
            stmt = stmt.where(Game.created_at <= date_to)

        # Order by most recent first
        stmt = stmt.order_by(Game.created_at.desc())

        # Count total without pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.db.execute(count_stmt)
        total_count = total.scalar_one()

        # Apply pagination
        stmt = stmt.offset(offset).limit(limit)

        # Eager load related data
        stmt = stmt.options(
            selectinload(Game.board_state),
            selectinload(Game.players),
            selectinload(Game.model)
        )

        result = await self.db.execute(stmt)
        games = result.scalars().all()
        return games, total_count
