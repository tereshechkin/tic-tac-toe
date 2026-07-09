import React from 'react';

interface GameStatusProps {
  status: string;
  filledPercent: number;
  startTime: Date;
  elapsedTime: string;
  moveCount: number;
  isGameOver: boolean;
  onRestart: () => void;
  onExit: () => void;
  theme: 'light' | 'dark';
}

const GameStatus: React.FC<GameStatusProps> = ({
  status,
  filledPercent,
  startTime,
  elapsedTime,
  moveCount,
  isGameOver,
  onRestart,
  onExit,
  theme,
}) => {
  const getStatusColor = () => {
    if (status.includes('Победа')) return 'text-green-400';
    if (status === 'Ничья') return 'text-yellow-400';
    if (status.includes('Ожидание')) return 'text-orange-400';
    return 'text-accent';
  };

  const getCardClass = () => {
    return theme === 'dark' ? 'bg-card border-gray-700/30' : 'bg-white border-gray-300';
  };

  const getTextClass = () => {
    return theme === 'dark' ? 'text-gray-300' : 'text-gray-700';
  };

  return (
    <div className={`p-6 rounded-card shadow-card border ${getCardClass()}`}>
      <h3 className={`text-lg font-bold mb-4 ${getTextClass()}`}>Статус игры</h3>
      
      <div className="space-y-4">
        <div>
          <p className={`text-sm ${getTextClass()}`}>Текущий статус</p>
          <p className={`text-lg font-semibold ${getStatusColor()}`}>{status}</p>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className={getTextClass()}>Клеток заполнено</span>
            <span className={`font-semibold ${getTextClass()}`}>{filledPercent}%</span>
          </div>
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-accent transition-all duration-500"
              style={{ width: `${filledPercent}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-700/30">
          <div>
            <p className={`text-xs ${getTextClass()}`}>Начало игры</p>
            <p className={`text-sm font-medium ${getTextClass()}`}>
              {startTime.toLocaleTimeString()}
            </p>
          </div>
          <div>
            <p className={`text-xs ${getTextClass()}`}>Продолжительность</p>
            <p className={`text-sm font-mono font-medium ${getTextClass()}`}>{elapsedTime}</p>
          </div>
          <div className="col-span-2">
            <p className={`text-xs ${getTextClass()}`}>Сделано ходов</p>
            <p className={`text-sm font-medium ${getTextClass()}`}>{moveCount}</p>
          </div>
        </div>

        <div className="flex gap-3 pt-2 border-t border-gray-700/30">
          {isGameOver && (
            <button
              onClick={onRestart}
              className="flex-1 btn-primary text-sm py-2"
            >
              🔄 Повторить игру
            </button>
          )}
          <button
            onClick={onExit}
            className={`flex-1 ${isGameOver ? 'btn-secondary' : 'btn-primary'} text-sm py-2`}
          >
            🚪 Выйти
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameStatus;
