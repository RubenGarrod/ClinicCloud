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

  // Inicializar estado de autenticación al cargar la app
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      
      // Verificar si hay token y datos guardados
      const token = authService.getToken();
      const userData = authService.getUserData();

      if (token && userData) {
        // Verificar que el token siga siendo válido
        try {
          const verifiedUser = await authService.verifyToken();
          const normalizedUser = normalizeUserData(verifiedUser);
          setUser(normalizedUser);
          setIsAuthenticated(true);
        } catch (error) {
          // Token inválido, limpiar datos
          console.log('Token expirado o inválido, limpiando sesión');
          authService.clearLocalStorage();
          setUser(null);
          setIsAuthenticated(false);
        }
      }
    } catch (error) {
      console.error('Error inicializando autenticación:', error);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await authService.login(email, password);

      const normalizedUser = normalizeUserData(response.user);
      setUser(normalizedUser);
      setIsAuthenticated(true);

      return response;
    } catch (error) {
      console.error('Error en login:', error);
      throw error;
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await authService.register(name, email, password);

      const normalizedUser = normalizeUserData(response.user);
      setUser(normalizedUser);
      setIsAuthenticated(true);

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

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    updateUser,
    updateProfile,
    initializeAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};