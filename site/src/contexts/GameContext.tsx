import React, { createContext, useContext, useState, ReactNode } from 'react';

interface GameContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  boardSize: number;
  winSequence: number;
  setGameConfig: (boardSize: number, winSequence: number) => void;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export const GameProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [boardSize, setBoardSize] = useState(3);
  const [winSequence, setWinSequence] = useState(3);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const setGameConfig = (size: number, sequence: number) => {
    setBoardSize(size);
    setWinSequence(sequence);
  };

  return (
    <GameContext.Provider value={{ theme, toggleTheme, boardSize, winSequence, setGameConfig }}>
      {children}
    </GameContext.Provider>
  );
};

export const useGame = () => {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
};
