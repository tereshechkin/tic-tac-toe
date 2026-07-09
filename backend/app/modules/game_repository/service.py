from uuid import UUID
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.game_repository.repository import GameDbRepository
from app.modules.game_repository.schemas import GameListItem, GameListResponse


class GameListService:
    def __init__(self, db: AsyncSession):
        self.repo = GameDbRepository(db)

    async def get_user_games(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        model_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> GameListResponse:
        games, total = await self.repo.get_user_games(
            user_id, limit, offset, status, model_id, date_from, date_to
        )

        items = []
        for game in games:
            # Determine which player is the current user
            user_player = None
            opponent_player = None
            for player in game.players:
                if player.user_id == user_id:
                    user_player = player
                else:
                    opponent_player = player

            if not user_player or not opponent_player:
                continue

            # Opponent type
            if game.game_mode == "computer":
                opponent_type = "LLM"
            else:
                opponent_type = "friend"

            # First move: X always moves first
            if user_player.player_sign == "X":
                first_move = "player"
            else:
                first_move = "ai" if game.game_mode == "computer" else "friend"

            # Current move
            board_state = game.board_state
            current_turn = board_state.current_turn if board_state else None
            if current_turn is None:
                current_move = None
            else:
                if user_player.player_sign == current_turn:
                    current_move = "player"
                else:
                    current_move = "ai" if game.game_mode == "computer" else "friend"

            # Progress: percentage of free cells
            total_cells = game.board_size * game.board_size
            move_count = board_state.move_count if board_state else 0
            free_cells = total_cells - move_count
            progress = (free_cells / total_cells) * 100 if total_cells > 0 else 0.0

            item = GameListItem(
                sessionId=game.id,
                createdAt=game.created_at,
                opponentName=opponent_player.player_name,
                opponentType=opponent_type,
                boardSize=game.board_size,
                difficulty=game.difficulty,
                firstMove=first_move,
                currentMove=current_move,
                status=game.game_status,
                winner=game.winner,
                modelId=game.model_id,
                progress=progress,
            )
            items.append(item)

        return GameListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
