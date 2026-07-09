from typing import List, Optional, Tuple


def create_empty_board(size: int) -> List[List[Optional[str]]]:
    """Create a board of given size filled with None."""
    return [[None for _ in range(size)] for _ in range(size)]


def is_valid_move(board: List[List[Optional[str]]], row: int, col: int) -> bool:
    """Check if the move is within bounds and cell is empty."""
    size = len(board)
    if row < 0 or row >= size or col < 0 or col >= size:
        return False
    return board[row][col] is None


def get_available_moves(board: List[List[Optional[str]]]) -> List[Tuple[int, int]]:
    """Return list of available (row, col) moves."""
    size = len(board)
    return [(r, c) for r in range(size) for c in range(size) if board[r][c] is None]


def make_move(
    board: List[List[Optional[str]]], row: int, col: int, player: str
) -> List[List[Optional[str]]]:
    """Apply a move and return a new board (deep copy)."""
    if not is_valid_move(board, row, col):
        raise ValueError("Invalid move")
    # Copy board to avoid mutation
    new_board = [row[:] for row in board]
    new_board[row][col] = player
    return new_board


def check_winner(
    board: List[List[Optional[str]]], win_sequence: int, last_row: int, last_col: int, player: str
) -> Tuple[Optional[str], Optional[List[Tuple[int, int]]]]:
    """
    Check if the last move created a winning line.
    Returns (winner, winning_cells) where winner is 'X' or 'O' or None.
    """
    size = len(board)
    if last_row < 0 or last_row >= size or last_col < 0 or last_col >= size:
        return None, None
    if board[last_row][last_col] != player:
        return None, None

    directions = [
        (0, 1),   # horizontal
        (1, 0),   # vertical
        (1, 1),   # diagonal down-right
        (1, -1),  # diagonal down-left
    ]

    for dr, dc in directions:
        cells = [(last_row, last_col)]
        # Check forward
        for step in range(1, win_sequence):
            r = last_row + dr * step
            c = last_col + dc * step
            if not (0 <= r < size and 0 <= c < size) or board[r][c] != player:
                break
            cells.append((r, c))
        # Check backward
        for step in range(1, win_sequence):
            r = last_row - dr * step
            c = last_col - dc * step
            if not (0 <= r < size and 0 <= c < size) or board[r][c] != player:
                break
            cells.append((r, c))
        if len(cells) >= win_sequence:
            return player, cells[:win_sequence]

    return None, None


def is_board_full(board: List[List[Optional[str]]]) -> bool:
    """Check if all cells are filled."""
    return all(cell is not None for row in board for cell in row)
