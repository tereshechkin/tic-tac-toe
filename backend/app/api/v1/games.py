from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.modules.game_engine import GameEngineService, GameCreateRequest, GameCreateResponse
from app.modules.game_engine.schemas import GameState, MoveRequest
from app.modules.game_repository import GameListService, GameListResponse
from app.dependencies import get_game_engine_service, get_current_user, get_game_list_service
from app.core.exceptions import AppException
from app.modules.idm.schemas import UserResponse

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    request: Request,
    data: GameCreateRequest,
    game_engine: GameEngineService = Depends(get_game_engine_service),
):
    """Create a new game session."""
    try:
        response = await game_engine.create_game(data)
        return response
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("", response_model=GameListResponse)
async def list_user_games(
    current_user: UserResponse = Depends(get_current_user),
    game_list_service: GameListService = Depends(get_game_list_service),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, regex="^(waiting|in_progress|finished)$"),
    model_id: Optional[UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    """
    Get list of games for the current user with pagination and filters.
    """
    return await game_list_service.get_user_games(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        status=status,
        model_id=model_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{session_id}", response_model=GameState)
async def get_game(
    session_id: UUID,
    game_engine: GameEngineService = Depends(get_game_engine_service),
):
    """Get current game state."""
    try:
        state = await game_engine.get_game_state(session_id)
        return state
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{session_id}/move", response_model=GameState)
async def make_move(
    session_id: UUID,
    move_data: MoveRequest,
    game_engine: GameEngineService = Depends(get_game_engine_service),
):
    """Make a move in the game."""
    try:
        state = await game_engine.make_move(
            session_id=session_id,
            player=move_data.player,
            row=move_data.row,
            col=move_data.col,
        )
        return state
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{session_id}/computer-move", response_model=GameState)
async def request_computer_move(
    session_id: UUID,
    game_engine: GameEngineService = Depends(get_game_engine_service),
):
    """Request computer move (for computer mode)."""
    try:
        state = await game_engine.request_computer_move(session_id)
        return state
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{session_id}/restart", response_model=GameState)
async def restart_game(
    session_id: UUID,
    game_engine: GameEngineService = Depends(get_game_engine_service),
):
    """Restart the game with same parameters."""
    try:
        state = await game_engine.restart_game(session_id)
        return state
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{session_id}/exit", status_code=status.HTTP_200_OK)
async def exit_game(
    session_id: UUID,
    game_engine: GameEngineService = Depends(get_game_engine_service),
):
    """Exit game (keep state for later)."""
    try:
        await game_engine.exit_game(session_id)
        return {"message": "Game exited"}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
