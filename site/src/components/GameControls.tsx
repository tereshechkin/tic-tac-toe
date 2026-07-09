import React from 'react';

interface GameControlsProps {
  onRestart: () => void;
  onExit: () => void;
  isGameOver: boolean;
  theme: 'light' | 'dark';
}

const GameControls: React.FC<GameControlsProps> = ({
  onRestart,
  onExit,
  isGameOver,
  theme,
}) => {
  const getCardClass = () => {
    return theme === 'dark' ? 'bg-card border-gray-700/30' : 'bg-white border-gray-300';
  };

  return (
    <div className={`p-6 rounded-card shadow-card border ${getCardClass()}`}>
      <h3 className={`text-lg font-bold mb-4 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
        Управление
      </h3>
      
      <div className="space-y-3">
        {isGameOver && (
          <button
            onClick={onRestart}
            className="w-full btn-primary text-center"
          >
            🔄 Повторить игру
          </button>
        )}
        
        <button
          onClick={onExit}
          className="w-full btn-secondary text-center"
        >
          🚪 Выйти
        </button>
      </div>
    </div>
  );
};

export default GameControls;
