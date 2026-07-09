import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from app.core.cache import cache
from app.core.exceptions import NotFoundException, ValidationException, ConflictException
from app.modules.game_engine.logic import (
    create_empty_board,
    is_valid_move,
    make_move,
    check_winner,
    get_available_moves,
    is_board_full,
)
from app.modules.game_engine.schemas import (
    GameState,
    GameCreateRequest,
    MoveRequest,
    MoveHistoryItem,
    GameCreateResponse,
)
from app.modules.game_engine.websocket_manager import WebSocketManager
from app.modules.llm_manager.service import LLMManagerService
from app.modules.game_engine.repository import GameRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GameEngineService:
    def __init__(
        self,
        websocket_manager: WebSocketManager,
        llm_manager: LLMManagerService,
        game_repo: GameRepository,
    ):
        self.ws_manager = websocket_manager
        self.llm_manager = llm_manager
        self.repo = game_repo

    def _redis_key(self, session_id: UUID) -> str:
        return f"game:{session_id}"

    async def _get_state_from_redis(self, session_id: UUID) -> Optional[GameState]:
        key = self._redis_key(session_id)
        data = await cache.get(key)
        if not data:
            return None
        return GameState.from_redis_dict(json.loads(data))

    async def _save_state_to_redis(self, game_state: GameState) -> None:
        key = self._redis_key(game_state.session_id)
        await cache.set(key, json.dumps(game_state.to_redis_dict()), ttl=86400)  # 24 hours

    async def _save_to_db(self, game_state: GameState) -> None:
        """Asynchronously save to PostgreSQL (stub with await)."""
        await self.repo.save_game_state(game_state.to_redis_dict())

    async def create_game(self, request: GameCreateRequest) -> GameCreateResponse:
        """Create a new game session."""
        session_id = uuid.uuid4()
        board = create_empty_board(request.board_size)

        # Determine player names
        player_x_name = request.player_x_name or "Player X"
        if request.game_mode == "computer":
            # For computer mode, O is the computer
            player_o_name = request.player_o_name or "Computer"
            # Maybe use model name? Not needed now.
        else:
            player_o_name = request.player_o_name or "Player O"

        game_state = GameState(
            session_id=session_id,
            board=board,
            board_size=request.board_size,
            win_sequence=request.win_sequence,
            game_mode=request.game_mode,
            status="in_progress",  # or waiting? We'll set in_progress
            current_turn="X",  # X starts
            player_x_name=player_x_name,
            player_o_name=player_o_name,
            model_id=request.model_id,
            difficulty=request.difficulty,
            winner=None,
            winning_cells=None,
            move_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            finished_at=None,
            move_history=[],
        )

        await self._save_state_to_redis(game_state)
        # Save to DB immediately for persistence
        await self._save_to_db(game_state)
        logger.info(f"Game created: {session_id}")

        return GameCreateResponse(session_id=session_id)

    async def get_game_state(self, session_id: UUID) -> GameState:
        state = await self._get_state_from_redis(session_id)
        if not state:
            raise NotFoundException("Game session not found")
        return state

    async def make_move(self, session_id: UUID, player: str, row: int, col: int) -> GameState:
        """Process a player move."""
        state = await self._get_state_from_redis(session_id)
        if not state:
            raise NotFoundException("Game session not found")

        if state.status == "finished":
            raise ValidationException("Game already finished")

        if state.current_turn != player:
            raise ValidationException(f"Not {player}'s turn")

        if not is_valid_move(state.board, row, col):
            raise ValidationException("Invalid move")

        # Apply move
        new_board = make_move(state.board, row, col, player)
        state.board = new_board
        state.move_count += 1
        state.updated_at = datetime.utcnow()

        # Check winner
        winner, winning_cells = check_winner(state.board, state.win_sequence, row, col, player)
        if winner:
            state.winner = winner
            state.winning_cells = winning_cells
            state.status = "finished"
            state.finished_at = datetime.utcnow()
            state.current_turn = None
        elif state.move_count == state.board_size * state.board_size:
            # Draw
            state.winner = "draw"
            state.status = "finished"
            state.finished_at = datetime.utcnow()
            state.current_turn = None
        else:
            # Switch turn
            state.current_turn = "O" if player == "X" else "X"

        # Add to history
        state.move_history.append(MoveHistoryItem(player=player, row=row, col=col))

        # Save state to Redis and DB (write-behind: save to DB asynchronously)
        await self._save_state_to_redis(state)
        await self._save_to_db(state)

        # Broadcast events
        await self.ws_manager.broadcast_move_made(str(session_id), player, row, col)
        await self.ws_manager.broadcast_game_state(str(session_id), state.to_redis_dict())

        if state.status == "finished":
            await self.ws_manager.broadcast_game_over(
                str(session_id), state.winner, state.winning_cells
            )

        # If game mode is computer and it's computer's turn, request computer move
        if state.game_mode == "computer" and state.status == "in_progress":
            # Determine if computer is the next player
            computer_player = "O"  # Assuming computer always plays O
            if state.current_turn == computer_player:
                # Request computer move (async) - we can fire and forget or await
                await self._request_computer_move_internal(session_id, state)

        return state

    async def _request_computer_move_internal(self, session_id: UUID, state: GameState) -> None:
        """Internal method to get computer move, without broadcasting thinking?"""
        # Notify clients that computer is thinking
        await self.ws_manager.broadcast_computer_thinking(str(session_id))

        # Get move from LLM
        row, col = await self.llm_manager.get_move(
            board=state.board,
            board_size=state.board_size,
            win_sequence=state.win_sequence,
            player="O",  # computer plays O
            model_id=state.model_id,
            difficulty=state.difficulty,
        )

        # Validate move (should be valid, but double-check)
        if not is_valid_move(state.board, row, col):
            # If invalid, try up to 3 times
            for attempt in range(3):
                logger.warning(f"Invalid computer move ({row},{col}), retry {attempt+1}")
                row, col = await self.llm_manager.get_move(
                    board=state.board,
                    board_size=state.board_size,
                    win_sequence=state.win_sequence,
                    player="O",
                    model_id=state.model_id,
                    difficulty=state.difficulty,
                )
                if is_valid_move(state.board, row, col):
                    break
            else:
                # Still invalid, pick random valid move
                available = get_available_moves(state.board)
                if available:
                    row, col = available[0]  # fallback
                else:
                    # No moves left, but game should have ended
                    raise ValidationException("No valid moves for computer")

        # Apply computer move
        await self.make_move(session_id, "O", row, col)

    async def request_computer_move(self, session_id: UUID) -> GameState:
        """Explicitly request computer move (e.g., from WebSocket)."""
        state = await self._get_state_from_redis(session_id)
        if not state:
            raise NotFoundException("Game session not found")
        if state.status == "finished":
            raise ValidationException("Game already finished")
        if state.game_mode != "computer":
            raise ValidationException("Game mode is not computer")
        if state.current_turn != "O":
            raise ValidationException("Not computer's turn")

        await self._request_computer_move_internal(session_id, state)
        # Return updated state
        return await self._get_state_from_redis(session_id)

    async def restart_game(self, session_id: UUID) -> GameState:
        """Restart a game with same parameters."""
        state = await self._get_state_from_redis(session_id)
        if not state:
            raise NotFoundException("Game session not found")

        # Create new board
        new_board = create_empty_board(state.board_size)
        state.board = new_board
        state.status = "in_progress"
        state.current_turn = "X"
        state.winner = None
        state.winning_cells = None
        state.move_count = 0
        state.finished_at = None
        state.updated_at = datetime.utcnow()
        state.move_history = []

        await self._save_state_to_redis(state)
        await self._save_to_db(state)
        await self.ws_manager.broadcast_game_state(str(session_id), state.to_redis_dict())
        return state

    async def exit_game(self, session_id: UUID) -> None:
        """Exit game without finishing (keep in Redis for later)."""
        state = await self._get_state_from_redis(session_id)
        if not state:
            raise NotFoundException("Game session not found")
        # Save current state to DB before exit
        await self._save_to_db(state)
        logger.info(f"Game {session_id} exited by user")
        # Optionally change status? Not required.
