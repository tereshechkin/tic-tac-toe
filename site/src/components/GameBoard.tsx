import React from 'react';

interface GameBoardProps {
  board: (string | null)[][];
  boardSize: number;
  onCellClick: (row: number, col: number) => void;
  winner: string | null;
  winningCells: [number, number][];
  theme: 'light' | 'dark';
  isGameOver: boolean;
}

const GameBoard: React.FC<GameBoardProps> = ({
  board,
  boardSize,
  onCellClick,
  winner,
  winningCells,
  theme,
  isGameOver,
}) => {
  const getCellSize = () => {
    if (boardSize <= 3) return 'h-24 w-24';
    if (boardSize <= 5) return 'h-16 w-16';
    if (boardSize <= 10) return 'h-12 w-12';
    return 'h-8 w-8';
  };

  const getTextSize = () => {
    if (boardSize <= 3) return 'text-5xl';
    if (boardSize <= 5) return 'text-3xl';
    if (boardSize <= 10) return 'text-2xl';
    return 'text-xl';
  };

  const isWinningCell = (row: number, col: number): boolean => {
    return winningCells.some(([r, c]) => r === row && c === col);
  };

  const getCellBackground = (row: number, col: number) => {
    const value = board[row][col];
    if (isWinningCell(row, col)) {
      return 'bg-green-500/30 border-green-500';
    }
    if (value === 'X') {
      return theme === 'dark' ? 'bg-blue-500/20 border-blue-400' : 'bg-blue-200 border-blue-400';
    }
    if (value === 'O') {
      return theme === 'dark' ? 'bg-red-500/20 border-red-400' : 'bg-red-200 border-red-400';
    }
    return theme === 'dark' ? 'bg-primary-light border-gray-600 hover:border-accent' : 'bg-gray-200 border-gray-400 hover:border-blue-400';
  };

  const getCellTextColor = (value: string | null) => {
    if (value === 'X') return 'text-blue-400';
    if (value === 'O') return 'text-red-400';
    return '';
  };

  return (
    <div className="flex flex-col items-center">
      <div
        className="grid gap-1 p-4 bg-card rounded-card shadow-card"
        style={{
          gridTemplateColumns: `repeat(${boardSize}, 1fr)`,
          width: boardSize <= 3 ? 'auto' : '100%',
          maxWidth: 600,
        }}
      >
        {board.map((row, rowIndex) =>
          row.map((cell, colIndex) => (
            <button
              key={`${rowIndex}-${colIndex}`}
              onClick={() => onCellClick(rowIndex, colIndex)}
              disabled={!!winner || cell !== null || isGameOver}
              className={`
                ${getCellSize()}
                ${getCellBackground(rowIndex, colIndex)}
                border-2 rounded-button
                flex items-center justify-center
                transition-all duration-200
                hover:scale-105
                disabled:opacity-80 disabled:cursor-not-allowed disabled:hover:scale-100
                relative
              `}
            >
              {cell && (
                <span
                  className={`${getTextSize()} ${getCellTextColor(cell)} font-bold animate-fade-in`}
                >
                  {cell}
                </span>
              )}
              {!cell && !winner && !isGameOver && (
                <span className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-20 transition-opacity duration-200">
                  <span className={`${getTextSize()} font-bold text-gray-400`}>
                    {rowIndex % 2 === 0 ? 'X' : 'O'}
                  </span>
                </span>
              )}
            </button>
          ))
        )}
      </div>

      {winner && (
        <div className="mt-4 p-2 px-6 bg-green-500/20 border border-green-500 rounded-button animate-fade-in">
          <span className="text-green-400 font-bold text-lg">
            🏆 Победил {winner === 'X' ? 'Игрок X' : 'Игрок O'}!
          </span>
        </div>
      )}

      {!winner && isGameOver && (
        <div className="mt-4 p-2 px-6 bg-yellow-500/20 border border-yellow-500 rounded-button animate-fade-in">
          <span className="text-yellow-400 font-bold text-lg">
            🤝 Ничья!
          </span>
        </div>
      )}
    </div>
  );
};

export default GameBoard;
