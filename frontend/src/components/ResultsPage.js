// src/components/ResultsPage.js
import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, X, Calendar, User, ChevronLeft, ChevronRight, Filter, Check, Bookmark, FileText, Sparkles } from 'lucide-react';
import DynamicTranslation from './DynamicTranslation';
import SourceLogo from './SourceLogo';
import Button from './ui/Button';
import clsx from 'clsx';
import authService from '../services/authService';
import favoritesService from '../services/favoritesService';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import AIAssistantModal from './AIAssistantModal';

// Colores para categorías médicas - Paleta única de 24 colores
const categoryColors = {
  // Cardiology - Red
  'cardiologia': 'bg-red-100 text-red-900 dark:bg-red-900 dark:text-red-100',
  'cardiología': 'bg-red-100 text-red-900 dark:bg-red-900 dark:text-red-100',
  'cardiology': 'bg-red-100 text-red-900 dark:bg-red-900 dark:text-red-100',
  // Neurology - Violet
  'neurologia': 'bg-violet-100 text-violet-900 dark:bg-violet-900 dark:text-violet-100',
  'neurología': 'bg-violet-100 text-violet-900 dark:bg-violet-900 dark:text-violet-100',
  'neurology': 'bg-violet-100 text-violet-900 dark:bg-violet-900 dark:text-violet-100',
  // Oncology - Pink
  'oncologia': 'bg-pink-100 text-pink-900 dark:bg-pink-900 dark:text-pink-100',
  'oncología': 'bg-pink-100 text-pink-900 dark:bg-pink-900 dark:text-pink-100',
  'oncology': 'bg-pink-100 text-pink-900 dark:bg-pink-900 dark:text-pink-100',
  // Pediatrics - Green
  'pediatria': 'bg-green-100 text-green-900 dark:bg-green-900 dark:text-green-100',
  'pediatría': 'bg-green-100 text-green-900 dark:bg-green-900 dark:text-green-100',
  'pediatrics': 'bg-green-100 text-green-900 dark:bg-green-900 dark:text-green-100',
  // Dermatology - Rose
  'dermatologia': 'bg-rose-100 text-rose-900 dark:bg-rose-900 dark:text-rose-100',
  'dermatología': 'bg-rose-100 text-rose-900 dark:bg-rose-900 dark:text-rose-100',
  'dermatology': 'bg-rose-100 text-rose-900 dark:bg-rose-900 dark:text-rose-100',
  // Psychiatry - Indigo
  'psiquiatria': 'bg-indigo-100 text-indigo-900 dark:bg-indigo-900 dark:text-indigo-100',
  'psiquiatría': 'bg-indigo-100 text-indigo-900 dark:bg-indigo-900 dark:text-indigo-100',
  'psychiatry': 'bg-indigo-100 text-indigo-900 dark:bg-indigo-900 dark:text-indigo-100',
  // Obstetrics and Gynecology - Yellow
  'obstetricia y ginecologia': 'bg-yellow-100 text-yellow-900 dark:bg-yellow-900 dark:text-yellow-100',
  'obstetricia y ginecología': 'bg-yellow-100 text-yellow-900 dark:bg-yellow-900 dark:text-yellow-100',
  'obstetrics and gynecology': 'bg-yellow-100 text-yellow-900 dark:bg-yellow-900 dark:text-yellow-100',
  // Orthopedics - Orange
  'traumatologia': 'bg-orange-100 text-orange-900 dark:bg-orange-900 dark:text-orange-100',
  'traumatología': 'bg-orange-100 text-orange-900 dark:bg-orange-900 dark:text-orange-100',
  'orthopedics': 'bg-orange-100 text-orange-900 dark:bg-orange-900 dark:text-orange-100',
  // Ophthalmology - Cyan
  'oftalmologia': 'bg-cyan-100 text-cyan-900 dark:bg-cyan-900 dark:text-cyan-100',
  'oftalmología': 'bg-cyan-100 text-cyan-900 dark:bg-cyan-900 dark:text-cyan-100',
  'ophthalmology': 'bg-cyan-100 text-cyan-900 dark:bg-cyan-900 dark:text-cyan-100',
  // Otolaryngology - Teal
  'otorrinolaringologia': 'bg-teal-100 text-teal-900 dark:bg-teal-900 dark:text-teal-100',
  'otorrinolaringología': 'bg-teal-100 text-teal-900 dark:bg-teal-900 dark:text-teal-100',
  'otolaryngology': 'bg-teal-100 text-teal-900 dark:bg-teal-900 dark:text-teal-100',
  // Endocrinology - Lime
  'endocrinologia': 'bg-lime-100 text-lime-900 dark:bg-lime-900 dark:text-lime-100',
  'endocrinología': 'bg-lime-100 text-lime-900 dark:bg-lime-900 dark:text-lime-100',
  'endocrinology': 'bg-lime-100 text-lime-900 dark:bg-lime-900 dark:text-lime-100',
  // Urology - Blue
  'urologia': 'bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100',
  'urología': 'bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100',
  'urology': 'bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100',
  // Gastroenterology - Amber (oscuro)
  'gastroenterologia': 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-100',
  'gastroenterología': 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-100',
  'gastroenterology': 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-100',
  // Medical Genetics - Fuchsia
  'genetica medica': 'bg-fuchsia-100 text-fuchsia-900 dark:bg-fuchsia-900 dark:text-fuchsia-100',
  'genética médica': 'bg-fuchsia-100 text-fuchsia-900 dark:bg-fuchsia-900 dark:text-fuchsia-100',
  'medical genetics': 'bg-fuchsia-100 text-fuchsia-900 dark:bg-fuchsia-900 dark:text-fuchsia-100',
  // Geriatrics - Stone
  'geriatria': 'bg-stone-300 text-stone-950 dark:bg-stone-700 dark:text-stone-200',
  'geriatría': 'bg-stone-300 text-stone-950 dark:bg-stone-700 dark:text-stone-200',
  'geriatrics': 'bg-stone-300 text-stone-950 dark:bg-stone-700 dark:text-stone-200',
  // Infectious Disease - Purple
  'infectologia': 'bg-purple-100 text-purple-600 dark:bg-purple-600 dark:text-purple-100',
  'infectología': 'bg-purple-100 text-purple-600 dark:bg-purple-600 dark:text-purple-100',
  'infectious disease': 'bg-purple-100 text-purple-600 dark:bg-purple-600 dark:text-purple-100',
  // Immunology - Emerald
  'inmunologia': 'bg-emerald-100 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-100',
  'inmunología': 'bg-emerald-100 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-100',
  'immunology': 'bg-emerald-100 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-100',
  // Nephrology - Sky
  'nefrologia': 'bg-sky-100 text-sky-900 dark:bg-sky-900 dark:text-sky-100',
  'nefrología': 'bg-sky-100 text-sky-900 dark:bg-sky-900 dark:text-sky-100',
  'nephrology': 'bg-sky-100 text-sky-900 dark:bg-sky-900 dark:text-sky-100',
  // Pulmonology - Indigo (oscuro)
  'neumologia': 'bg-indigo-200 text-indigo-950 dark:bg-indigo-950 dark:text-indigo-200',
  'neumología': 'bg-indigo-200 text-indigo-950 dark:bg-indigo-950 dark:text-indigo-200',
  'pulmonology': 'bg-indigo-200 text-indigo-950 dark:bg-indigo-950 dark:text-indigo-200',
  // Rheumatology - Red oscuro
  'reumatologia': 'bg-red-200 text-red-950 dark:bg-red-950 dark:text-red-200',
  'reumatología': 'bg-red-200 text-red-950 dark:bg-red-950 dark:text-red-200',
  'rheumatology': 'bg-red-200 text-red-950 dark:bg-red-950 dark:text-red-200',
  // General Medicine - Gray
  'medicina general': 'bg-gray-200 text-gray-800 dark:bg-gray-600 dark:text-gray-100',
  'general medicine': 'bg-gray-200 text-gray-800 dark:bg-gray-600 dark:text-gray-100',
  // Internal Medicine - Zinc
  'medicina interna': 'bg-zinc-100 text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100',
  'internal medicine': 'bg-zinc-100 text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100',
  // Radiology - Violet oscuro
  'radiologia': 'bg-violet-200 text-violet-950 dark:bg-violet-950 dark:text-violet-200',
  'radiología': 'bg-violet-200 text-violet-950 dark:bg-violet-950 dark:text-violet-200',
  'radiology': 'bg-violet-200 text-violet-950 dark:bg-violet-950 dark:text-violet-200',
  // Anesthesiology - Teal oscuro
  'anestesiologia': 'bg-teal-200 text-teal-950 dark:bg-teal-950 dark:text-teal-200',
  'anestesiología': 'bg-teal-200 text-teal-950 dark:bg-teal-950 dark:text-teal-200',
  'anesthesiology': 'bg-teal-200 text-teal-950 dark:bg-teal-950 dark:text-teal-200',
  // Hematology - Pink oscuro
  'hematologia': 'bg-pink-200 text-pink-950 dark:bg-pink-950 dark:text-pink-200',
  'hematología': 'bg-pink-200 text-pink-950 dark:bg-pink-950 dark:text-pink-200',
  'hematology': 'bg-pink-200 text-pink-950 dark:bg-pink-950 dark:text-pink-200',
  'default': 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
};








const getCategoryColor = (categoryName) => {
  if (!categoryName) return categoryColors.default;
  const normalizedName = categoryName.toLowerCase().trim();
  return categoryColors[normalizedName] || categoryColors.default;
};

const ResultsPage = ({ query, results, isLoading, onSearch, onSelectDocument, selectedDocument, searchMetadata }) => {
  const [searchInput, setSearchInput] = useState(query);
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  const toast = useToast();
  const previewPanelRef = useRef(null);

  // Estados para favoritos
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteId, setFavoriteId] = useState(null);
  const [isFavoriteLoading, setIsFavoriteLoading] = useState(false);

  // Estado para el modal del asistente IA
  const [isAIAssistantModalOpen, setIsAIAssistantModalOpen] = useState(false);

  // Estado para preferencias del usuario (cargadas desde la API)
  const [itemsPerPage, setItemsPerPage] = useState(25); // Número de resultados por página
  const [defaultSort, setDefaultSort] = useState('relevance'); // Orden por defecto (relevance, date, author)

  // Cargar preferencias del usuario al montar el componente
  useEffect(() => {
    const loadUserPreferences = async () => {
      try {
        const token = authService.getToken();
        if (!token) {
          // Si no hay token, usar valores por defecto
          return;
        }

        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/preferences`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Preferencias cargadas en ResultsPage:', data); // Debug

          // El backend devuelve camelCase gracias a by_alias=False
          // Aplicar preferencias de paginación y ordenamiento
          setItemsPerPage(data.resultsPerPage || data.results_per_page || 25);
          setDefaultSort(data.defaultSort || data.default_sort || 'relevance');
        }
      } catch (error) {
        console.error('Error loading user preferences:', error);
        // En caso de error, mantener valores por defecto
      }
    };

    loadUserPreferences();
  }, []); // Solo se ejecuta una vez al montar el componente

  // Escuchar cambios en preferencias desde SettingsModal
  useEffect(() => {
    const handlePreferencesChange = (event) => {
      const { field, value } = event.detail;
      console.log('ResultsPage recibió cambio de preferencia:', field, '=', value); // Debug

      if (field === 'resultsPerPage') {
        setItemsPerPage(value);
        setCurrentPage(1); // Reset a la primera página cuando cambia items per page
      } else if (field === 'defaultSort') {
        setDefaultSort(value);
      }
    };

    // Agregar listener para el evento personalizado
    window.addEventListener('preferencesChanged', handlePreferencesChange);

    // Cleanup al desmontar
    return () => {
      window.removeEventListener('preferencesChanged', handlePreferencesChange);
    };
  }, []);

  // Extraer todas las categorías únicas de los resultados
  const availableCategories = React.useMemo(() => {
    const categories = new Set();
    results.forEach(doc => {
      if (doc.categoria?.nombre) {
        categories.add(doc.categoria.nombre);
      }
    });
    return Array.from(categories).sort();
  }, [results]);

  // Aplicar filtros y ordenamiento a los resultados
  const filteredAndSortedResults = React.useMemo(() => {
    let filtered = [...results];

    // 1. Filtrar por categorías seleccionadas
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(doc =>
        doc.categoria?.nombre && selectedCategories.includes(doc.categoria.nombre)
      );
    }

    // 2. Filtrar por rango de fechas
    if (dateFrom || dateTo) {
      filtered = filtered.filter(doc => {
        if (!doc.fecha_publicacion) return false;
        const docDate = new Date(doc.fecha_publicacion);

        if (dateFrom && dateTo) {
          return docDate >= new Date(dateFrom) && docDate <= new Date(dateTo);
        } else if (dateFrom) {
          return docDate >= new Date(dateFrom);
        } else if (dateTo) {
          return docDate <= new Date(dateTo);
        }
        return true;
      });
    }

    // 3. Aplicar ordenamiento según preferencia del usuario
    // IMPORTANTE: No se filtran resultados, solo se reordenan
    if (defaultSort === 'date') {
      // Ordenar por fecha de publicación (más reciente primero)
      filtered.sort((a, b) => {
        const dateA = a.fecha_publicacion ? new Date(a.fecha_publicacion) : new Date(0);
        const dateB = b.fecha_publicacion ? new Date(b.fecha_publicacion) : new Date(0);
        return dateB - dateA; // Descendente (más reciente primero)
      });
    } else if (defaultSort === 'author') {
      // Ordenar por autor (alfabéticamente)
      filtered.sort((a, b) => {
        const authorA = (a.autor && a.autor.length > 0 ? a.autor[0] : '').toLowerCase();
        const authorB = (b.autor && b.autor.length > 0 ? b.autor[0] : '').toLowerCase();
        return authorA.localeCompare(authorB);
      });
    }
    // Si defaultSort === 'relevance', mantener el orden original de la API
    // (que ya viene ordenado por relevancia desde el backend)

    return filtered;
  }, [results, selectedCategories, dateFrom, dateTo, defaultSort]);

  // Cálculos de paginación del lado del cliente
  // Usa itemsPerPage de las preferencias del usuario
  const totalItems = filteredAndSortedResults.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedResults = filteredAndSortedResults.slice(startIndex, endIndex);

  // Reset pagination when results or filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [results, selectedCategories, dateFrom, dateTo]);

  // Reset filters when results change (new search)
  useEffect(() => {
    setSelectedCategories([]);
    setDateFrom('');
    setDateTo('');
  }, [results]);

  // Limpiar el documento seleccionado cuando cambian los resultados o cuando están vacíos
  useEffect(() => {
    if (results.length === 0) {
      onSelectDocument(null);
    }
  }, [results, onSelectDocument]);

  // Limpiar selección si el documento seleccionado ya no está en los resultados
  useEffect(() => {
    if (selectedDocument && !results.some(doc => doc.id_documento === selectedDocument.id_documento)) {
      onSelectDocument(null);
    }
  }, [results, selectedDocument, onSelectDocument]);

  // Verificar si el documento seleccionado está en favoritos
  useEffect(() => {
    const checkFavoriteStatus = async () => {
      if (!selectedDocument || !isAuthenticated) {
        setIsFavorite(false);
        setFavoriteId(null);
        return;
      }

      try {
        setIsFavoriteLoading(true);
        const response = await favoritesService.checkIfFavorite(selectedDocument.id_documento);
        setIsFavorite(response.is_favorite);
        setFavoriteId(response.favorite_id);
      } catch (error) {
        console.error('Error checking favorite status:', error);
      } finally {
        setIsFavoriteLoading(false);
      }
    };

    checkFavoriteStatus();
  }, [selectedDocument, isAuthenticated]);

  // Función para añadir/eliminar favorito
  const handleToggleFavorite = async () => {
    if (!isAuthenticated) {
      toast.info(t('favorites.loginRequired', 'Debes iniciar sesión para guardar favoritos'));
      return;
    }

    if (!selectedDocument) return;

    try {
      setIsFavoriteLoading(true);

      if (isFavorite && favoriteId) {
        // Eliminar de favoritos
        await favoritesService.removeFavorite(favoriteId);
        setIsFavorite(false);
        setFavoriteId(null);
        toast.warning(t('favorites.removedFromFavorites'));
      } else {
        // Añadir a favoritos
        const response = await favoritesService.addFavorite(selectedDocument);
        setIsFavorite(true);
        setFavoriteId(response.id);
        toast.success(t('favorites.addedToFavorites'));
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      if (isFavorite) {
        toast.error(t('favorites.errorRemoving'));
      } else {
        toast.error(t('favorites.errorAdding'));
      }
    } finally {
      setIsFavoriteLoading(false);
    }
  };


  // Función para manejar la selección/deselección de documentos
  const handleDocumentSelection = (doc) => {
    // Si el documento ya está seleccionado, lo deseleccionamos
    if (selectedDocument && selectedDocument.id_documento === doc.id_documento) {
      onSelectDocument(null);
    } else {
      // Si no, lo seleccionamos
      onSelectDocument(doc);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      // Limpiar el documento seleccionado cuando se hace una nueva búsqueda
      onSelectDocument(null);
      setCurrentPage(1);
      onSearch(searchInput);
    }
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleGoToPage = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Generar números de página estilo Google
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 7; // Mostrar máximo 7 páginas

    if (totalPages <= maxPagesToShow) {
      // Si hay pocas páginas, mostrar todas
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Lógica estilo Google
      if (currentPage <= 4) {
        // Al principio: 1 2 3 4 5 ... último
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 3) {
        // Al final: 1 ... antepenúltimo-2 antepenúltimo-1 antepenúltimo penúltimo último
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        // En medio: 1 ... actual-1 actual actual+1 ... último
        pages.push(1);
        pages.push('...');
        pages.push(currentPage - 1);
        pages.push(currentPage);
        pages.push(currentPage + 1);
        pages.push('...');
        pages.push(totalPages);
      }
    }

    return pages;
  };

  const formatDate = (dateString) => {
    if (!dateString) return t('results.dateNotAvailable');
    const date = new Date(dateString);
    return date.toLocaleDateString(navigator.language || 'es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const toggleCategory = (categoryName) => {
    setSelectedCategories(prev =>
      prev.includes(categoryName)
        ? prev.filter(c => c !== categoryName)
        : [...prev, categoryName]
    );
  };

  const clearFilters = () => {
    setSelectedCategories([]);
    setDateFrom('');
    setDateTo('');
  };

  const hasActiveFilters = selectedCategories.length > 0 || dateFrom || dateTo;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {t('results.title')}
        </h1>
        <h2 className="text-lg text-gray-600 dark:text-gray-400 mb-6">
          "{query}"
        </h2>
      </div>
      
      <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto px-4 sm:px-6 lg:px-0 sticky top-[4.5rem] z-10 mb-8">
        <div className="flex">
          <input
            type="text"
            className="flex-1 px-3 py-2 sm:px-4 sm:py-3 border border-gray-300 dark:border-gray-600 rounded-l-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-sm sm:text-base"
            placeholder={t('search.placeholder')}
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            aria-label="Campo de búsqueda"
          />
          <Button
            type="submit"
            disabled={isLoading || !searchInput.trim()}
            loading={isLoading}
            className="rounded-l-none border-l-0 px-3 sm:px-4"
            aria-label={t('search.button')}
          >
            <Search className="w-4 h-4 sm:w-5 sm:h-5" />
          </Button>
        </div>
      </form>

      {/* Filters Section */}
      {!isLoading && results.length > 0 && (
        <div className="w-full max-w-7xl mx-auto mb-6">
          <div className="flex items-center justify-between mb-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              {showFilters ? t('results.hideFilters') : t('results.showFilters')}
              {hasActiveFilters && (
                <span className="ml-2 px-2 py-0.5 text-xs bg-primary-500 text-white rounded-full">
                  {selectedCategories.length + (dateFrom ? 1 : 0) + (dateTo ? 1 : 0)}
                </span>
              )}
            </Button>
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="text-sm"
              >
                {t('results.clearFilters')}
              </Button>
            )}
          </div>

          {showFilters && (
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-4">
              {/* Category Filter */}
              {availableCategories.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                    {t('results.filterByCategory')}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {availableCategories.map(category => {
                      const isSelected = selectedCategories.includes(category);
                      return (
                        <button
                          key={category}
                          onClick={() => toggleCategory(category)}
                          className={clsx(
                            'inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-full transition-all',
                            getCategoryColor(category),
                            isSelected
                              ? 'ring-2 ring-offset-2 ring-primary-500 dark:ring-offset-gray-800'
                              : 'opacity-60 hover:opacity-100'
                          )}
                        >
                          {isSelected && <Check className="w-3 h-3" />}
                          <DynamicTranslation contentLanguage="es">
                            {category}
                          </DynamicTranslation>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Date Filter */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                  {t('results.filterByDate')}
                </h3>
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="flex-1">
                    <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                      {t('results.dateFrom')}
                    </label>
                    <input
                      type="date"
                      value={dateFrom}
                      onChange={(e) => setDateFrom(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                      {t('results.dateTo')}
                    </label>
                    <input
                      type="date"
                      value={dateTo}
                      onChange={(e) => setDateTo(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="mt-8">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">{t('results.loading')}</p>
          </div>
        ) : results.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-2">{t('results.noResults')}</p>
            <p className="text-gray-500 dark:text-gray-500">{t('results.tryAgain')}</p>
          </div>
        ) : (
          <div>
            <div className={clsx('grid gap-6', selectedDocument ? 'lg:grid-cols-2' : 'grid-cols-1')}>
              <div className="space-y-4">
                {paginatedResults.map((doc) => (
                  <div 
                    key={doc.id_documento} 
                    className={clsx(
                      'result-item bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 cursor-pointer transition-all duration-200 hover:shadow-lg border border-gray-200 dark:border-gray-700',
                      selectedDocument && selectedDocument.id_documento === doc.id_documento && 'ring-2 ring-primary-500 border-primary-500'
                    )}
                    onClick={() => handleDocumentSelection(doc)}
                  >
                    <div className="mb-3">
                      <span className={clsx(
                        'inline-block px-3 py-1 text-xs font-medium rounded-full',
                        getCategoryColor(doc.categoria?.nombre)
                      )}>
                        {doc.categoria ? (
                          <DynamicTranslation contentLanguage="es">
                            {doc.categoria.nombre}
                          </DynamicTranslation>
                        ) : t('results.noCategory')}
                      </span>
                    </div>
                    
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 line-clamp-2">
                      <DynamicTranslation contentLanguage="en">
                        {doc.titulo}
                      </DynamicTranslation>
                    </h3>
                    
                    <div className="mb-4">
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400 mb-2">
                        <User className="w-4 h-4 mr-1 flex-shrink-0" />
                        <span className="truncate">
                          {doc.autor && doc.autor.length > 0 
                            ? doc.autor.join(', ') 
                            : t('results.unknownAuthor')}
                        </span>
                      </div>
                    </div>
                    
                    <p className="text-gray-700 dark:text-gray-300 mb-4 line-clamp-3">
                      <DynamicTranslation contentLanguage="en">
                        {doc.texto_resumen || t('results.noSummary')}
                      </DynamicTranslation>
                    </p>
                    
                    <div className="flex justify-between items-end">
                      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <Calendar className="w-4 h-4 mr-1" />
                        <span>{formatDate(doc.fecha_publicacion)}</span>
                      </div>
                      <a
                        href={doc.url_fuente}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-4 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <span className="mr-2">
                          <SourceLogo url={doc.url_fuente} size="sm" />
                        </span>
                        {t('results.source')}
                      </a>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Preview Panel */}
              {selectedDocument && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 sticky top-[9.5rem] h-fit max-h-[calc(100vh-11rem)] overflow-y-auto custom-scrollbar" ref={previewPanelRef}>
                  <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white pr-8">
                        <DynamicTranslation contentLanguage="en">
                          {selectedDocument.titulo}
                        </DynamicTranslation>
                      </h3>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {/* Botón de favorito */}
                        {isAuthenticated && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleToggleFavorite}
                            disabled={isFavoriteLoading}
                            className={clsx(
                              'p-2 transition-colors',
                              isFavorite
                                ? 'text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300'
                                : 'text-gray-400 hover:text-primary-600 dark:text-gray-500 dark:hover:text-primary-400'
                            )}
                            aria-label={isFavorite ? t('favorites.removeFromFavorites') : t('favorites.addToFavorites')}
                            title={isFavorite ? t('favorites.removeFromFavorites') : t('favorites.addToFavorites')}
                          >
                            <Bookmark
                              className={clsx(
                                'w-5 h-5 transition-all',
                                isFavorite && 'fill-current'
                              )}
                            />
                          </Button>
                        )}
                        {/* Botón de cerrar */}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onSelectDocument(null)}
                          className="p-2"
                          aria-label="Cerrar vista previa"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                      <span className={clsx(
                        'inline-block px-3 py-1 text-xs font-medium rounded-full',
                        getCategoryColor(selectedDocument.categoria?.nombre)
                      )}>
                        {selectedDocument.categoria ? (
                          <DynamicTranslation contentLanguage="es">
                            {selectedDocument.categoria.nombre}
                          </DynamicTranslation>
                        ) : t('results.noCategory')}
                      </span>
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        <span>{formatDate(selectedDocument.fecha_publicacion)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-6">
                    <div className="mb-6">
                      <div className="flex items-center text-gray-700 dark:text-gray-300 mb-2">
                        <User className="w-4 h-4 mr-2" />
                        <span className="font-medium">{t('results.authors')}</span>
                      </div>
                      <p className="text-[15px] text-gray-600 dark:text-gray-400 ml-6">
                        {selectedDocument.autor && selectedDocument.autor.length > 0
                          ? selectedDocument.autor.join(', ')
                          : t('results.unknownAuthor')}
                      </p>
                    </div>

                    <div className="mb-6">
                      <div className="flex items-center text-gray-700 dark:text-gray-300 mb-2">
                        <FileText className="w-4 h-4 mr-2" />
                        <span className="font-medium">{t('results.summary')}</span>
                      </div>
                      <div className="text-[15px] text-gray-600 dark:text-gray-400 ml-6 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg leading-relaxed">
                        <DynamicTranslation contentLanguage="en">
                          {selectedDocument.texto_resumen || t('results.noSummary')}
                        </DynamicTranslation>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <Button
                        variant="primary"
                        className="w-full"
                        onClick={() => window.open(selectedDocument.url_fuente, '_blank')}
                      >
                        <span className="mr-2">
                          <SourceLogo url={selectedDocument.url_fuente} size="sm" />
                        </span>
                        {t('results.viewFull')}
                      </Button>

                      {isAuthenticated && (
                        <Button
                          variant="ghost"
                          className="w-full flex items-center justify-center gap-2"
                          onClick={() => setIsAIAssistantModalOpen(true)}
                        >
                          <Sparkles className="w-4 h-4" />
                          {t('aiAssistant.consultDocument', 'Consultar con asistente')}
                          <span className="ml-2 px-2 py-0.5 text-xs bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 rounded-full">
                            {t('aiAssistant.comingSoon', 'Próximamente')}
                          </span>
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Pagination Controls */}
            {totalItems > 0 && (
              <div className="flex flex-col sm:flex-row justify-between items-center gap-4 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg mt-8">
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {t('results.showingResults', {
                      start: startIndex + 1,
                      end: Math.min(endIndex, totalItems),
                      total: totalItems
                    })}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handlePrevPage}
                    disabled={currentPage === 1 || isLoading}
                    className="px-3 py-1"
                  >
                    <ChevronLeft className="w-4 h-4 mr-1" />
                    {t('results.previous')}
                  </Button>

                  {/* Page Numbers */}
                  <div className="flex items-center gap-1">
                    {getPageNumbers().map((pageNum, index) => (
                      pageNum === '...' ? (
                        <span
                          key={`ellipsis-${index}`}
                          className="px-2 text-gray-400 dark:text-gray-500"
                        >
                          ...
                        </span>
                      ) : (
                        <Button
                          key={pageNum}
                          variant={currentPage === pageNum ? 'primary' : 'ghost'}
                          size="sm"
                          onClick={() => handleGoToPage(pageNum)}
                          disabled={isLoading}
                          className={clsx(
                            'px-3 py-1 min-w-[2.5rem]',
                            currentPage === pageNum && 'font-semibold'
                          )}
                        >
                          {pageNum}
                        </Button>
                      )
                    ))}
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleNextPage}
                    disabled={currentPage >= totalPages || isLoading}
                    className="px-3 py-1"
                  >
                    {t('results.next')}
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </div>
            )}

            {/* Mensaje informativo sobre resultados filtrados */}
            {totalItems > 0 && searchMetadata?.filteredBySimilarity && (
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <p className="text-sm text-blue-800 dark:text-blue-200 text-center">
                  {t('results.filteredResultsInfo')}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* AI Assistant Modal */}
      <AIAssistantModal
        isOpen={isAIAssistantModalOpen}
        onClose={() => setIsAIAssistantModalOpen(false)}
      />
    </div>
  );
};

export default ResultsPage;