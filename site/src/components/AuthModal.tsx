import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabType = 'login' | 'register';
type AuthStep = 'input' | 'verify';

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('login');
  const [step, setStep] = useState<AuthStep>('input');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<number | null>(null);
  const { sendRegistrationCode, sendLoginCode, verifyRegistration, verifyLogin } = useAuth();

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      resetState();
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isOpen]);

  useEffect(() => {
    if (timer > 0) {
      timerRef.current = setInterval(() => {
        setTimer((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current!);
            setStep('input');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [timer]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  const resetState = () => {
    setStep('input');
    setError('');
    setCode('');
    setTimer(0);
    setIsLoading(false);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const handleSendCode = async () => {
    setError('');
    if (!email) {
      setError('Введите email');
      return;
    }
    if (activeTab === 'register' && !username) {
      setError('Введите имя пользователя');
      return;
    }
    setIsLoading(true);
    try {
      if (activeTab === 'login') {
        await sendLoginCode(email);
      } else {
        await sendRegistrationCode(email, username);
      }
      setStep('verify');
      setTimer(300);
    } catch (err: any) {
      setError(err.message || 'Ошибка отправки кода');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    setError('');
    if (!code || code.length !== 6) {
      setError('Введите 6-значный код');
      return;
    }
    setIsLoading(true);
    try {
      if (activeTab === 'login') {
        await verifyLogin(email, code);
      } else {
        await verifyRegistration(email, code);
      }
      onClose();
    } catch (err: any) {
      setError(err.message || 'Неверный код');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTabSwitch = (tab: TabType) => {
    setActiveTab(tab);
    resetState();
    setEmail('');
    setUsername('');
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in p-4">
      <div
        ref={modalRef}
        className="bg-primary-light rounded-card shadow-2xl w-full max-w-md border border-gray-700/50 animate-slide-down"
      >
        <div className="flex justify-between items-center p-6 border-b border-gray-700/50">
          <h2 className="text-2xl font-bold text-white">
            {activeTab === 'login' ? 'Вход' : 'Регистрация'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors duration-200"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex border-b border-gray-700/50">
          <button
            className={`flex-1 py-3 text-center font-medium transition-colors duration-200 ${
              activeTab === 'login'
                ? 'text-accent border-b-2 border-accent'
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => handleTabSwitch('login')}
          >
            Вход
          </button>
          <button
            className={`flex-1 py-3 text-center font-medium transition-colors duration-200 ${
              activeTab === 'register'
                ? 'text-accent border-b-2 border-accent'
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => handleTabSwitch('register')}
          >
            Регистрация
          </button>
        </div>

        <form onSubmit={(e) => e.preventDefault()} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-button text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={step === 'verify'}
              className="w-full px-4 py-2 bg-primary border border-gray-600 rounded-button text-white focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              placeholder="email@example.com"
              required
            />
          </div>

          {activeTab === 'register' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Имя пользователя
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={step === 'verify'}
                className="w-full px-4 py-2 bg-primary border border-gray-600 rounded-button text-white focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="Игрок"
                required
              />
            </div>
          )}

          {step === 'verify' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Код подтверждения
              </label>
              <input
                type="text"
                value={code}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, '').slice(0, 6);
                  setCode(val);
                }}
                className="w-full px-4 py-2 bg-primary border border-gray-600 rounded-button text-white focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200 text-center text-2xl tracking-widest font-mono"
                placeholder="000000"
                maxLength={6}
                autoFocus
              />
              <div className="flex justify-between items-center mt-2">
                <span className="text-sm text-gray-400">
                  Код отправлен на {email}
                </span>
                <span className="text-sm font-mono text-accent">
                  {formatTime(timer)}
                </span>
              </div>
            </div>
          )}

          {step === 'input' ? (
            <button
              type="button"
              onClick={handleSendCode}
              disabled={isLoading}
              className="w-full btn-primary text-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Отправка...' : 'Отправить код'}
            </button>
          ) : (
            <button
              type="button"
              onClick={handleVerifyCode}
              disabled={isLoading || code.length !== 6}
              className="w-full btn-primary text-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Проверка...' : 'Ввести код'}
            </button>
          )}

          <p className="text-center text-sm text-gray-400">
            {activeTab === 'login' ? (
              <>
                Нет аккаунта?{' '}
                <button
                  type="button"
                  onClick={() => handleTabSwitch('register')}
                  className="text-accent hover:text-accent-light transition-colors duration-200"
                >
                  Зарегистрироваться
                </button>
              </>
            ) : (
              <>
                Уже есть аккаунт?{' '}
                <button
                  type="button"
                  onClick={() => handleTabSwitch('login')}
                  className="text-accent hover:text-accent-light transition-colors duration-200"
                >
                  Войти
                </button>
              </>
            )}
          </p>
        </form>
      </div>
    </div>
  );
};

export default AuthModal;