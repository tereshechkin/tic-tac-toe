import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface HeaderProps {
  onLoginClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLoginClick }) => {
  const { isAuthenticated, user, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  return (
    <header className="bg-primary-light/80 backdrop-blur-sm border-b border-gray-700/50 fixed w-full top-0 z-50">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="text-2xl font-bold text-accent">
            <span className="text-white">✕</span>О<span className="text-white">✕</span>
          </div>
          <span className="text-white font-semibold text-lg hidden sm:block">Крестики-Нолики AI</span>
        </div>

        <div className="flex items-center gap-3">
          {!isAuthenticated ? (
            <button
              onClick={onLoginClick}
              className="btn-secondary text-sm py-2 px-4"
            >
              Войти
            </button>
          ) : (
            <div className="relative">
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-2 bg-card hover:bg-card-hover rounded-full px-3 py-2 transition-colors duration-200"
              >
                <span className="text-lg">{user?.username?.charAt(0) || '👤'}</span>
                <span className="text-sm font-medium">{user?.username}</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-card rounded-card shadow-lg py-1 border border-gray-700/50 animate-fade-in">
                  <button
                    onClick={() => {
                      logout();
                      setIsDropdownOpen(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-primary-light hover:text-white transition-colors duration-200"
                  >
                    Выйти
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;