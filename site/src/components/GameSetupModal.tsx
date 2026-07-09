import React, { useState, useEffect } from 'react';

interface GameSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartGame: (config: any) => void;
}

type GameMode = 'computer' | 'friend';
type BoardSize = 3 | 5 | 10 | 30;
type WinSequence = 3 | 4 | 5;
type Difficulty = 'easy' | 'medium' | 'hard';

interface ModelResponse {
  id: string;
  name: string;
  description: string | null;
  type: 'reasoning' | 'non-reasoning';
  enabled: boolean;
  manufacturer: string | null;
  release_date: string | null;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

export const GameSetupModal: React.FC<GameSetupModalProps> = ({ isOpen, onClose, onStartGame }) => {
  const [gameMode, setGameMode] = useState<GameMode>('computer');
  const [selectedModelId, setSelectedModelId] = useState<string>('');
  const [selectedModelName, setSelectedModelName] = useState<string>('');
  const [boardSize, setBoardSize] = useState<BoardSize>(3);
  const [winSequence, setWinSequence] = useState<WinSequence>(3);
  const [difficulty, setDifficulty] = useState<Difficulty>('medium');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [models, setModels] = useState<ModelResponse[]>([]);
  const [loadingModels, setLoadingModels] = useState(false);

  // Загрузка списка моделей при открытии модалки
  useEffect(() => {
    if (isOpen) {
      const fetchModels = async () => {
        setLoadingModels(true);
        setError('');
        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/models`);
          if (!response.ok) {
            throw new Error('Не удалось загрузить список моделей');
          }
          const data = await response.json();
          if (data.models && Array.isArray(data.models)) {
            setModels(data.models);
            // Выбираем первую включённую модель или первую вообще
            const enabled = data.models.find((m: ModelResponse) => m.enabled);
            const first = data.models[0];
            const selected = enabled || first;
            if (selected) {
              setSelectedModelId(selected.id);
              setSelectedModelName(selected.name);
            }
          }
        } catch (err: any) {
          setError(err.message || 'Ошибка загрузки моделей');
        } finally {
          setLoadingModels(false);
        }
      };
      fetchModels();
    }
  }, [isOpen]);

  const boardSizes: BoardSize[] = [3, 5, 10, 30];
  const winSequences: WinSequence[] = [3, 4, 5];
  const difficultyLevels: { value: Difficulty; label: string }[] = [
    { value: 'easy', label: 'Легкий' },
    { value: 'medium', label: 'Средний' },
    { value: 'hard', label: 'Сложный' },
  ];

  const handleStartGame = async () => {
    setError('');
    setIsLoading(true);

    // Для режима friend модель не нужна
    const modelId = gameMode === 'computer' ? selectedModelId : null;
    const modelName = gameMode === 'computer' ? selectedModelName : null;

    const requestBody = {
      board_size: boardSize,
      win_sequence: winSequence,
      game_mode: gameMode,
      model_id: modelId,
      difficulty: gameMode === 'computer' ? difficulty : null,
      player_x_name: 'Игрок',
      player_o_name: gameMode === 'computer' ? 'Компьютер' : 'Друг',
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/games`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        let errorMsg = 'Ошибка создания игры';
        try {
          const data = await response.json();
          if (data.detail) {
            if (Array.isArray(data.detail)) {
              errorMsg = data.detail.map((d: any) => d.msg).join(', ');
            } else {
              errorMsg = data.detail;
            }
          }
        } catch (e) { /* ignore */ }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      const sessionId = data.session_id;

      const config = {
        gameMode,
        modelId: modelId,
        modelName: modelName || 'Модель',
        boardSize,
        winSequence,
        difficulty,
        playerX: 'Игрок',
        playerO: gameMode === 'computer' ? 'Компьютер' : 'Друг',
        sessionId,
      };
      onStartGame(config);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Ошибка соединения с сервером');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl rounded-2xl bg-primary-light p-8 shadow-2xl border border-gray-700/50">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-400 hover:text-white transition-colors duration-200"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <h2 className="mb-6 text-2xl font-bold text-white">Настройка игры</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 text-red-400 rounded-button text-sm">
            {error}
          </div>
        )}

        <div className="space-y-6">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-300">Режим игры</label>
            <div className="flex gap-4">
              <button
                onClick={() => setGameMode('computer')}
                className={`flex-1 rounded-button px-4 py-3 text-center font-semibold transition-all duration-300 ${
                  gameMode === 'computer'
                    ? 'bg-accent text-primary shadow-button hover:shadow-glow hover:scale-105'
                    : 'bg-primary border border-gray-600 text-gray-300 hover:border-accent hover:bg-primary-light'
                }`}
              >
                🤖 Играть с компьютером
              </button>
              <button
                onClick={() => setGameMode('friend')}
                className={`flex-1 rounded-button px-4 py-3 text-center font-semibold transition-all duration-300 ${
                  gameMode === 'friend'
                    ? 'bg-accent text-primary shadow-button hover:shadow-glow hover:scale-105'
                    : 'bg-primary border border-gray-600 text-gray-300 hover:border-accent hover:bg-primary-light'
                }`}
              >
                👥 Играть с другом
              </button>
            </div>
          </div>

          {gameMode === 'computer' && (
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-300">Выберите LLM модель</label>
              {loadingModels ? (
                <div className="text-gray-400">Загрузка моделей...</div>
              ) : (
                <select
                  value={selectedModelId}
                  onChange={(e) => {
                    const id = e.target.value;
                    const model = models.find(m => m.id === id);
                    setSelectedModelId(id);
                    setSelectedModelName(model ? model.name : '');
                  }}
                  className="w-full rounded-button border border-gray-600 bg-primary px-4 py-3 text-white focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all duration-200"
                >
                  {models.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.name} {!model.enabled && '(отключена)'} — {model.manufacturer || 'Неизвестный производитель'}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-300">Размер поля</label>
            <div className="flex flex-wrap gap-3">
              {boardSizes.map((size) => (
                <button
                  key={size}
                  onClick={() => setBoardSize(size)}
                  className={`rounded-button px-6 py-2 font-medium transition-all duration-300 ${
                    boardSize === size
                      ? 'bg-accent text-primary shadow-button hover:shadow-glow hover:scale-105'
                      : 'bg-primary border border-gray-600 text-gray-300 hover:border-accent hover:bg-primary-light'
                  }`}
                >
                  {size}×{size}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-300">
              Длина победной последовательности
            </label>
            <div className="flex flex-wrap gap-3">
              {winSequences.map((seq) => (
                <button
                  key={seq}
                  onClick={() => setWinSequence(seq)}
                  className={`rounded-button px-6 py-2 font-medium transition-all duration-300 ${
                    winSequence === seq
                      ? 'bg-accent text-primary shadow-button hover:shadow-glow hover:scale-105'
                      : 'bg-primary border border-gray-600 text-gray-300 hover:border-accent hover:bg-primary-light'
                  }`}
                >
                  {seq}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-300">Уровень сложности</label>
            <div className="flex flex-wrap gap-3">
              {difficultyLevels.map((level) => (
                <button
                  key={level.value}
                  onClick={() => setDifficulty(level.value)}
                  className={`flex-1 rounded-button px-6 py-2 font-medium transition-all duration-300 ${
                    difficulty === level.value
                      ? 'bg-accent text-primary shadow-button hover:shadow-glow hover:scale-105'
                      : 'bg-primary border border-gray-600 text-gray-300 hover:border-accent hover:bg-primary-light'
                  }`}
                >
                  {level.label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleStartGame}
            disabled={isLoading || loadingModels}
            className="mt-4 w-full btn-primary text-center text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Создание игры...' : '🚀 Запустить игру'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameSetupModal;
