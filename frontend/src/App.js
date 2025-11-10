/**
 * ClinicCloud Frontend - Main Application Component
 *
 * Copyright (C) 2025 Rubén García Rodríguez
 *
 * This file is part of ClinicCloud.
 *
 * ClinicCloud is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * ClinicCloud is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import authService from './services/authService';
import Layout from './components/layout/Layout';
import SearchPage from './components/SearchPage';
import ResultsPage from './components/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import FavoritesPage from './pages/FavoritesPage';
import Settings from './components/Settings';
import ResetPasswordPage from './components/ResetPasswordPage';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Componente puente para sincronizar preferencias del usuario con el tema
function PreferencesSyncBridge() {
  const { preferences } = useAuth();
  const { setTheme, setFontSize } = useTheme();

  useEffect(() => {
    if (preferences) {
      console.log('[App] Applying preferences to theme:', preferences);
      if (preferences.theme) {
        setTheme(preferences.theme);
      }
      if (preferences.fontSize) {
        setFontSize(preferences.fontSize);
      }
    }
  }, [preferences, setTheme, setFontSize]);

  return null; // Este componente no renderiza nada
}

function AppContent() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [searchMetadata, setSearchMetadata] = useState({
    total: 0,
    hasMore: false,
    filteredBySimilarity: false
  });

  // Cargar el idioma almacenado en localStorage cuando la app inicia
  useEffect(() => {
    const savedLanguage = localStorage.getItem('i18nextLng');
    if (savedLanguage) {
      i18n.changeLanguage(savedLanguage);
    }
  }, []);

  const handleSearch = async (query) => {
    setIsLoading(true);
    setSearchQuery(query);
    setSelectedDocument(null);

    try {
      // URL de la API usando variable de entorno
      const apiUrl = `${API_BASE_URL}/api/search/`;

      console.log(`Enviando búsqueda a: ${apiUrl} con query: ${query}`);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          limit: 500, // El backend tiene un límite de seguridad de 500
          offset: 0
          // similarity_threshold usa el valor por defecto del backend (0.88)
        }),
      });

      if (!response.ok) {
        throw new Error(`Error en la búsqueda: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`Resultados recibidos: ${data.results.length} resultados totales`);

      setSearchResults(data.results);
      setSearchMetadata({
        total: data.total,
        hasMore: false, // Ya no hay paginación en backend
        filteredBySimilarity: data.filtered_by_similarity
      });

      // Guardar en el historial si el usuario está autenticado
      try {
        const token = authService.getToken();
        if (token) {
          await fetch(`${API_BASE_URL}/api/history`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...authService.getAuthHeaders(),
            },
            body: JSON.stringify({
              query: query,
              results_count: data.total || data.results.length,
            }),
          });
          console.log('Search saved to history');
        }
      } catch (historyError) {
        // No mostrar error al usuario si falla guardar en historial
        console.error('Error saving to history:', historyError);
      }
    } catch (error) {
      console.error('Error:', error);
      setSearchResults([]);
      setSearchMetadata({ total: 0, hasMore: false, filteredBySimilarity: false });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <PreferencesSyncBridge />
      <Router>
        <Layout>
        <Routes>
        <Route path="/" element={
          <SearchPage
            onSearch={handleSearch}
            isLoading={isLoading}
          />
        } />
        <Route path="/results" element={
          <ResultsPage
            query={searchQuery}
            results={searchResults}
            isLoading={isLoading}
            onSearch={handleSearch}
            onSelectDocument={setSelectedDocument}
            selectedDocument={selectedDocument}
            searchMetadata={searchMetadata}
          />
        } />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/favorites" element={<FavoritesPage />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        </Routes>
        </Layout>
      </Router>
    </>
  );
}

function App() {
  return (
    <I18nextProvider i18n={i18n}>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <AppContent />
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </I18nextProvider>
  );
}

export default App;