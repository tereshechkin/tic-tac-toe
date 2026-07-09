from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Integer, CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class LLMModel(Base):
    __tablename__ = "game_llm_models"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    model_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    model_type: Mapped[str] = mapped_column(String(20), nullable=False)  # reasoning / non-reasoning
    manufacturer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    release_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    games: Mapped[list["Game"]] = relationship(back_populates="model")


class Game(Base):
    __tablename__ = "game"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    board_size: Mapped[int] = mapped_column(Integer, nullable=False)
    win_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    game_mode: Mapped[str] = mapped_column(String(20), nullable=False)  # computer / friend
    game_status: Mapped[str] = mapped_column(String(20), nullable=False)  # waiting / in_progress / finished
    model_id: Mapped[UUID | None] = mapped_column(ForeignKey("game_llm_models.id"), nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)  # easy / medium / hard
    winner: Mapped[str | None] = mapped_column(String(5), nullable=True)  # X / O / draw
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(game_mode = 'computer' AND difficulty IN ('easy', 'medium', 'hard')) OR "
            "(game_mode = 'friend' AND difficulty IS NULL)",
            name="ck_game_difficulty"
        ),
        CheckConstraint("board_size IN (3,5,10,30)", name="ck_board_size"),
        CheckConstraint("win_sequence IN (3,4,5)", name="ck_win_sequence"),
        CheckConstraint("game_mode IN ('computer','friend')", name="ck_game_mode"),
        CheckConstraint("game_status IN ('waiting','in_progress','finished')", name="ck_game_status"),
        CheckConstraint("winner IN ('X','O','draw',NULL)", name="ck_winner"),
    )

    model: Mapped["LLMModel"] = relationship(back_populates="games")
    players: Mapped[list["GamePlayer"]] = relationship(back_populates="game")
    board_state: Mapped["GameBoard"] = relationship(back_populates="game", uselist=False)
    moves: Mapped[list["GameMove"]] = relationship(back_populates="game")
    winning_cells: Mapped[list["GameWinningCell"]] = relationship(back_populates="game")


class GamePlayer(Base):
    __tablename__ = "game_player"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("game.id"), nullable=False, index=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("idm_user.id"), nullable=True, index=True)
    guest_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("idm_session.id"), nullable=False, index=True)
    player_type: Mapped[str] = mapped_column(String(20), nullable=False)  # first_player / second_player
    player_sign: Mapped[str] = mapped_column(String(1), nullable=False)  # X / O
    player_name: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        CheckConstraint("player_type IN ('first_player','second_player')", name="ck_player_type"),
        CheckConstraint("player_sign IN ('X','O')", name="ck_player_sign"),
        UniqueConstraint("game_id", "player_sign", name="idx_game_player_game_sign"),
    )

    game: Mapped["Game"] = relationship(back_populates="players")
    moves: Mapped[list["GameMove"]] = relationship(back_populates="player")


class GameBoard(Base):
    __tablename__ = "game_board"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("game.id"), unique=True, nullable=False, index=True)
    board: Mapped[dict] = mapped_column(JSONB, nullable=False)  # 2D array
    move_count: Mapped[int] = mapped_column(Integer, default=0)
    current_turn: Mapped[str | None] = mapped_column(String(1), nullable=True)  # X / O
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("current_turn IN ('X','O',NULL)", name="ck_current_turn"),
    )

    game: Mapped["Game"] = relationship(back_populates="board_state")


class GameMove(Base):
    __tablename__ = "game_moves"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("game.id"), nullable=False, index=True)
    player_id: Mapped[UUID] = mapped_column(ForeignKey("game_player.id"), nullable=False, index=True)
    row_position: Mapped[int] = mapped_column(Integer, nullable=False)
    col_position: Mapped[int] = mapped_column(Integer, nullable=False)
    move_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("game_id", "move_number", name="uq_game_moves_game_id_move_number"),
    )

    game: Mapped["Game"] = relationship(back_populates="moves")
    player: Mapped["GamePlayer"] = relationship(back_populates="moves")


class GameWinningCell(Base):
    __tablename__ = "game_winning_cells"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("game.id"), nullable=False, index=True)
    row_position: Mapped[int] = mapped_column(Integer, nullable=False)
    col_position: Mapped[int] = mapped_column(Integer, nullable=False)

    game: Mapped["Game"] = relationship(back_populates="winning_cells")
