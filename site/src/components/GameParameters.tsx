import React from 'react';

interface GameParametersProps {
  playerX: string;
  playerO: string;
  difficulty: string;
  winSequence: number;
  boardSize: number;
  model: string;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

const GameParameters: React.FC<GameParametersProps> = ({
  playerX,
  playerO,
  difficulty,
  winSequence,
  boardSize,
  model,
  theme,
  onToggleTheme,
}) => {
  const getCardClass = () => {
    return theme === 'dark' ? 'bg-card border-gray-700/30' : 'bg-white border-gray-300';
  };

  const getTextClass = () => {
    return theme === 'dark' ? 'text-gray-300' : 'text-gray-700';
  };

  const getLabelClass = () => {
    return theme === 'dark' ? 'text-gray-400' : 'text-gray-500';
  };

  return (
    <div className={`p-6 rounded-card shadow-card border ${getCardClass()}`}>
      <h3 className={`text-lg font-bold mb-4 ${getTextClass()}`}>Параметры игры</h3>
      
      <div className="space-y-3">
        <div>
          <p className={`text-sm ${getLabelClass()}`}>"X" — игрок</p>
          <p className={`font-medium ${getTextClass()}`}>{playerX}</p>
        </div>
        
        <div>
          <p className={`text-sm ${getLabelClass()}`}>"O" — игрок</p>
          <p className={`font-medium ${getTextClass()}`}>{playerO}</p>
        </div>
        
        <div>
          <p className={`text-sm ${getLabelClass()}`}>Уровень сложности</p>
          <p className={`font-medium ${getTextClass()}`}>{difficulty}</p>
        </div>
        
        <div>
          <p className={`text-sm ${getLabelClass()}`}>Размер победной серии</p>
          <p className={`font-medium ${getTextClass()}`}>{winSequence}</p>
        </div>
        
        <div>
          <p className={`text-sm ${getLabelClass()}`}>Размер поля</p>
          <p className={`font-medium ${getTextClass()}`}>{boardSize}×{boardSize}</p>
        </div>
        
        <div>
          <p className={`text-sm ${getLabelClass()}`}>LLM модель</p>
          <p className={`font-medium ${getTextClass()}`}>{model}</p>
        </div>
        
        <div className="pt-3 border-t border-gray-700/30">
          <div className="flex items-center justify-between">
            <span className={`text-sm ${getLabelClass()}`}>Тема</span>
            <button
              onClick={onToggleTheme}
              className={`px-4 py-2 rounded-button text-sm font-medium transition-all duration-300 ${
                theme === 'dark'
                  ? 'bg-primary-light text-white hover:bg-card-hover'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
              }`}
            >
              {theme === 'dark' ? '🌙 Темная' : '☀️ Светлая'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameParameters;
