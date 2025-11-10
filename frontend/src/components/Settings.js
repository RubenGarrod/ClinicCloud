import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Settings as SettingsIcon, Globe, List, ArrowUpDown, Type, Eye, Clock, BarChart3, Save, Trash2, AlertTriangle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import Button from './ui/Button';
import authService from '../services/authService';

const Settings = () => {
  const { t } = useTranslation();
  const { user, logout, preferences: contextPreferences, updatePreferences } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Valores por defecto
  const defaultPreferences = {
    preferredLanguage: 'es',
    resultsPerPage: 25,
    defaultSort: 'relevance',
    fontSize: 'normal',
    theme: 'system',
    saveSearchHistory: true,
    historyRetention: '6months',
    anonymousStats: true
  };

  const [preferences, setPreferences] = useState(defaultPreferences);

  // Cargar preferencias del contexto cuando estén disponibles
  useEffect(() => {
    if (contextPreferences) {
      setPreferences(prev => ({ ...prev, ...contextPreferences }));
    }
  }, [contextPreferences]);

  const handleChange = (field, value) => {
    setPreferences(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
    setError('');
    setSuccess('');
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = authService.getToken();
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/preferences`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al guardar preferencias');
      }

      // Actualizar preferencias en el contexto
      updatePreferences(preferences);

      setSuccess(t('settings.saveSuccess', 'Preferencias guardadas correctamente'));
      setHasChanges(false);
    } catch (error) {
      console.error('Error saving preferences:', error);
      setError(error.message || t('settings.saveError', 'Error al guardar preferencias'));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setLoading(true);
    setError('');

    try {
      const token = authService.getToken();
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/delete-account`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al eliminar cuenta');
      }

      // Cerrar sesión y redirigir
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Error deleting account:', error);
      setError(error.message || t('settings.deleteAccountError', 'Error al eliminar la cuenta'));
      setShowDeleteConfirm(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
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
      </div>

      {/* Mensajes de error/éxito */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-400 text-sm">
          {success}
        </div>
      )}

      <div className="space-y-6">
        {/* Preferencias de búsqueda */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-primary-600 dark:text-primary-400" />
            {t('settings.searchPreferences', 'Preferencias de búsqueda')}
          </h2>

          <div className="space-y-4">
            {/* Idioma preferido */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('settings.preferredLanguage', 'Idioma preferido de documentos')}
              </label>
              <select
                value={preferences.preferredLanguage}
                onChange={(e) => handleChange('preferredLanguage', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="es">{t('settings.spanish', 'Español')}</option>
                <option value="en">{t('settings.english', 'Inglés')}</option>
                <option value="both">{t('settings.both', 'Ambos')}</option>
              </select>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {t('settings.languageHelp', 'Los resultados priorizarán documentos en este idioma')}
              </p>
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
                <option value={20}>20</option>
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
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
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
              <select
                value={preferences.fontSize}
                onChange={(e) => handleChange('fontSize', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="small">{t('settings.small', 'Pequeño')}</option>
                <option value="normal">{t('settings.normal', 'Normal')}</option>
                <option value="large">{t('settings.large', 'Grande')}</option>
              </select>
            </div>
          </div>
        </div>

        {/* Privacidad y datos */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
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

        {/* Danger Zone - Eliminar cuenta */}
        <div className="bg-red-50 dark:bg-red-900/10 rounded-lg border-2 border-red-200 dark:border-red-800 p-6">
          <h2 className="text-lg font-semibold text-red-900 dark:text-red-400 mb-2 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            {t('settings.dangerZone', 'Zona de peligro')}
          </h2>
          <p className="text-sm text-red-700 dark:text-red-400 mb-4">
            {t('settings.dangerZoneDesc', 'Las acciones en esta sección son permanentes e irreversibles.')}
          </p>

          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-sm font-medium text-red-900 dark:text-red-300">
                {t('settings.deleteAccount', 'Eliminar mi cuenta')}
              </h3>
              <p className="text-xs text-red-700 dark:text-red-400 mt-1">
                {t('settings.deleteAccountDesc', 'Elimina permanentemente tu cuenta y todos tus datos asociados. Esta acción no se puede deshacer.')}
              </p>
            </div>
            <Button
              onClick={() => setShowDeleteConfirm(true)}
              variant="ghost"
              className="ml-4 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/20 border-red-300 dark:border-red-700"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              {t('settings.deleteAccountButton', 'Eliminar cuenta')}
            </Button>
          </div>
        </div>

        {/* Botón guardar */}
        <div className="flex justify-end">
          <Button
            onClick={handleSave}
            disabled={loading || !hasChanges}
            variant="primary"
          >
            <Save className="w-4 h-4 mr-2" />
            {loading ? t('settings.saving', 'Guardando...') : t('settings.save', 'Guardar preferencias')}
          </Button>
        </div>
      </div>

      {/* Modal de confirmación de eliminación */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-[9999] overflow-y-auto">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
            onClick={() => !loading && setShowDeleteConfirm(false)}
          />

          {/* Dialog */}
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
                </div>
                <h3 className="ml-3 text-lg font-semibold text-gray-900 dark:text-white">
                  {t('settings.deleteAccountConfirmTitle', '¿Eliminar tu cuenta?')}
                </h3>
              </div>

              <div className="mb-6">
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                  {t('settings.deleteAccountConfirmText', 'Esta acción eliminará permanentemente:')}
                </p>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1 list-disc list-inside">
                  <li>{t('settings.deleteAccountItem1', 'Tu perfil y datos personales')}</li>
                  <li>{t('settings.deleteAccountItem2', 'Todo tu historial de búsquedas')}</li>
                  <li>{t('settings.deleteAccountItem3', 'Tus documentos favoritos')}</li>
                  <li>{t('settings.deleteAccountItem4', 'Todas tus preferencias')}</li>
                </ul>
                <p className="text-sm text-red-600 dark:text-red-400 font-medium mt-3">
                  {t('settings.deleteAccountWarning', 'Esta acción no se puede deshacer.')}
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={loading}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50"
                >
                  {t('common.cancel', 'Cancelar')}
                </button>
                <button
                  onClick={handleDeleteAccount}
                  disabled={loading}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800 rounded-lg transition-colors disabled:opacity-50 flex items-center"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  {loading ? t('settings.deleting', 'Eliminando...') : t('settings.deleteAccountConfirm', 'Sí, eliminar mi cuenta')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
