import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import GameCarousel from './components/GameCarousel';
import Features from './components/Features';
import LLMCarousel from './components/LLMCarousel';
import Footer from './components/Footer';
import AuthModal from './components/AuthModal';
import GameSetupModal from './components/GameSetupModal';
import GameBoardPage from './pages/GameBoard';
import { AuthProvider } from './contexts/AuthContext';

const AppContent: React.FC = () => {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isGameSetupModalOpen, setIsGameSetupModalOpen] = useState(false);
  const [showGameBoard, setShowGameBoard] = useState(false);
  const [gameConfig, setGameConfig] = useState({
    sessionId: '',
    boardSize: 3,
    winSequence: 3,
    playerX: 'Игрок',
    playerO: 'Компьютер',
    difficulty: 'Средний',
    modelName: 'Модель',
  });

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isAuthModalOpen) {
          setIsAuthModalOpen(false);
        }
        if (isGameSetupModalOpen) {
          setIsGameSetupModalOpen(false);
        }
      }
    };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isAuthModalOpen, isGameSetupModalOpen]);

  const handleStartGame = () => {
    setIsGameSetupModalOpen(true);
  };

  const handleOpenAuth = () => {
    setIsAuthModalOpen(true);
  };

  const handleCloseAuth = () => {
    setIsAuthModalOpen(false);
  };

  const handleCloseGameSetup = () => {
    setIsGameSetupModalOpen(false);
  };

  const handleGameStart = (config: any) => {
    setGameConfig({
      sessionId: config.sessionId,
      boardSize: config.boardSize,
      winSequence: config.winSequence,
      playerX: config.playerX,
      playerO: config.playerO,
      difficulty: config.difficulty === 'easy' ? 'Лёгкий' : config.difficulty === 'medium' ? 'Средний' : 'Сложный',
      modelName: config.modelName || 'Модель',
    });
    setShowGameBoard(true);
    setIsGameSetupModalOpen(false);
  };

  const handleContinueGame = (sessionId: string) => {
    // Передаём только sessionId; остальные параметры будут загружены через REST в GameBoardPage
    setGameConfig({
      sessionId,
      boardSize: 3,
      winSequence: 3,
      playerX: '',
      playerO: '',
      difficulty: '',
      modelName: '',
    });
    setShowGameBoard(true);
  };

  const handleBackToHome = () => {
    setShowGameBoard(false);
  };

  if (showGameBoard) {
    return (
      <GameBoardPage
        sessionId={gameConfig.sessionId}
        initialBoardSize={gameConfig.boardSize || undefined}
        initialWinSequence={gameConfig.winSequence || undefined}
        initialPlayerX={gameConfig.playerX || undefined}
        initialPlayerO={gameConfig.playerO || undefined}
        initialDifficulty={gameConfig.difficulty || undefined}
        modelName={gameConfig.modelName || undefined}
        onBack={handleBackToHome}
      />
    );
  }

  return (
    <div className="min-h-screen bg-primary">
      <Header onLoginClick={handleOpenAuth} />
      <main>
        <Hero onStartGame={handleStartGame} onLoginClick={handleOpenAuth} />
        <GameCarousel onContinueGame={handleContinueGame} />
        <Features />
        <LLMCarousel />
      </main>
      <Footer />
      <AuthModal isOpen={isAuthModalOpen} onClose={handleCloseAuth} />
      <GameSetupModal isOpen={isGameSetupModalOpen} onClose={handleCloseGameSetup} onStartGame={handleGameStart} />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;