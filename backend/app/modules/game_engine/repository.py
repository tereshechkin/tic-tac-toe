from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.game_repository.models import Game, GameBoard, GamePlayer, GameMove, GameWinningCell
from app.modules.idm.models import Session as IDMSession
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_datetime(value):
    """Convert ISO string or datetime to datetime, return None for None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Try common ISO formats
        try:
            # Handle '2026-07-08T14:14:24.923872'
            if '.' in value:
                return datetime.fromisoformat(value)
            else:
                return datetime.fromisoformat(value)
        except ValueError:
            logger.warning(f"Failed to parse datetime string: {value}")
            return datetime.utcnow()
    return datetime.utcnow()


class GameRepository:
    """Repository for persisting game state to PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_game_state(self, game_state: dict) -> None:
        """
        Save or update game state in DB.
        Implements write-behind caching: called asynchronously after game finishes.
        """
        session_id_str = game_state.get('session_id')
        if not session_id_str:
            logger.warning("Cannot save game: missing session_id")
            return

        try:
            session_id = UUID(session_id_str)
        except ValueError:
            logger.warning(f"Invalid session_id format: {session_id_str}")
            return

        # Check if game already exists
        stmt = select(Game).where(Game.id == session_id)
        result = await self.db.execute(stmt)
        existing_game = result.scalar_one_or_none()

        if existing_game:
            # Update existing game
            await self._update_game(session_id, game_state)
        else:
            # Create new game records
            await self._create_game(session_id, game_state)

        logger.info(f"Game {session_id} saved to DB")

    async def _create_game(self, session_id: UUID, game_state: dict) -> None:
        """Create all records for a new game."""
        # 1. Game
        game = Game(
            id=session_id,
            board_size=game_state['board_size'],
            win_sequence=game_state['win_sequence'],
            game_mode=game_state['game_mode'],
            game_status=game_state['status'],
            model_id=game_state.get('model_id'),
            difficulty=game_state.get('difficulty'),
            winner=game_state.get('winner'),
            created_at=parse_datetime(game_state.get('created_at', datetime.utcnow())),
            finished_at=parse_datetime(game_state.get('finished_at')),
        )
        self.db.add(game)
        await self.db.flush()

        # 2. GameBoard
        board = GameBoard(
            game_id=session_id,
            board=game_state['board'],
            move_count=game_state['move_count'],
            current_turn=game_state.get('current_turn'),
            updated_at=parse_datetime(game_state.get('updated_at', datetime.utcnow())),
        )
        self.db.add(board)
        await self.db.flush()

        # 3. Players (X and O)
        player_x_name = game_state.get('player_x_name', 'Player X')
        player_o_name = game_state.get('player_o_name', 'Player O')

        # Create IDM sessions for guest players
        x_session = IDMSession(
            guest_name=player_x_name,
            created_at=datetime.utcnow(),
            ip_address=None,
        )
        self.db.add(x_session)
        await self.db.flush()

        o_session = IDMSession(
            guest_name=player_o_name,
            created_at=datetime.utcnow(),
            ip_address=None,
        )
        self.db.add(o_session)
        await self.db.flush()

        x_player = GamePlayer(
            game_id=session_id,
            user_id=None,
            guest_name=player_x_name,
            session_id=x_session.id,
            player_type='first_player',
            player_sign='X',
            player_name=player_x_name,
        )
        self.db.add(x_player)

        o_player = GamePlayer(
            game_id=session_id,
            user_id=None,
            guest_name=player_o_name,
            session_id=o_session.id,
            player_type='second_player',
            player_sign='O',
            player_name=player_o_name,
        )
        self.db.add(o_player)
        await self.db.flush()

        player_map = {'X': x_player.id, 'O': o_player.id}

        # 4. Moves
        move_history = game_state.get('move_history', [])
        for idx, move in enumerate(move_history, start=1):
            move_obj = GameMove(
                game_id=session_id,
                player_id=player_map[move['player']],
                row_position=move['row'],
                col_position=move['col'],
                move_number=idx,
                created_at=parse_datetime(move.get('timestamp', datetime.utcnow())),
            )
            self.db.add(move_obj)

        # 5. Winning cells
        winning_cells = game_state.get('winning_cells')
        if winning_cells:
            for row, col in winning_cells:
                cell = GameWinningCell(
                    game_id=session_id,
                    row_position=row,
                    col_position=col,
                )
                self.db.add(cell)

        await self.db.commit()

    async def _update_game(self, session_id: UUID, game_state: dict) -> None:
        """Update existing game records (status, board, moves, etc.)."""
        # Update Game
        stmt = select(Game).where(Game.id == session_id)
        result = await self.db.execute(stmt)
        game = result.scalar_one()
        game.game_status = game_state['status']
        game.winner = game_state.get('winner')
        game.finished_at = parse_datetime(game_state.get('finished_at'))
        # If game_mode, board_size, win_sequence don't change, no need to update
        self.db.add(game)

        # Update GameBoard
        stmt = select(GameBoard).where(GameBoard.game_id == session_id)
        result = await self.db.execute(stmt)
        board = result.scalar_one()
        board.board = game_state['board']
        board.move_count = game_state['move_count']
        board.current_turn = game_state.get('current_turn')
        board.updated_at = parse_datetime(game_state.get('updated_at', datetime.utcnow()))
        self.db.add(board)

        # Add new moves (if any)
        # We'll get existing move numbers to avoid duplicates
        stmt = select(GameMove.move_number).where(GameMove.game_id == session_id)
        result = await self.db.execute(stmt)
        existing_move_numbers = {row[0] for row in result.fetchall()}

        # Get player ids
        stmt = select(GamePlayer).where(GamePlayer.game_id == session_id)
        result = await self.db.execute(stmt)
        players = result.scalars().all()
        player_map = {p.player_sign: p.id for p in players}

        move_history = game_state.get('move_history', [])
        for idx, move in enumerate(move_history, start=1):
            if idx in existing_move_numbers:
                continue  # already saved
            move_obj = GameMove(
                game_id=session_id,
                player_id=player_map[move['player']],
                row_position=move['row'],
                col_position=move['col'],
                move_number=idx,
                created_at=parse_datetime(move.get('timestamp', datetime.utcnow())),
            )
            self.db.add(move_obj)

        # Replace winning cells: delete old, insert new
        stmt = select(GameWinningCell).where(GameWinningCell.game_id == session_id)
        result = await self.db.execute(stmt)
        old_cells = result.scalars().all()
        for cell in old_cells:
            await self.db.delete(cell)

        winning_cells = game_state.get('winning_cells')
        if winning_cells:
            for row, col in winning_cells:
                cell = GameWinningCell(
                    game_id=session_id,
                    row_position=row,
                    col_position=col,
                )
                self.db.add(cell)

        await self.db.commit()
