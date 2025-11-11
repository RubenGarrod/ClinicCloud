import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import authService from '../services/authService';
import { Clock, Search, Trash2, RefreshCw, Calendar, Filter, X } from 'lucide-react';
import Button from '../components/ui/Button';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const HistoryPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }
    fetchHistory();
  }, [user, navigate]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = authService.getToken();
      if (!token) {
        navigate('/');
        return;
      }

      const response = await fetch(`${API_URL}/api/history`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Error al cargar el historial');
      }

      const data = await response.json();
      setHistory(data.items || []);
    } catch (err) {
      console.error('Error fetching history:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async (id) => {
    if (!window.confirm(t('history.confirmDelete', '¿Eliminar esta búsqueda del historial?'))) {
      return;
    }

    try {
      setDeletingId(id);
      const token = authService.getToken();

      const response = await fetch(`${API_URL}/api/history/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Error al eliminar');
      }

      // Actualizar el estado local
      setHistory(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      console.error('Error deleting history item:', err);
      alert(t('history.deleteError', 'Error al eliminar la búsqueda'));
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm(t('history.confirmClearAll', '¿Eliminar todo el historial? Esta acción no se puede deshacer.'))) {
      return;
    }

    try {
      setLoading(true);
      const token = authService.getToken();

      const response = await fetch(`${API_URL}/api/history`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Error al limpiar el historial');
      }

      setHistory([]);
    } catch (err) {
      console.error('Error clearing history:', err);
      alert(t('history.clearError', 'Error al limpiar el historial'));
    } finally {
      setLoading(false);
    }
  };

  const handleRepeatSearch = (query) => {
    // Navegar a la página principal con el query como parámetro
    navigate(`/?q=${encodeURIComponent(query)}`);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) {
      return t('history.justNow', 'Justo ahora');
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return t('history.minutesAgo', { count: minutes, defaultValue: `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}` });
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return t('history.hoursAgo', { count: hours, defaultValue: `Hace ${hours} hora${hours > 1 ? 's' : ''}` });
    } else if (diffInSeconds < 604800) {
      const days = Math.floor(diffInSeconds / 86400);
      return t('history.daysAgo', { count: days, defaultValue: `Hace ${days} día${days > 1 ? 's' : ''}` });
    } else {
      return date.toLocaleDateString();
    }
  };

  if (loading && history.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">{t('history.loading', 'Cargando historial...')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Clock className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {t('history.title', 'Historial de búsquedas')}
            </h1>
          </div>

          {history.length > 0 && (
            <Button
              variant="outline"
              onClick={handleClearAll}
              className="text-red-600 hover:text-red-700 hover:border-red-600"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              {t('history.clearAll', 'Limpiar todo')}
            </Button>
          )}
        </div>

        <p className="text-gray-600 dark:text-gray-400">
          {t('history.subtitle', 'Aquí puedes ver todas tus búsquedas anteriores')}
        </p>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <Button onClick={fetchHistory} variant="outline" className="mt-2">
            {t('history.retry', 'Reintentar')}
          </Button>
        </div>
      )}

      {/* Empty State */}
      {!loading && history.length === 0 && !error && (
        <div className="text-center py-16">
          <Search className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
            {t('history.empty', 'No hay búsquedas en el historial')}
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            {t('history.emptyDescription', 'Tus búsquedas aparecerán aquí automáticamente')}
          </p>
          <Button onClick={() => navigate('/')} variant="primary">
            {t('history.startSearching', 'Comenzar a buscar')}
          </Button>
        </div>
      )}

      {/* History List */}
      {history.length > 0 && (
        <div className="space-y-4">
          {history.map((item) => (
            <div
              key={item.id}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Query */}
                  <div className="flex items-center space-x-2 mb-2">
                    <Search className="w-5 h-5 text-primary-600 dark:text-primary-400 flex-shrink-0" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                      {item.query}
                    </h3>
                  </div>

                  {/* Metadata */}
                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      {formatDate(item.created_at)}
                    </span>

                    {item.results_count !== undefined && item.results_count !== null && (
                      <span>
                        {t('history.results', { count: item.results_count, defaultValue: `${item.results_count} resultados` })}
                      </span>
                    )}

                    {item.categories && item.categories.length > 0 && (
                      <span className="flex items-center">
                        <Filter className="w-4 h-4 mr-1" />
                        {item.categories.join(', ')}
                      </span>
                    )}

                    {(item.date_from || item.date_to) && (
                      <span className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {item.date_from && item.date_to
                          ? `${item.date_from} - ${item.date_to}`
                          : item.date_from || item.date_to}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleRepeatSearch(item.query)}
                    className="p-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                    title={t('history.repeatSearch', 'Repetir búsqueda')}
                  >
                    <RefreshCw className="w-5 h-5" />
                  </button>

                  <button
                    onClick={() => handleDeleteItem(item.id)}
                    disabled={deletingId === item.id}
                    className="p-2 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50"
                    title={t('history.delete', 'Eliminar')}
                  >
                    {deletingId === item.id ? (
                      <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <Trash2 className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HistoryPage;
