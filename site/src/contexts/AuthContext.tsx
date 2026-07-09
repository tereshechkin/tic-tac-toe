import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
  theme_preference: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  sendRegistrationCode: (email: string, username: string) => Promise<void>;
  sendLoginCode: (email: string) => Promise<void>;
  verifyRegistration: (email: string, code: string) => Promise<void>;
  verifyLogin: (email: string, code: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const getBaseUrl = () => {
  return import.meta.env.VITE_BACKEND_BASE_URL || '';
};

const apiRequest = async (path: string, options: RequestInit = {}) => {
  const base = getBaseUrl();
  const url = `${base}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  if (!response.ok) {
    let errorMsg = 'Ошибка запроса';
    try {
      const data = await response.json();
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          errorMsg = data.detail.map((d: any) => d.msg).join(', ');
        } else {
          errorMsg = data.detail;
        }
      }
    } catch (e) {
      // ignore
    }
    throw new Error(errorMsg);
  }
  return response.json();
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const setAuthData = (access: string, userData: User) => {
    setAccessToken(access);
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('accessToken', access);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const clearAuth = () => {
    setAccessToken(null);
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
  };

  // Восстановление сессии
  useEffect(() => {
    const storedAccess = localStorage.getItem('accessToken');
    const storedUser = localStorage.getItem('user');
    if (storedAccess && storedUser) {
      const verifyToken = async () => {
        try {
          const data = await apiRequest('/api/v1/auth/verify', {
            headers: { Authorization: `Bearer ${storedAccess}` },
          });
          setAuthData(storedAccess, data);
        } catch (error) {
          clearAuth();
        }
      };
      verifyToken();
    }
  }, []);

  const sendRegistrationCode = async (email: string, username: string) => {
    await apiRequest('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username }),
    });
  };

  const sendLoginCode = async (email: string) => {
    await apiRequest('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  };

  const verifyRegistration = async (email: string, code: string) => {
    const data = await apiRequest('/api/v1/auth/verify-registration', {
      method: 'POST',
      body: JSON.stringify({ email, code }),
    });
    setAuthData(data.access_token, data.user);
  };

  const verifyLogin = async (email: string, code: string) => {
    const data = await apiRequest('/api/v1/auth/verify-login', {
      method: 'POST',
      body: JSON.stringify({ email, code }),
    });
    setAuthData(data.access_token, data.user);
  };

  const logout = async () => {
    try {
      if (accessToken) {
        await apiRequest('/api/v1/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${accessToken}` },
        });
      }
    } catch (error) {
      // ignore
    } finally {
      clearAuth();
    }
  };

  return (
    <AuthContext.Provider value={{
      isAuthenticated,
      user,
      accessToken,
      sendRegistrationCode,
      sendLoginCode,
      verifyRegistration,
      verifyLogin,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};