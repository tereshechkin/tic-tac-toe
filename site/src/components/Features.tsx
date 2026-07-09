import React, { useState } from 'react';

interface Feature {
  id: string;
  title: string;
  description: string;
  icon: string;
}

const features: Feature[] = [
  {
    id: 'ai',
    title: 'Игра против AI',
    description: 'Выберите LLM-модель для игры: GPT-4o, Claude 3.5 Sonnet, YandexGPT, LLama 3 и другие. Настройте сложность от лёгкой до экспертной, чтобы игра была интересной и развивающей.',
    icon: '🤖',
  },
  {
    id: 'two-player',
    title: 'Игра вдвоём',
    description: 'Режим для двух игроков на одном устройстве. Идеально для игры с друзьями или семьёй. Переключайтесь ходами и наслаждайтесь классической игрой.',
    icon: '👥',
  },
  {
    id: 'history',
    title: 'История партий',
    description: 'Просматривайте все сыгранные игры с полной информацией: дата, время, противник, параметры игры и результат. Анализируйте свои успехи и прогресс.',
    icon: '📚',
  },
  {
    id: 'analysis',
    title: 'Анализ ходов',
    description: 'После окончания игры просмотрите оптимальные ходы и стратегии. Узнайте, где можно было сыграть лучше и улучшите своё мастерство.',
    icon: '📊',
  },
  {
    id: 'themes',
    title: 'Настройки внешнего вида',
    description: 'Выбирайте между светлой и тёмной темой интерфейса. Настраивайте внешний вид под свои предпочтения и комфорт игры.',
    icon: '🎨',
  },
];

const Features: React.FC = () => {
  const [openFeatureId, setOpenFeatureId] = useState<string | null>(null);

  const toggleFeature = (id: string) => {
    setOpenFeatureId(openFeatureId === id ? null : id);
  };

  return (
    <section className="py-16 bg-primary-light/30">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12">
          Что вы можете делать в игре
        </h2>
        
        <div className="max-w-3xl mx-auto space-y-3">
          {features.map((feature) => (
            <div
              key={feature.id}
              className="card overflow-hidden border border-gray-700/30 hover:border-accent/30 transition-all duration-200"
            >
              <button
                onClick={() => toggleFeature(feature.id)}
                className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-primary-light/20 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-opacity-50"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{feature.icon}</span>
                  <span className="font-semibold text-lg">{feature.title}</span>
                </div>
                <svg
                  className={`w-5 h-5 transition-transform duration-300 ${openFeatureId === feature.id ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              <div
                className={`overflow-hidden transition-all duration-300 ease-in-out ${
                  openFeatureId === feature.id ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <div className="px-6 pb-4 pt-1 text-gray-300 border-t border-gray-700/30">
                  {feature.description}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
