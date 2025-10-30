import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  History, 
  Search, 
  Calendar, 
  Clock, 
  FileText, 
  Trash2,
  Filter,
  Download,
  Eye
} from 'lucide-react';
import Button from './ui/Button';

const SearchHistory = () => {
  const { t } = useTranslation();
  const [searchHistory, setSearchHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  // Mock data - en producción esto vendría de la API
  useEffect(() => {
    const mockHistory = [
      {
        id: 1,
        query: 'diabetes tipo 2 tratamiento',
        date: new Date(2024, 0, 15),
        resultsCount: 127,
        categoryKey: 'endocrinology'
      },
      {
        id: 2,
        query: 'hipertensión arterial diagnóstico',
        date: new Date(2024, 0, 14),
        resultsCount: 89,
        categoryKey: 'cardiology'
      },
      {
        id: 3,
        query: 'covid-19 síntomas neurológicos',
        date: new Date(2024, 0, 12),
        resultsCount: 45,
        categoryKey: 'neurology'
      },
      {
        id: 4,
        query: 'cáncer de mama screening',
        date: new Date(2024, 0, 10),
        resultsCount: 203,
        categoryKey: 'oncology'
      },
      {
        id: 5,
        query: 'insuficiencia renal crónica',
        date: new Date(2024, 0, 8),
        resultsCount: 156,
        categoryKey: 'nephrology'
      }
    ];
    
    setTimeout(() => {
      setSearchHistory(mockHistory);
      setFilteredHistory(mockHistory);
      setLoading(false);
    }, 1000);
  }, []);

  // Filtrar historial
  useEffect(() => {
    let filtered = searchHistory;

    // Filtro por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t(`history.categories.${item.categoryKey}`, item.categoryKey).toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtro por fecha
    if (dateFilter !== 'all') {
      const now = new Date();
      const filterDate = new Date();
      
      switch (dateFilter) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0);
          filtered = filtered.filter(item => item.date >= filterDate);
          break;
        case 'week':
          filterDate.setDate(now.getDate() - 7);
          filtered = filtered.filter(item => item.date >= filterDate);
          break;
        case 'month':
          filterDate.setMonth(now.getMonth() - 1);
          filtered = filtered.filter(item => item.date >= filterDate);
          break;
      }
    }

    setFilteredHistory(filtered);
  }, [searchHistory, searchTerm, dateFilter]);

  const deleteSearch = (id) => {
    setSearchHistory(prev => prev.filter(item => item.id !== id));
  };

  const clearAll = () => {
    if (window.confirm(t('history.confirmClear', '¿Estás seguro de que quieres borrar todo el historial?'))) {
      setSearchHistory([]);
      setFilteredHistory([]);
    }
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-6"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <History className="w-8 h-8 text-primary-600 dark:text-primary-400" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {t('history.title', 'Historial de Búsquedas')}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {t('history.subtitle', 'Revisa y gestiona tus búsquedas anteriores')}
            </p>
          </div>
        </div>
        
        {searchHistory.length > 0 && (
          <div className="flex space-x-2">
            <Button variant="secondary" size="sm">
              <Download className="w-4 h-4 mr-2" />
              {t('history.export', 'Exportar')}
            </Button>
            <Button variant="danger" size="sm" onClick={clearAll}>
              <Trash2 className="w-4 h-4 mr-2" />
              {t('history.clearAll', 'Limpiar todo')}
            </Button>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search filter */}
          <div className="flex-1">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder={t('history.searchPlaceholder', 'Buscar en el historial...')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          
          {/* Date filter */}
          <div className="sm:w-48">
            <select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">{t('history.allTime', 'Todo el tiempo')}</option>
              <option value="today">{t('history.today', 'Hoy')}</option>
              <option value="week">{t('history.lastWeek', 'Última semana')}</option>
              <option value="month">{t('history.lastMonth', 'Último mes')}</option>
            </select>
          </div>
        </div>
      </div>

      {/* History List */}
      <div className="space-y-4">
        {filteredHistory.length === 0 ? (
          <div className="text-center py-12">
            <History className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {searchHistory.length === 0 
                ? t('history.noHistory', 'No hay historial de búsquedas')
                : t('history.noResults', 'No se encontraron búsquedas')
              }
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              {searchHistory.length === 0
                ? t('history.startSearching', 'Comienza a buscar para ver tu historial aquí')
                : t('history.tryDifferentFilter', 'Prueba con diferentes filtros')
              }
            </p>
          </div>
        ) : (
          filteredHistory.map((item) => (
            <div
              key={item.id}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:border-primary-300 dark:hover:border-primary-600 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <Search className="w-4 h-4 text-primary-600 dark:text-primary-400 flex-shrink-0" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                      "{item.query}"
                    </h3>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{formatDate(item.date)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <FileText className="w-4 h-4" />
                      <span>{item.resultsCount} {t('history.results')}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Filter className="w-4 h-4" />
                      <span>{t(`history.categories.${item.categoryKey}`, item.categoryKey)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <Button variant="ghost" size="sm" title={t('history.viewResults', 'Ver resultados')}>
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => deleteSearch(item.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                    title={t('history.delete', 'Eliminar')}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination placeholder */}
      {filteredHistory.length > 10 && (
        <div className="mt-8 text-center">
          <Button variant="secondary">
            {t('history.loadMore', 'Cargar más')}
          </Button>
        </div>
      )}
    </div>
  );
};

export default SearchHistory;