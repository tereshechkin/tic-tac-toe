import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface GameListItem {
  sessionId: string;
  createdAt: string;
  opponentName: string;
  opponentType: 'LLM' | 'friend';
  boardSize: number;
  difficulty: 'easy' | 'medium' | 'hard' | null;
  firstMove: 'player' | 'ai' | 'friend';
  currentMove: 'player' | 'ai' | 'friend' | null;
  status: 'waiting' | 'in_progress' | 'finished';
  winner: 'X' | 'O' | 'draw' | null;
  modelId: string | null;
  progress: number;
}

interface GameCarouselProps {
  onContinueGame: (sessionId: string) => void;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

const GameCarousel: React.FC<GameCarouselProps> = ({ onContinueGame }) => {
  const { isAuthenticated, accessToken } = useAuth();
  const [games, setGames] = useState<GameListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const carouselRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const fetchGames = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/games?limit=100`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        if (!response.ok) {
          throw new Error('Не удалось загрузить историю игр');
        }
        const data = await response.json();
        setGames(data.items || []);
      } catch (err: any) {
        setError(err.message || 'Ошибка загрузки');
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, [isAuthenticated, accessToken]);

  const scrollLeft = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const scrollRight = () => {
    if (currentIndex < games.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  if (loading) {
    return (
      <section className="py-12 bg-primary/50">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold mb-6 text-center">📋 История игр</h2>
          <div className="text-center text-gray-400">Загрузка...</div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="py-12 bg-primary/50">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold mb-6 text-center">📋 История игр</h2>
          <div className="text-center text-red-400">{error}</div>
        </div>
      </section>
    );
  }

  if (games.length === 0) {
    return (
      <section className="py-12 bg-primary/50">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold mb-6 text-center">📋 История игр</h2>
          <div className="card p-8 text-center max-w-md mx-auto">
            <p className="text-gray-400 text-lg">
              Вы ещё не играли. Начните первую игру!
            </p>
          </div>
        </div>
      </section>
    );
  }

  const currentGame = games[currentIndex];

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getDifficultyLabel = (difficulty: string | null) => {
    if (!difficulty) return '—';
    const map: Record<string, string> = {
      easy: 'Лёгкий',
      medium: 'Средний',
      hard: 'Сложный',
    };
    return map[difficulty] || difficulty;
  };

  const getFirstMoveLabel = (firstMove: string) => {
    const map: Record<string, string> = {
      player: 'Вы первый',
      ai: 'AI первый',
      friend: 'Друг первый',
    };
    return map[firstMove] || firstMove;
  };

  const getStatusLabel = (status: string) => {
    const map: Record<string, string> = {
      waiting: 'Ожидание',
      in_progress: 'В процессе',
      finished: 'Завершена',
    };
    return map[status] || status;
  };

  return (
    <section className="py-12 bg-primary/50">
      <div className="container mx-auto px-4">
        <h2 className="text-2xl font-bold mb-6 text-center">📋 История игр</h2>

        <div className="relative max-w-4xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={scrollLeft}
              disabled={currentIndex === 0}
              className="p-2 rounded-full bg-card hover:bg-card-hover disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <div className="flex-1" ref={carouselRef}>
              <div className="card p-6 transition-all duration-300">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-400">Дата и время</div>
                    <div className="font-semibold">
                      {formatDate(currentGame.createdAt)} {formatTime(currentGame.createdAt)}
                    </div>

                    <div className="text-sm text-gray-400 mt-3">Противник</div>
                    <div className="font-semibold flex items-center gap-2">
                      {currentGame.opponentType === 'LLM' ? '🤖' : '👤'}
                      {currentGame.opponentName}
                    </div>

                    <div className="text-sm text-gray-400 mt-3">Параметры</div>
                    <div className="text-sm">
                      {currentGame.boardSize}×{currentGame.boardSize} • {getDifficultyLabel(currentGame.difficulty)} • {getFirstMoveLabel(currentGame.firstMove)}
                    </div>

                    <div className="text-sm text-gray-400 mt-3">Статус</div>
                    <div className="text-sm font-medium">
                      {getStatusLabel(currentGame.status)}
                      {currentGame.winner && currentGame.status === 'finished' && (
                        <span className="ml-2 text-green-400">
                          {currentGame.winner === 'draw' ? 'Ничья' : `Победил ${currentGame.winner}`}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col justify-between">
                    <div>
                      <div className="text-sm text-gray-400">Прогресс</div>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-accent transition-all duration-500"
                            style={{ width: `${currentGame.progress}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold">{currentGame.progress}%</span>
                      </div>
                    </div>

                    {currentGame.status !== 'finished' && (
                      <button
                        onClick={() => onContinueGame(currentGame.sessionId)}
                        className="btn-primary text-sm py-2 px-4 mt-3"
                      >
                        ▶ Продолжить
                      </button>
                    )}

                    {currentGame.status === 'finished' && (
                      <div className="text-sm text-green-400 mt-3">✅ Завершена</div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={scrollRight}
              disabled={currentIndex === games.length - 1}
              className="p-2 rounded-full bg-card hover:bg-card-hover disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <div className="text-center mt-4 text-sm text-gray-400">
            {currentIndex + 1} / {games.length}
          </div>
        </div>
      </div>
    </section>
  );
};

export default GameCarousel;
