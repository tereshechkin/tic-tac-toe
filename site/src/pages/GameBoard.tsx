import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import AuthModal from '../components/AuthModal';
import GameBoard from '../components/GameBoard';
import GameStatus from '../components/GameStatus';
import GameParameters from '../components/GameParameters';
import { GameProvider } from '../contexts/GameContext';

interface GameBoardPageProps {
  sessionId: string;
  initialPlayerX?: string;
  initialPlayerO?: string;
  initialDifficulty?: string;
  modelName?: string;
  onBack?: () => void;
  initialModel?: string;
  initialBoardSize?: number;
  initialWinSequence?: number;
}

interface GameState {
  session_id: string;
  board: ("X" | "O" | null)[][];
  board_size: 3 | 5 | 10 | 30;
  win_sequence: 3 | 4 | 5;
  game_mode: "computer" | "friend";
  status: "waiting" | "in_progress" | "finished";
  current_turn: "X" | "O" | null;
  player_x_name: string;
  player_o_name: string;
  model_id: string | null;
  difficulty: "easy" | "medium" | "hard" | null;
  winner: "X" | "O" | "draw" | null;
  winning_cells: [number, number][] | null;
  move_count: number;
  created_at: string;
  updated_at: string;
  finished_at: string | null;
  move_history: Array<{ player: "X" | "O"; row: number; col: number; timestamp: string }>;
}

interface WsMessage {
  type: string;
  data: any;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';
const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

const GameBoardPageContent: React.FC<GameBoardPageProps> = ({
  sessionId,
  initialPlayerX,
  initialPlayerO,
  initialDifficulty,
  modelName: propModelName,
  initialModel,
  onBack,
  initialBoardSize,
  initialWinSequence,
}) => {
  const { accessToken } = useAuth();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [showExitModal, setShowExitModal] = useState(false);

  const modelDisplayName = propModelName || initialModel || 'Модель';

  const [gameState, setGameState] = useState<GameState | null>(null);
  const [board, setBoard] = useState<(string | null)[][]>([]);
  const [winner, setWinner] = useState<string | null>(null);
  const [winningCells, setWinningCells] = useState<[number, number][]>([]);
  const [isGameOver, setIsGameOver] = useState(false);
  const [gameStatus, setGameStatus] = useState('Загрузка...');
  const [moveCount, setMoveCount] = useState(0);
  const [filledCells, setFilledCells] = useState(0);
  const [totalCells, setTotalCells] = useState(0);
  const [startTime, setStartTime] = useState(new Date());
  const [elapsedTime, setElapsedTime] = useState('00:00:00');
  const [isThinking, setIsThinking] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const [isLoadingState, setIsLoadingState] = useState(true);

  const wsRef = useRef<WebSocket | null>(null);
  const timerRef = useRef<number | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  // Загрузка состояния через REST, если не переданы начальные параметры
  useEffect(() => {
    const loadInitialState = async () => {
      if (initialBoardSize !== undefined && initialWinSequence !== undefined) {
        // Если параметры переданы, используем их и считаем загрузку завершённой
        setIsLoadingState(false);
        return;
      }

      // Иначе загружаем через REST
      try {
        const headers: HeadersInit = {};
        if (accessToken) {
          headers.Authorization = `Bearer ${accessToken}`;
        }
        const response = await fetch(`${API_BASE_URL}/api/v1/games/${sessionId}`, { headers });
        if (!response.ok) {
          throw new Error('Не удалось загрузить состояние игры');
        }
        const state: GameState = await response.json();
        if (isMounted.current) {
          updateGameState(state);
          setIsLoadingState(false);
        }
      } catch (err: any) {
        if (isMounted.current) {
          setConnectionError(err.message || 'Ошибка загрузки состояния');
          setIsLoadingState(false);
        }
      }
    };

    loadInitialState();
  }, [sessionId, initialBoardSize, initialWinSequence, accessToken]);

  useEffect(() => {
    if (gameState?.status === 'in_progress' || gameState?.status === 'waiting') {
      const start = new Date(gameState?.created_at || Date.now());
      setStartTime(start);
      if (timerRef.current) clearInterval(timerRef.current);
      timerRef.current = setInterval(() => {
        const now = new Date();
        const diff = Math.floor((now.getTime() - start.getTime()) / 1000);
        const hours = Math.floor(diff / 3600);
        const minutes = Math.floor((diff % 3600) / 60);
        const seconds = diff % 60;
        setElapsedTime(
          `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
        );
      }, 1000);
    } else if (gameState?.status === 'finished') {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [gameState]);

  const updateGameState = (state: GameState) => {
    if (!isMounted.current) return;
    setGameState(state);
    setBoard(state.board);
    setWinner(state.winner === 'draw' ? null : state.winner);
    setWinningCells(state.winning_cells || []);
    setIsGameOver(state.status === 'finished');
    setMoveCount(state.move_count);
    const filled = state.board.flat().filter(cell => cell !== null).length;
    setFilledCells(filled);
    setTotalCells(state.board_size * state.board_size);

    let statusText = '';
    if (state.status === 'waiting') {
      statusText = 'Ожидание игроков...';
    } else if (state.status === 'in_progress') {
      if (state.current_turn) {
        const playerName = state.current_turn === 'X' ? state.player_x_name : state.player_o_name;
        statusText = `Ход "${state.current_turn}" (${playerName})`;
      } else {
        statusText = 'Игра в процессе...';
      }
    } else if (state.status === 'finished') {
      if (state.winner === 'draw') {
        statusText = 'Ничья';
      } else if (state.winner) {
        const winnerName = state.winner === 'X' ? state.player_x_name : state.player_o_name;
        statusText = `Победа "${state.winner}" (${winnerName})`;
      } else {
        statusText = 'Игра завершена';
      }
    }
    setGameStatus(statusText);
  };

  const handleWsMessage = (event: MessageEvent) => {
    try {
      const message: WsMessage = JSON.parse(event.data);
      switch (message.type) {
        case 'game_state':
          updateGameState(message.data);
          setIsThinking(false);
          break;
        case 'move_made':
          break;
        case 'game_over':
          break;
        case 'computer_thinking':
          setIsThinking(true);
          setGameStatus('Компьютер обдумывает ход...');
          break;
        case 'error':
          setConnectionError(message.data.message || 'Ошибка WebSocket');
          break;
        case 'exit':
          if (wsRef.current) {
            wsRef.current.close(1000, 'Normal closure');
          }
          if (onBack) onBack();
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err);
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);
    setConnectionError(null);

    const wsUrl = `${WS_BASE_URL}/ws/games/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!isMounted.current) return;
      setIsConnecting(false);
      setConnectionError(null);
    };

    ws.onmessage = (event) => {
      if (!isMounted.current) return;
      handleWsMessage(event);
    };

    ws.onerror = (error) => {
      if (!isMounted.current) return;
      if (wsRef.current !== ws) return;
      console.error('WebSocket error:', error);
      setConnectionError('Ошибка соединения с сервером');
      setIsConnecting(false);
    };

    ws.onclose = (event) => {
      if (!isMounted.current) return;
      if (wsRef.current !== ws) return;
      if (event.code !== 1000) {
        if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = setTimeout(() => {
          if (isMounted.current && wsRef.current === ws) {
            connectWebSocket();
          }
        }, 3000);
      }
    };
  };

  useEffect(() => {
    if (sessionId) {
      connectWebSocket();
    }

    return () => {
      if (wsRef.current) {
        const readyState = wsRef.current.readyState;
        if (readyState === WebSocket.OPEN || readyState === WebSocket.CONNECTING) {
          wsRef.current.close(1000, 'Component unmount');
        }
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [sessionId]);

  const handleOpenAuth = () => setIsAuthModalOpen(true);
  const handleCloseAuth = () => setIsAuthModalOpen(false);
  const handleToggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  const handleCellClick = (row: number, col: number) => {
    if (!gameState || gameState.status !== 'in_progress') return;
    if (gameState.current_turn === null) return;
    if (board[row][col] !== null) return;

    const player = gameState.current_turn;
    const message = {
      type: 'make_move',
      player,
      row,
      col,
    };

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      setConnectionError('Соединение потеряно, попробуйте перезагрузить страницу');
    }
  };

  const handleRestart = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'restart' }));
    }
  };

  const handleExit = () => {
    setShowExitModal(true);
  };

  const confirmExit = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'exit' }));
    } else {
      if (onBack) onBack();
    }
    setShowExitModal(false);
  };

  const cancelExit = () => setShowExitModal(false);

  const getPlayerX = gameState?.player_x_name || initialPlayerX || 'Игрок';
  const getPlayerO = gameState?.player_o_name || initialPlayerO || 'Компьютер';
  const getDifficulty = gameState?.difficulty
    ? { easy: 'Лёгкий', medium: 'Средний', hard: 'Сложный' }[gameState.difficulty] || initialDifficulty || 'Средний'
    : initialDifficulty || 'Средний';
  const getModel = modelDisplayName;
  const getBoardSize = gameState?.board_size ?? initialBoardSize ?? 3;
  const getWinSequence = gameState?.win_sequence ?? initialWinSequence ?? 3;

  const boardClass = theme === 'dark' ? 'bg-primary' : 'bg-gray-100';
  const textClass = theme === 'dark' ? 'text-white' : 'text-gray-900';

  if (isLoadingState) {
    return (
      <div className={`min-h-screen ${boardClass} ${textClass} flex items-center justify-center`}>
        <div className="text-center">
          <p className="text-xl">Загрузка игры...</p>
        </div>
      </div>
    );
  }

  if (!gameState && !isConnecting && !connectionError) {
    return (
      <div className={`min-h-screen ${boardClass} ${textClass} flex items-center justify-center`}>
        <div className="text-center">
          <p className="text-xl">Игра не найдена или произошла ошибка</p>
          <button onClick={() => onBack?.()} className="mt-4 btn-primary">
            Вернуться на главную
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${boardClass} ${textClass}`}>
      <Header onLoginClick={handleOpenAuth} />

      <main className="pt-20 pb-12">
        <div className="container mx-auto px-4">
          {connectionError && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 text-red-400 rounded-button text-sm text-center">
              {connectionError}
            </div>
          )}
          {isThinking && (
            <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 rounded-button text-sm text-center animate-pulse">
              🤔 Компьютер думает...
            </div>
          )}

          <div className="flex flex-col lg:flex-row gap-6 justify-center items-start">
            <div className="lg:w-64 w-full">
              <GameParameters
                playerX={getPlayerX}
                playerO={getPlayerO}
                difficulty={getDifficulty}
                winSequence={getWinSequence}
                boardSize={getBoardSize}
                model={getModel}
                theme={theme}
                onToggleTheme={handleToggleTheme}
              />
            </div>

            <div className="flex-1 flex justify-center">
              <GameBoard
                board={board.length ? board : Array(getBoardSize).fill(null).map(() => Array(getBoardSize).fill(null))}
                boardSize={getBoardSize}
                onCellClick={handleCellClick}
                winner={winner}
                winningCells={winningCells}
                theme={theme}
                isGameOver={isGameOver}
              />
            </div>

            <div className="lg:w-64 w-full">
              <GameStatus
                status={gameStatus}
                filledPercent={totalCells > 0 ? Math.round((filledCells / totalCells) * 100) : 0}
                startTime={startTime}
                elapsedTime={elapsedTime}
                moveCount={moveCount}
                isGameOver={isGameOver}
                onRestart={handleRestart}
                onExit={handleExit}
                theme={theme}
              />
            </div>
          </div>
        </div>
      </main>

      <Footer />
      <AuthModal isOpen={isAuthModalOpen} onClose={handleCloseAuth} />

      {showExitModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-primary-light rounded-card shadow-2xl w-full max-w-md p-6 border border-gray-700/50">
            <h3 className="text-xl font-bold mb-4">Подтверждение выхода</h3>
            <p className="text-gray-300 mb-6">
              Вы уверены, что хотите выйти? Игра будет сохранена как незавершенная.
            </p>
            <div className="flex gap-4 justify-end">
              <button onClick={cancelExit} className="btn-secondary text-sm py-2 px-6">
                Отмена
              </button>
              <button onClick={confirmExit} className="btn-primary text-sm py-2 px-6">
                Выйти
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const GameBoardPage: React.FC<GameBoardPageProps> = (props) => {
  return (
    <GameProvider>
      <GameBoardPageContent {...props} />
    </GameProvider>
  );
};

export default GameBoardPage;