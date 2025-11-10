import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const { preferences } = useAuth();

  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'system';
  });

  const [fontSize, setFontSize] = useState(() => {
    const savedSize = localStorage.getItem('fontSize');
    return savedSize || 'normal';
  });

  // Aplicar preferencias del usuario cuando se cargan desde AuthContext
  useEffect(() => {
    if (preferences) {
      console.log('[ThemeContext] Applying preferences from AuthContext:', preferences);
      if (preferences.theme) {
        setTheme(preferences.theme);
      }
      if (preferences.fontSize) {
        setFontSize(preferences.fontSize);
      }
    }
  }, [preferences]);

  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const savedState = localStorage.getItem('sidebarCollapsed');
    return savedState ? JSON.parse(savedState) : false;
  });

  // Aplicar tema basado en preferencias del usuario o sistema
  useEffect(() => {
    localStorage.setItem('theme', theme);

    let effectiveTheme = theme;

    // Si es 'system', detectar preferencia del sistema
    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      effectiveTheme = prefersDark ? 'dark' : 'light';
    }

    if (effectiveTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Aplicar tamaño de fuente
  useEffect(() => {
    localStorage.setItem('fontSize', fontSize);

    // Remover todas las clases de tamaño de fuente
    document.documentElement.classList.remove('font-size-small', 'font-size-normal', 'font-size-large');

    // Agregar la clase correspondiente
    document.documentElement.classList.add(`font-size-${fontSize}`);
  }, [fontSize]);

  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', JSON.stringify(sidebarCollapsed));
  }, [sidebarCollapsed]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => !prev);
  };

  const value = {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches),
    fontSize,
    setFontSize,
    sidebarCollapsed,
    setSidebarCollapsed,
    toggleSidebar,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};