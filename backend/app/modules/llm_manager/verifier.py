import re
from typing import List, Optional, Tuple

def parse_move_response(text: str, board: List[List[Optional[str]]]) -> Optional[Tuple[int, int]]:
    """
    Parse LLM response to extract row and column. Validates that the move is within board and cell is empty.
    Returns (row, col) or None if invalid.
    """
    # Find all numbers in the text
    numbers = re.findall(r'\b\d+\b', text)
    if len(numbers) < 2:
        return None
    # Take first two numbers
    try:
        row = int(numbers[0])
        col = int(numbers[1])
    except ValueError:
        return None
    
    size = len(board)
    if row < 0 or row >= size or col < 0 or col >= size:
        return None
    if board[row][col] is not None:
        return None
    return (row, col)
