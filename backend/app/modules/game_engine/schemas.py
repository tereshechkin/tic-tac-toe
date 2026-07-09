from datetime import datetime
from typing import List, Optional, Literal, Tuple
from uuid import UUID
from pydantic import BaseModel, Field


class MoveHistoryItem(BaseModel):
    player: Literal["X", "O"]
    row: int
    col: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GameState(BaseModel):
    session_id: UUID
    board: List[List[Optional[str]]]  # 2D array, values: "X", "O", or None
    board_size: int
    win_sequence: int
    game_mode: Literal["computer", "friend"]
    status: Literal["waiting", "in_progress", "finished"]
    current_turn: Optional[Literal["X", "O"]]
    player_x_name: str
    player_o_name: str
    model_id: Optional[UUID] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    winner: Optional[Literal["X", "O", "draw"]] = None
    winning_cells: Optional[List[Tuple[int, int]]] = None
    move_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    move_history: List[MoveHistoryItem] = []

    def to_redis_dict(self) -> dict:
        """Convert to dict for Redis storage (serialize as JSON)."""
        return self.model_dump(mode="json")

    @classmethod
    def from_redis_dict(cls, data: dict) -> "GameState":
        return cls(**data)


class GameCreateRequest(BaseModel):
    board_size: Literal[3, 5, 10, 30]
    win_sequence: Literal[3, 4, 5]
    game_mode: Literal["computer", "friend"]
    model_id: Optional[UUID] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    player_x_name: str = "Player X"
    player_o_name: str = "Player O"


class GameCreateResponse(BaseModel):
    session_id: UUID


class MoveRequest(BaseModel):
    session_id: UUID
    player: Literal["X", "O"]
    row: int
    col: int


class MoveResponse(BaseModel):
    session_id: UUID
    success: bool
    message: Optional[str] = None
    game_state: Optional[GameState] = None


# WebSocket event types
class WSEvent(BaseModel):
    type: Literal["game_state", "move_made", "game_over", "computer_thinking", "error"]
    data: dict


# For LLM manager
class LLMMoveRequest(BaseModel):
    board: List[List[Optional[str]]]
    board_size: int
    win_sequence: int
    player: Literal["X", "O"]  # which player the LLM should play
    model_id: Optional[UUID] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None


class LLMMoveResponse(BaseModel):
    row: int
    col: int
