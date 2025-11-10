import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [preferences, setPreferences] = useState(null);

  // Función para normalizar datos del usuario del backend
  const normalizeUserData = (userData) => {
    if (!userData) return null;

    // Si el backend devuelve avatar_icon y avatar_color separados, convertir a objeto avatar
    if (userData.avatar_icon || userData.avatar_color) {
      userData.avatar = {
        icon: userData.avatar_icon || 'cat',
        color: userData.avatar_color || 'blue'
      };
    }

    // Si no tiene avatar, usar default
    if (!userData.avatar) {
      userData.avatar = { icon: 'cat', color: 'blue' };
    }

    return userData;
  };

  // Función para cargar preferencias del usuario
  const loadUserPreferences = async () => {
    console.log('[AuthContext] loadUserPreferences - Starting...');
    try {
      const token = authService.getToken();
      console.log('[AuthContext] loadUserPreferences - Token exists:', !!token);

      if (!token) {
        console.log('[AuthContext] loadUserPreferences - No token, aborting');
        return;
      }

      const url = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/preferences`;
      console.log('[AuthContext] loadUserPreferences - Fetching from:', url);

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      console.log('[AuthContext] loadUserPreferences - Response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('[AuthContext] loadUserPreferences - Data received:', data);
        setPreferences(data);
        // Guardar en localStorage para persistencia
        localStorage.setItem('user_preferences', JSON.stringify(data));
        console.log('[AuthContext] loadUserPreferences - Preferences set in state and localStorage');
      } else {
        const errorText = await response.text();
        console.error('[AuthContext] loadUserPreferences - Failed:', response.status, errorText);
      }
    } catch (error) {
      console.error('[AuthContext] loadUserPreferences - Error:', error);
    }
  };

  // Monitorear cambios en preferences
  useEffect(() => {
    console.log('[AuthContext] preferences state changed:', preferences);
  }, [preferences]);

  // Inicializar estado de autenticación al cargar la app
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      console.log('[AuthContext] initializeAuth - Starting...');
      setIsLoading(true);

      // Verificar si hay token y datos guardados
      const token = authService.getToken();
      const userData = authService.getUserData();
      console.log('[AuthContext] initializeAuth - Token exists:', !!token, 'UserData exists:', !!userData);

      if (token && userData) {
        // Verificar que el token siga siendo válido
        try {
          console.log('[AuthContext] initializeAuth - Verifying token...');
          const verifiedUser = await authService.verifyToken();
          const normalizedUser = normalizeUserData(verifiedUser);
          setUser(normalizedUser);
          setIsAuthenticated(true);
          console.log('[AuthContext] initializeAuth - User verified, calling loadUserPreferences...');
          // Cargar preferencias del usuario
          await loadUserPreferences();
          console.log('[AuthContext] initializeAuth - Completed successfully');
        } catch (error) {
          // Token inválido, limpiar datos
          console.log('[AuthContext] initializeAuth - Token expirado o inválido, limpiando sesión');
          authService.clearLocalStorage();
          localStorage.removeItem('user_preferences');
          setUser(null);
          setIsAuthenticated(false);
          setPreferences(null);
        }
      } else {
        console.log('[AuthContext] initializeAuth - No token or userData, skipping');
      }
    } catch (error) {
      console.error('[AuthContext] initializeAuth - Error:', error);
      setUser(null);
      setIsAuthenticated(false);
      setPreferences(null);
    } finally {
      setIsLoading(false);
      console.log('[AuthContext] initializeAuth - Loading finished');
    }
  };

  const login = async (email, password) => {
    try {
      console.log('[AuthContext] login - Starting...');
      const response = await authService.login(email, password);

      const normalizedUser = normalizeUserData(response.user);
      setUser(normalizedUser);
      setIsAuthenticated(true);
      console.log('[AuthContext] login - User set, calling loadUserPreferences...');
      // Cargar preferencias del usuario
      await loadUserPreferences();
      console.log('[AuthContext] login - Completed');

      return response;
    } catch (error) {
      console.error('[AuthContext] login - Error:', error);
      throw error;
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await authService.register(name, email, password);

      const normalizedUser = normalizeUserData(response.user);
      setUser(normalizedUser);
      setIsAuthenticated(true);
      // Cargar preferencias del usuario (o crear defaults si es nuevo)
      await loadUserPreferences();

      return response;
    } catch (error) {
      console.error('Error en registro:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Error en logout:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setPreferences(null);
      localStorage.removeItem('user_preferences');
    }
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user_data', JSON.stringify(userData));
  };

  const updateProfile = (updates) => {
    const updatedUser = { ...user, ...updates };
    const normalizedUser = normalizeUserData(updatedUser);
    setUser(normalizedUser);
    localStorage.setItem('user_data', JSON.stringify(normalizedUser));
  };

  const updatePreferences = (newPreferences) => {
    setPreferences(newPreferences);
    localStorage.setItem('user_preferences', JSON.stringify(newPreferences));
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    preferences,
    login,
    register,
    logout,
    updateUser,
    updateProfile,
    updatePreferences,
    loadUserPreferences,
    initializeAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};