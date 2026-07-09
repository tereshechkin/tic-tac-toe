from typing import List, Optional

def build_prompt(board: List[List[Optional[str]]], board_size: int, win_sequence: int, player: str, difficulty: Optional[str] = None) -> str:
    """
    Build a prompt for LLM to make a move in Tic-Tac-Toe.
    """
    # Convert board to string representation
    board_str = ""
    for row in board:
        row_str = " ".join([cell if cell is not None else "." for cell in row])
        board_str += row_str + "\n"
    
    difficulty_text = ""
    if difficulty:
        difficulty_text = f"Difficulty level: {difficulty}. "
    
    prompt = f"""You are playing Tic-Tac-Toe. Board size is {board_size}x{board_size}. 
You need to win by getting {win_sequence} in a row, column, or diagonal.
Current board (X and O, . means empty):
{board_str}
{difficulty_text}You are playing as '{player}'. 
It's your turn. Please provide only the row and column numbers (0-indexed) where you want to place your '{player}', separated by a space or comma. 
For example: "0 1" or "0,1". 
Do not include any other text or explanation.
Your move:"""
    return prompt
