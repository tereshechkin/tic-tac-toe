import React from 'react';
import { useAuth } from '../contexts/AuthContext';

interface HeroProps {
  onStartGame: () => void;
  onLoginClick: () => void;
}

const Hero: React.FC<HeroProps> = ({ onStartGame, onLoginClick }) => {
  const { isAuthenticated } = useAuth();

  return (
    <section className="pt-24 pb-16 md:pt-32 md:pb-20 bg-gradient-to-b from-primary-dark to-primary relative overflow-hidden">
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-10 left-10 w-64 h-64 bg-accent rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-accent rounded-full blur-3xl"></div>
      </div>
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="text-white">Играй в классические</span>
            <br />
            <span className="text-accent">крестики-нолики против сильного AI</span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Выбери уровень сложности, сражайся с LLM-моделями и анализируй свои партии
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={onStartGame}
              className="btn-primary text-lg px-10 py-4"
            >
              🎮 Начать новую игру
            </button>
            
            {!isAuthenticated && (
              <div className="flex items-center gap-3 text-gray-400">
                <span>Уже есть аккаунт?</span>
                <button
                  onClick={onLoginClick}
                  className="text-accent hover:text-accent-light font-semibold transition-colors duration-200 underline-offset-2 hover:underline"
                >
                  Войдите
                </button>
                <span className="text-sm hidden md:inline">чтобы сохранять историю игр</span>
              </div>
            )}
          </div>

          {isAuthenticated && (
            <p className="mt-4 text-sm text-gray-400">
              ✅ Вы авторизованы. История игр будет сохраняться.
            </p>
          )}
        </div>
      </div>
    </section>
  );
};

export default Hero;
