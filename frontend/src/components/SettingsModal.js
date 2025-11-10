import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Settings as SettingsIcon, Globe, List, ArrowUpDown, Type, Eye, Clock, BarChart3, Sun, Moon, Monitor, RotateCcw } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import Modal from './ui/Modal';
import authService from '../services/authService';
import Button from './ui/Button';

const SettingsModal = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const { theme, setTheme, fontSize, setFontSize } = useTheme();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true); // Estado de carga

  const [preferences, setPreferences] = useState({
    preferredLanguage: 'es',
    resultsPerPage: 25,
    defaultSort: 'relevance',
    saveSearchHistory: true,
    historyRetention: '6months',
    anonymousStats: true
  });

  // Cargar preferencias del usuario cada vez que se abre el modal
  useEffect(() => {
    if (isOpen) {
      setIsLoading(true); // Mostrar indicador de carga
      loadPreferences();
    }
  }, [isOpen]);

  // Cargar preferencias desde el backend
  const loadPreferences = async () => {
    try {
      const token = authService.getToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/preferences`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Preferencias cargadas desde API:', data); // Debug

        // El backend devuelve snake_case, necesitamos mapear a camelCase
        // Intentar ambos formatos para compatibilidad
        setPreferences({
          preferredLanguage: data.preferredLanguage || data.preferred_language || 'es',
          resultsPerPage: data.resultsPerPage || data.results_per_page || 25,
          defaultSort: data.defaultSort || data.default_sort || 'relevance',
          saveSearchHistory: data.saveSearchHistory !== undefined ? data.saveSearchHistory :
                            (data.save_search_history !== undefined ? data.save_search_history : true),
          historyRetention: data.historyRetention || data.history_retention || '6months',
          anonymousStats: data.anonymousStats !== undefined ? data.anonymousStats :
                         (data.anonymous_stats !== undefined ? data.anonymous_stats : true)
        });

        // Aplicar tema y fontSize desde preferencias guardadas
        if (data.theme || data.theme) {
          setTheme(data.theme);
        }
        if (data.fontSize || data.font_size) {
          setFontSize(data.fontSize || data.font_size);
        }
      } else if (response.status === 401) {
        // Token expirado - cerrar modal silenciosamente
        console.log('Token expirado al cargar preferencias, cerrando modal');
        onClose();
      }
    } catch (error) {
      // Si no hay token, ignorar el error silenciosamente
      if (!authService.getToken()) {
        return;
      }
      console.error('Error loading preferences:', error);
    } finally {
      setIsLoading(false); // Ocultar indicador de carga
    }
  };

  // Guardar una preferencia individual en el backend
  const savePreference = async (field, value) => {
    try {
      const token = authService.getToken();

      // Si no hay token, el usuario no está autenticado - silenciosamente ignorar
      if (!token) {
        return;
      }

      const payload = { [field]: value };

      console.log('Guardando preferencia:', field, '=', value); // Debug

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/preferences`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        // Si es 401, el token expiró - cerrar modal silenciosamente
        if (response.status === 401) {
          console.log('Token expirado, cerrando configuración');
          onClose();
          return;
        }

        const data = await response.json();
        console.error('Error del servidor:', data); // Debug
        throw new Error(data.detail || 'Error al guardar preferencia');
      }

      const savedData = await response.json();
      console.log('Preferencia guardada exitosamente:', savedData); // Debug
    } catch (error) {
      // Si el error es de red o el fetch falló, ignorar silenciosamente si no hay token
      if (!authService.getToken()) {
        return;
      }
      console.error('Error saving preference:', error);
      setError(error.message || t('settings.saveError', 'Error al guardar preferencias'));
      setTimeout(() => setError(''), 3000);
    }
  };

  // Manejar cambios en preferencias generales (resultsPerPage, defaultSort, etc.)
  const handleChange = (field, value) => {
    console.log('Cambiando preferencia:', field, '→', value); // Debug

    // Actualizar estado local inmediatamente
    setPreferences(prev => ({
      ...prev,
      [field]: value
    }));
    setError('');

    // Guardar automáticamente en el backend
    savePreference(field, value);

    // Emitir evento personalizado para que otros componentes se actualicen
    // Especialmente importante para resultsPerPage y defaultSort
    if (field === 'resultsPerPage' || field === 'defaultSort') {
      window.dispatchEvent(new CustomEvent('preferencesChanged', {
        detail: { field, value }
      }));
    }
  };

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    savePreference('theme', newTheme);
  };

  const handleFontSizeChange = (newFontSize) => {
    setFontSize(newFontSize);
    savePreference('fontSize', newFontSize);
  };

  const handleLanguageChange = (newLanguage) => {
    // Cambiar idioma inmediatamente
    i18n.changeLanguage(newLanguage);
    // Actualizar estado y guardar
    setPreferences(prev => ({
      ...prev,
      preferredLanguage: newLanguage
    }));
    savePreference('preferredLanguage', newLanguage);
  };

  // Restaurar configuración por defecto
  const handleResetToDefaults = async () => {
    if (!window.confirm(t('settings.confirmReset', '¿Estás seguro de que quieres restaurar la configuración por defecto?'))) {
      return;
    }

    try {
      const token = authService.getToken();

      // Valores por defecto
      const defaults = {
        preferredLanguage: 'es',
        resultsPerPage: 25,
        defaultSort: 'relevance',
        fontSize: 'normal',
        theme: 'system',
        saveSearchHistory: true,
        historyRetention: '6months',
        anonymousStats: true
      };

      // Guardar todos los valores por defecto en el backend
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/preferences`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(defaults),
      });

      if (!response.ok) {
        throw new Error('Error al restaurar configuración');
      }

      // Actualizar estado local
      setPreferences(defaults);
      setTheme(defaults.theme);
      setFontSize(defaults.fontSize);
      i18n.changeLanguage(defaults.preferredLanguage);

      // Emitir eventos para que otros componentes se actualicen
      window.dispatchEvent(new CustomEvent('preferencesChanged', {
        detail: { field: 'resultsPerPage', value: defaults.resultsPerPage }
      }));
      window.dispatchEvent(new CustomEvent('preferencesChanged', {
        detail: { field: 'defaultSort', value: defaults.defaultSort }
      }));

      // Mostrar mensaje de éxito (opcional)
      console.log('Configuración restaurada a valores por defecto');

    } catch (error) {
      console.error('Error al restaurar configuración:', error);
      setError(t('settings.resetError', 'Error al restaurar configuración'));
      setTimeout(() => setError(''), 3000);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="lg"
      showCloseButton={true}
    >
      <div className="bg-white dark:bg-gray-800">
        {/* Header */}
        <div className="px-6 py-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <SettingsIcon className="w-8 h-8 text-primary-600 dark:text-primary-400" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {t('settings.title', 'Configuración')}
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {t('settings.subtitle', 'Personaliza tu experiencia de búsqueda')}
                </p>
              </div>
            </div>

            {/* Botón de restaurar por defecto */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleResetToDefaults}
              className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400"
            >
              <RotateCcw className="w-4 h-4" />
              <span className="hidden sm:inline">{t('settings.resetToDefaults', 'Restaurar')}</span>
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-4 max-h-[60vh] overflow-y-auto">
          {/* Mensajes de error */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Indicador de carga mientras se cargan las preferencias */}
          {isLoading && (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <span className="ml-3 text-gray-600 dark:text-gray-400">
                {t('settings.loading', 'Cargando preferencias...')}
              </span>
            </div>
          )}

          {/* Solo mostrar preferencias cuando termine de cargar */}
          {!isLoading && (
          <div className="space-y-6">
            {/* Preferencias de búsqueda */}
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 p-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Globe className="w-5 h-5 mr-2 text-primary-600 dark:text-primary-400" />
                {t('settings.searchPreferences', 'Preferencias de búsqueda')}
              </h2>

              <div className="space-y-4">
                {/* Idioma */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('settings.language', 'Idioma')}
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {/* Español */}
                    <button
                      type="button"
                      onClick={() => handleLanguageChange('es')}
                      className={`flex items-center justify-center p-3 border-2 rounded-lg transition-all ${
                        i18n.language === 'es'
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      <span className={`text-sm font-medium ${
                        i18n.language === 'es'
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {t('settings.spanish', 'Español')}
                      </span>
                    </button>

                    {/* English */}
                    <button
                      type="button"
                      onClick={() => handleLanguageChange('en')}
                      className={`flex items-center justify-center p-3 border-2 rounded-lg transition-all ${
                        i18n.language === 'en'
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      <span className={`text-sm font-medium ${
                        i18n.language === 'en'
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {t('settings.english', 'English')}
                      </span>
                    </button>
                  </div>
                </div>

                {/* Resultados por página */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <List className="w-4 h-4 inline mr-1" />
                    {t('settings.resultsPerPage', 'Número de resultados por página')}
                  </label>
                  <select
                    value={preferences.resultsPerPage}
                    onChange={(e) => handleChange('resultsPerPage', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                  </select>
                </div>

                {/* Orden por defecto */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <ArrowUpDown className="w-4 h-4 inline mr-1" />
                    {t('settings.defaultSort', 'Orden por defecto')}
                  </label>
                  <select
                    value={preferences.defaultSort}
                    onChange={(e) => handleChange('defaultSort', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="relevance">{t('settings.relevance', 'Relevancia')}</option>
                    <option value="date">{t('settings.date', 'Fecha')}</option>
                    <option value="author">{t('settings.author', 'Autor')}</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Preferencias de visualización */}
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 p-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Eye className="w-5 h-5 mr-2 text-primary-600 dark:text-primary-400" />
                {t('settings.displayPreferences', 'Preferencias de visualización')}
              </h2>

              <div className="space-y-4">
                {/* Tamaño de fuente */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Type className="w-4 h-4 inline mr-1" />
                    {t('settings.fontSize', 'Tamaño de fuente')}
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {/* Pequeño */}
                    <button
                      type="button"
                      onClick={() => handleFontSizeChange('small')}
                      className={`flex flex-col items-center justify-center p-3 border-2 rounded-lg transition-all ${
                        fontSize === 'small'
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      <span className={`text-xs mb-1 ${
                        fontSize === 'small'
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-gray-600 dark:text-gray-400'
                      }`}>
                        A
                      </span>
                      <span className={`text-sm font-medium ${
                        fontSize === 'small'
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {t('settings.small', 'Pequeño')}
                      </span>
                    </button>

                    {/* Normal */}
                    <button
                      type="button"
                      onClick={() => handleFontSizeChange('normal')}
                      className={`flex flex-col items-center justify-center p-3 border-2 rounded-lg transition-all ${
                        fontSize === 'normal'
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      <span className={`text-sm mb-1 ${
                        fontSize === 'normal'
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-gray-600 dark:text-gray-400'
                      }`}>
                        A
                      </span>
                      <span className={`text-sm font-medium ${
                        fontSize === 'normal'
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {t('settings.normal', 'Normal')}
                      </span>
                    </button>

                    {/* Grande */}
                    <button
                      type="button"
                      onClick={() => handleFontSizeChange('large')}
                      className={`flex flex-col items-center justify-center p-3 border-2 rounded-lg transition-all ${
                        fontSize === 'large'
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      <span className={`text-base mb-1 ${
                        fontSize === 'large'
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-gray-600 dark:text-gray-400'
                      }`}>
                        A
                      </span>
                      <span className={`text-sm font-medium ${
                        fontSize === 'large'
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {t('settings.large', 'Grande')}
                      </span>
                    </button>
                  </div>
                </div>

                {/* Tema */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('settings.theme', 'Tema')}
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {/* Claro */}
                    <button
                      type="button"
                      onClick={() => handleThemeChange('light')}
                      className={`flex flex-col items-center justify-center p-3 border-2 rounded-lg transition-all ${
                        theme === 'light'
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      <Sun className={`w-6 h-6 mb-1 ${
                        theme === 'light'
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-gray-600 dark:text-gray-400'
                      }`} />
                      <span className={`text-sm font-medium ${
                        theme === 'light'
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {t('settings.light', 'Claro')}
                      </span>
                    </button>

                    {/* Oscuro */}
                    <button
                      type="button"
                      onClick={() => handleThemeChange('dark')}
                      className={`flex flex-col items-center justify-center p-3 border-2 rounded-lg transition-all ${
                        theme === 'dark'
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      <Moon className={`w-6 h-6 mb-1 ${
                        theme === 'dark'
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-gray-600 dark:text-gray-400'
                      }`} />
                      <span className={`text-sm font-medium ${
                        theme === 'dark'
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {t('settings.dark', 'Oscuro')}
                      </span>
                    </button>

                    {/* Sistema */}
                    <button
                      type="button"
                      onClick={() => handleThemeChange('system')}
                      className={`flex flex-col items-center justify-center p-3 border-2 rounded-lg transition-all ${
                        theme === 'system'
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      <Monitor className={`w-6 h-6 mb-1 ${
                        theme === 'system'
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-gray-600 dark:text-gray-400'
                      }`} />
                      <span className={`text-sm font-medium ${
                        theme === 'system'
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {t('settings.system', 'Sistema')}
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Privacidad y datos */}
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 p-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2 text-primary-600 dark:text-primary-400" />
                {t('settings.privacyData', 'Privacidad de datos')}
              </h2>

              <div className="space-y-4">
                {/* Guardar historial */}
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      type="checkbox"
                      checked={preferences.saveSearchHistory}
                      onChange={(e) => handleChange('saveSearchHistory', e.target.checked)}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                  </div>
                  <div className="ml-3">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {t('settings.saveHistory', 'Guardar historial de búsquedas')}
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {t('settings.saveHistoryHelp', 'Guarda tus búsquedas para acceder a ellas más tarde')}
                    </p>
                  </div>
                </div>

                {/* Tiempo de retención */}
                {preferences.saveSearchHistory && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Clock className="w-4 h-4 inline mr-1" />
                      {t('settings.historyRetention', 'Tiempo de retención del historial')}
                    </label>
                    <select
                      value={preferences.historyRetention}
                      onChange={(e) => handleChange('historyRetention', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="1month">{t('settings.oneMonth', '1 mes')}</option>
                      <option value="3months">{t('settings.threeMonths', '3 meses')}</option>
                      <option value="6months">{t('settings.sixMonths', '6 meses')}</option>
                      <option value="forever">{t('settings.forever', 'Siempre')}</option>
                    </select>
                  </div>
                )}

                {/* Datos anónimos */}
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      type="checkbox"
                      checked={preferences.anonymousStats}
                      onChange={(e) => handleChange('anonymousStats', e.target.checked)}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                  </div>
                  <div className="ml-3">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {t('settings.anonymousStats', 'Compartir datos anónimos para estadísticas')}
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {t('settings.anonymousStatsHelp', 'Ayuda a mejorar el servicio compartiendo datos de uso anónimos')}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default SettingsModal;
