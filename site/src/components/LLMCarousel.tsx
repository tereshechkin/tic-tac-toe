import React, { useState, useEffect, useRef } from 'react';

interface Model {
  id: string;
  name: string;
  manufacturer: string | null;
  release_date: string | null;
  description: string | null;
  type: 'reasoning' | 'non-reasoning';
  enabled: boolean;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

const LLMCarousel: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    const fetchModels = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/models`);
        if (!response.ok) {
          throw new Error('Не удалось загрузить модели');
        }
        const data = await response.json();
        if (data.models && Array.isArray(data.models)) {
          setModels(data.models);
        }
      } catch (err: any) {
        setError(err.message || 'Ошибка загрузки');
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, []);

  const scrollLeft = () => {
    if (models.length === 0) return;
    setCurrentIndex((prev) => (prev === 0 ? models.length - 1 : prev - 1));
  };

  const scrollRight = () => {
    if (models.length === 0) return;
    setCurrentIndex((prev) => (prev === models.length - 1 ? 0 : prev + 1));
  };

  useEffect(() => {
    if (!isHovered && models.length > 0) {
      intervalRef.current = setInterval(scrollRight, 5000);
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isHovered, models.length]);

  if (loading) {
    return (
      <section className="py-16 bg-primary-dark">
        <div className="container mx-auto px-4 text-center text-gray-400">Загрузка моделей...</div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="py-16 bg-primary-dark">
        <div className="container mx-auto px-4 text-center text-red-400">{error}</div>
      </section>
    );
  }

  if (models.length === 0) {
    return (
      <section className="py-16 bg-primary-dark">
        <div className="container mx-auto px-4 text-center text-gray-400">Нет доступных моделей</div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-primary-dark">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-4">
          🤖 Используемые LLM модели
        </h2>
        <p className="text-center text-gray-400 mb-12">
          Выберите модель AI для игры
        </p>

        <div
          className="relative max-w-5xl mx-auto"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <div className="flex items-center gap-4">
            <button
              onClick={scrollLeft}
              className="p-3 rounded-full bg-card hover:bg-card-hover transition-all duration-200 shadow-lg hover:shadow-glow"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <div className="flex-1 overflow-hidden">
              <div
                className="flex transition-transform duration-500 ease-in-out"
                style={{ transform: `translateX(-${currentIndex * 100}%)` }}
              >
                {models.map((model) => (
                  <div key={model.id} className="w-full flex-shrink-0 px-2">
                    <div className="card p-6 text-center border border-gray-700/30 hover:border-accent/50 transition-all duration-300">
                      <div className="text-5xl mb-4">{model.type === 'reasoning' ? '🧠' : '⚡'}</div>
                      <h3 className="text-xl font-bold mb-1">{model.name}</h3>
                      <p className="text-sm text-gray-400 mb-2">{model.manufacturer || 'Неизвестный производитель'}</p>
                      <p className="text-sm text-gray-500 mb-4">
                        {model.release_date ? `Обновление: ${model.release_date}` : 'Дата релиза неизвестна'}
                      </p>
                      <div className="flex flex-wrap gap-2 justify-center">
                        <span className="px-3 py-1 text-xs bg-accent/10 text-accent-light rounded-full border border-accent/20">
                          {model.type === 'reasoning' ? 'Рассуждающая' : 'Без рассуждения'}
                        </span>
                        <span className={`px-3 py-1 text-xs rounded-full border ${model.enabled ? 'bg-green-500/10 text-green-400 border-green-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'}`}>
                          {model.enabled ? 'Доступна' : 'Отключена'}
                        </span>
                      </div>
                      {model.description && (
                        <p className="mt-3 text-sm text-gray-400 border-t border-gray-700/30 pt-3">
                          {model.description}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={scrollRight}
              className="p-3 rounded-full bg-card hover:bg-card-hover transition-all duration-200 shadow-lg hover:shadow-glow"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <div className="flex justify-center gap-2 mt-6">
            {models.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentIndex(idx)}
                className={`h-2 rounded-full transition-all duration-300 ${
                  idx === currentIndex ? 'w-8 bg-accent' : 'w-2 bg-gray-600 hover:bg-gray-400'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default LLMCarousel;