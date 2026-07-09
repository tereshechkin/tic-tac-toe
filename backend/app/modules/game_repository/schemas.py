from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal


class GameListItem(BaseModel):
    sessionId: UUID
    createdAt: datetime
    opponentName: str
    opponentType: Literal["LLM", "friend"]
    boardSize: int
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    firstMove: Literal["player", "ai", "friend"]
    currentMove: Optional[Literal["player", "ai", "friend"]] = None
    status: Literal["waiting", "in_progress", "finished"]
    winner: Optional[Literal["X", "O", "draw"]] = None
    modelId: Optional[UUID] = None
    progress: float


class GameListResponse(BaseModel):
    items: list[GameListItem]
    total: int
    limit: int
    offset: int
