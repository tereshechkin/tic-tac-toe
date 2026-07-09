from typing import List, Optional, Literal
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel


class LLMMoveRequest(BaseModel):
    board: List[List[Optional[str]]]  # 2D array
    board_size: int
    win_sequence: int
    player: Literal["X", "O"]  # which player the LLM should play
    model_id: Optional[UUID] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None


class LLMMoveResponse(BaseModel):
    row: int
    col: int


class ModelResponse(BaseModel):
    """Response schema for a single LLM model."""
    id: UUID
    name: str
    description: Optional[str] = None
    type: Literal["reasoning", "non-reasoning"]
    enabled: bool
    manufacturer: Optional[str] = None
    release_date: Optional[date] = None


class ModelListResponse(BaseModel):
    """Response schema for list of LLM models."""
    models: List[ModelResponse]
