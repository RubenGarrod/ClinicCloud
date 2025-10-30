/**
 * PÁGINA DE FAVORITOS
 * ===================
 * Muestra los documentos favoritos del usuario autenticado
 *
 * Copyright (C) 2025 Rubén García Rodríguez
 * Licensed under GPL-3.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import favoritesService from '../services/favoritesService';
import { Bookmark, Calendar, User, Trash2, Search, Filter, X, FileText, Edit3, Save, Tag, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import DynamicTranslation from '../components/DynamicTranslation';
import SourceLogo from '../components/SourceLogo';
import Button from '../components/ui/Button';
import Modal from '../components/ui/Modal';
import AIAssistantModal from '../components/AIAssistantModal';
import clsx from 'clsx';

// Colores completos para categorías médicas (mismo que ResultsPage)
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
  // Gastroenterology - Amber
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
  // Pulmonology - Indigo
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

const FavoritesPage = () => {
  const { t } = useTranslation();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const previewPanelRef = useRef(null);

  const [favorites, setFavorites] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedTag, setSelectedTag] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [deleteConfirmModal, setDeleteConfirmModal] = useState({ isOpen: false, favoriteId: null });
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [editedNotes, setEditedNotes] = useState('');
  const [editedTags, setEditedTags] = useState([]);
  const [newTag, setNewTag] = useState('');
  const [isSavingChanges, setIsSavingChanges] = useState(false);
  const [showTags, setShowTags] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
  const [showTagDropdown, setShowTagDropdown] = useState(false);
  const [isAIAssistantModalOpen, setIsAIAssistantModalOpen] = useState(false);

  // Cargar favoritos al montar el componente
  useEffect(() => {
    if (authLoading) return;

    if (!isAuthenticated) {
      navigate('/');
      return;
    }

    loadFavorites();
  }, [isAuthenticated, authLoading, navigate]);

  const loadFavorites = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await favoritesService.getFavorites();
      setFavorites(data);
    } catch (err) {
      console.error('Error loading favorites:', err);
      setError(err.message);
      toast.error(t('favorites.errorLoading'));
    } finally {
      setIsLoading(false);
    }
  };

  // Inicializar notas y tags cuando se selecciona un documento
  useEffect(() => {
    if (selectedDocument) {
      setEditedNotes(selectedDocument.notes || '');
      setEditedTags(selectedDocument.tags || []);
      setIsEditingNotes(false);
      setNewTag('');
    }
  }, [selectedDocument]);

  const handleRemoveFavorite = async (favoriteId) => {
    try {
      await favoritesService.removeFavorite(favoriteId);
      setFavorites(prev => prev.filter(fav => fav.id !== favoriteId));
      if (selectedDocument && selectedDocument.id === favoriteId) {
        setSelectedDocument(null);
      }
      toast.warning(t('favorites.removedFromFavorites'));
      setDeleteConfirmModal({ isOpen: false, favoriteId: null });
    } catch (err) {
      console.error('Error removing favorite:', err);
      toast.error(t('favorites.errorRemoving'));
    }
  };

  const handleSaveNotesAndTags = async () => {
    if (!selectedDocument) return;

    try {
      setIsSavingChanges(true);
      const updates = {
        notes: editedNotes || null,
        tags: editedTags.length > 0 ? editedTags : []
      };

      const updatedFavorite = await favoritesService.updateFavorite(selectedDocument.id, updates);

      // Actualizar en el estado local
      setFavorites(prev => prev.map(fav =>
        fav.id === selectedDocument.id ? updatedFavorite : fav
      ));
      setSelectedDocument(updatedFavorite);
      setIsEditingNotes(false);
      toast.success(t('favorites.changesSaved', 'Cambios guardados'));
    } catch (err) {
      console.error('Error saving changes:', err);
      toast.error(t('favorites.errorSaving', 'Error al guardar cambios'));
    } finally {
      setIsSavingChanges(false);
    }
  };

  const handleAddTag = (tagToAdd = null) => {
    // Si tagToAdd es un string, usarlo; si no, usar newTag
    const tagValue = typeof tagToAdd === 'string' ? tagToAdd : newTag;
    const trimmedTag = tagValue.trim();
    if (trimmedTag && !editedTags.includes(trimmedTag)) {
      setEditedTags([...editedTags, trimmedTag]);
      setNewTag('');
      setShowTagDropdown(false);
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setEditedTags(editedTags.filter(tag => tag !== tagToRemove));
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

  // Extraer categorías únicas
  const availableCategories = React.useMemo(() => {
    const categories = new Set();
    favorites.forEach(fav => {
      if (fav.category) {
        categories.add(fav.category);
      }
    });
    return Array.from(categories).sort();
  }, [favorites]);

  // Extraer todos los tags únicos
  const availableTags = React.useMemo(() => {
    const tags = new Set();
    favorites.forEach(fav => {
      if (fav.tags && Array.isArray(fav.tags)) {
        fav.tags.forEach(tag => tags.add(tag));
      }
    });
    return Array.from(tags).sort();
  }, [favorites]);

  // Tags disponibles para el dropdown (excluyendo los ya añadidos al documento actual)
  const availableTagsForDropdown = React.useMemo(() => {
    if (!newTag.trim()) return availableTags;
    const lowerSearch = newTag.toLowerCase();
    return availableTags.filter(tag =>
      tag.toLowerCase().includes(lowerSearch) && !editedTags.includes(tag)
    );
  }, [availableTags, newTag, editedTags]);

  // Filtrar favoritos por categoría y tag
  const filteredFavorites = React.useMemo(() => {
    let filtered = favorites;

    if (selectedCategory) {
      filtered = filtered.filter(fav => fav.category === selectedCategory);
    }

    if (selectedTag) {
      filtered = filtered.filter(fav =>
        fav.tags && Array.isArray(fav.tags) && fav.tags.includes(selectedTag)
      );
    }

    return filtered;
  }, [favorites, selectedCategory, selectedTag]);

  if (authLoading || isLoading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">{t('favorites.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <Bookmark className="w-7 h-7 text-primary-600 dark:text-primary-400" />
              {t('favorites.title')}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {t('favorites.subtitle')}
            </p>
          </div>
        </div>

        {/* Filters */}
        {favorites.length > 0 && (availableCategories.length > 0 || availableTags.length > 0) && (
          <div className="mt-6">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              {showFilters ? t('results.hideFilters') : t('results.showFilters')}
              {(selectedCategory || selectedTag) && (
                <span className="ml-2 px-2 py-0.5 text-xs bg-primary-500 text-white rounded-full">
                  {(selectedCategory ? 1 : 0) + (selectedTag ? 1 : 0)}
                </span>
              )}
            </Button>

            {showFilters && (
              <div className="mt-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-6">
                {/* Filter by Category */}
                {availableCategories.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                        {t('favorites.filterByCategory')}
                      </h3>
                      {selectedCategory && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedCategory(null)}
                          className="text-xs"
                        >
                          {t('common.clear', 'Limpiar')}
                        </Button>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {availableCategories.map(category => {
                        const isSelected = selectedCategory === category;
                        return (
                          <button
                            key={category}
                            onClick={() => setSelectedCategory(isSelected ? null : category)}
                            className={clsx(
                              'inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-full transition-all',
                              getCategoryColor(category),
                              isSelected
                                ? 'ring-2 ring-offset-2 ring-primary-500 dark:ring-offset-gray-800'
                                : 'opacity-60 hover:opacity-100'
                            )}
                          >
                            <DynamicTranslation contentLanguage="es">
                              {category}
                            </DynamicTranslation>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Filter by Tag */}
                {availableTags.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                        {t('favorites.filterByTag', 'Filtrar por tag')}
                      </h3>
                      {selectedTag && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedTag(null)}
                          className="text-xs"
                        >
                          {t('common.clear', 'Limpiar')}
                        </Button>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {availableTags.map(tag => {
                        const isSelected = selectedTag === tag;
                        return (
                          <button
                            key={tag}
                            onClick={() => setSelectedTag(isSelected ? null : tag)}
                            className={clsx(
                              'inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-full transition-all',
                              'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200',
                              isSelected
                                ? 'ring-2 ring-offset-2 ring-primary-500 dark:ring-offset-gray-800'
                                : 'opacity-60 hover:opacity-100'
                            )}
                          >
                            <Tag className="w-3 h-3" />
                            {tag}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Clear all filters */}
                {(selectedCategory || selectedTag) && (
                  <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedCategory(null);
                        setSelectedTag(null);
                      }}
                      className="text-xs"
                    >
                      {t('favorites.clearFilters')}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Content */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
          <p className="text-red-800 dark:text-red-200">{error}</p>
          <Button
            variant="ghost"
            size="sm"
            onClick={loadFavorites}
            className="mt-2"
          >
            {t('favorites.retry')}
          </Button>
        </div>
      )}

      {filteredFavorites.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <Bookmark className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {t('favorites.empty')}
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {t('favorites.emptyDescription')}
          </p>
          <Button
            variant="primary"
            onClick={() => navigate('/')}
          >
            <Search className="w-4 h-4 mr-2" />
            {t('favorites.startSearching')}
          </Button>
        </div>
      ) : (
        <>
          {/* Results count */}
          <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            {t('favorites.showingResults', {
              start: 1,
              end: filteredFavorites.length,
              total: filteredFavorites.length
            })}
          </div>

          {/* Preview Panel - Arriba a ancho completo */}
          {selectedDocument && (
            <div
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 mb-6 overflow-hidden"
              ref={previewPanelRef}
            >
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white pr-8">
                    <DynamicTranslation contentLanguage="en">
                      {selectedDocument.document_title}
                    </DynamicTranslation>
                  </h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedDocument(null)}
                    className="p-2 flex-shrink-0"
                    aria-label="Cerrar vista previa"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span className={clsx(
                    'inline-block px-3 py-1 text-xs font-medium rounded-full',
                    getCategoryColor(selectedDocument.category)
                  )}>
                    <DynamicTranslation contentLanguage="es">
                      {selectedDocument.category || t('results.noCategory')}
                    </DynamicTranslation>
                  </span>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <Calendar className="w-4 h-4 mr-1" />
                    <span>{formatDate(selectedDocument.publication_date)}</span>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-6">
                {/* Authors */}
                <div>
                  <div className="flex items-center text-gray-700 dark:text-gray-300 mb-2">
                    <User className="w-4 h-4 mr-2" />
                    <span className="font-medium">{t('results.authors')}</span>
                  </div>
                  <p className="text-[15px] text-gray-600 dark:text-gray-400 ml-6">
                    {selectedDocument.authors && selectedDocument.authors.length > 0
                      ? selectedDocument.authors.join(', ')
                      : t('results.unknownAuthor')}
                  </p>
                </div>

                {/* Summary - Si existe en el documento */}
                {selectedDocument.document_summary && (
                  <div>
                    <div className="flex items-center text-gray-700 dark:text-gray-300 mb-2">
                      <FileText className="w-4 h-4 mr-2" />
                      <span className="font-medium">{t('results.summary')}</span>
                    </div>
                    <div className="text-[15px] text-gray-600 dark:text-gray-400 ml-6 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg leading-relaxed">
                      <DynamicTranslation contentLanguage="en">
                        {selectedDocument.document_summary}
                      </DynamicTranslation>
                    </div>
                  </div>
                )}

                {/* Tags and Notes - Side by side */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Tags */}
                  <div>
                  <button
                    onClick={() => setShowTags(!showTags)}
                    className="flex items-center justify-between w-full text-gray-700 dark:text-gray-300 mb-3 hover:text-gray-900 dark:hover:text-white transition-colors"
                  >
                    <div className="flex items-center">
                      <Tag className="w-4 h-4 mr-2" />
                      <span className="font-medium">{t('favorites.tags', 'Tags')}</span>
                      {editedTags.length > 0 && (
                        <span className="ml-2 px-2 py-0.5 text-xs bg-primary-500 text-white rounded-full">
                          {editedTags.length}
                        </span>
                      )}
                    </div>
                    {showTags ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                  {showTags && (
                    <div className="space-y-3">
                      {/* Tags display */}
                      {editedTags.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {editedTags.map((tag, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200"
                            >
                              {tag}
                              <button
                                onClick={() => handleRemoveTag(tag)}
                                className="hover:text-primary-600 dark:hover:text-primary-400"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm italic text-gray-400 dark:text-gray-500">
                          {t('favorites.noTags', 'Sin tags')}
                        </p>
                      )}
                      {/* Add tag input with dropdown */}
                      <div className="relative">
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={newTag}
                            onChange={(e) => {
                              setNewTag(e.target.value);
                              setShowTagDropdown(e.target.value.trim().length > 0);
                            }}
                            onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                            onFocus={() => newTag.trim().length > 0 && setShowTagDropdown(true)}
                            onBlur={() => setTimeout(() => setShowTagDropdown(false), 200)}
                            placeholder={t('favorites.addTag', 'Añadir tag...')}
                            className="flex-1 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleAddTag}
                            disabled={!newTag.trim()}
                            className="px-3"
                          >
                            {t('favorites.add', 'Añadir')}
                          </Button>
                        </div>
                        {/* Dropdown con tags existentes */}
                        {showTagDropdown && availableTagsForDropdown.length > 0 && (
                          <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                            {availableTagsForDropdown.map((tag, index) => (
                              <button
                                key={index}
                                onClick={() => handleAddTag(tag)}
                                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-600 flex items-center gap-2"
                              >
                                <Tag className="w-3 h-3 text-primary-600 dark:text-primary-400" />
                                <span className="text-gray-900 dark:text-white">{tag}</span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Notes */}
                <div>
                  <button
                    onClick={() => setShowNotes(!showNotes)}
                    className="flex items-center justify-between w-full text-gray-700 dark:text-gray-300 mb-3 hover:text-gray-900 dark:hover:text-white transition-colors"
                  >
                    <div className="flex items-center">
                      <Edit3 className="w-4 h-4 mr-2" />
                      <span className="font-medium">{t('favorites.notes', 'Notas personales')}</span>
                      {editedNotes && (
                        <span className="ml-2 w-2 h-2 bg-primary-500 rounded-full"></span>
                      )}
                    </div>
                    {showNotes ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                  {showNotes && (
                    <div className="space-y-3">
                    {isEditingNotes ? (
                      <>
                        {/* Textarea for editing */}
                        <textarea
                          value={editedNotes}
                          onChange={(e) => setEditedNotes(e.target.value)}
                          placeholder={t('favorites.notesPlaceholder', 'Escribe tus notas aquí...')}
                          className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent min-h-[100px] resize-y"
                        />
                        {/* Action buttons */}
                        <div className="flex gap-2 justify-end">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setEditedNotes(selectedDocument.notes || '');
                              setIsEditingNotes(false);
                            }}
                          >
                            {t('favorites.cancel', 'Cancelar')}
                          </Button>
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={handleSaveNotesAndTags}
                            disabled={isSavingChanges}
                            className="flex items-center gap-1"
                          >
                            <Save className="w-3 h-3" />
                            {isSavingChanges ? t('favorites.saving', 'Guardando...') : t('favorites.save', 'Guardar')}
                          </Button>
                        </div>
                      </>
                    ) : (
                      <>
                        {editedNotes ? (
                          <>
                            {/* Notes display */}
                            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-wrap">
                              {editedNotes}
                            </p>
                            {/* Edit button */}
                            <div className="flex justify-end">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setIsEditingNotes(true);
                                }}
                                className="text-xs"
                              >
                                {t('favorites.edit', 'Editar')}
                              </Button>
                            </div>
                          </>
                        ) : (
                          <div className="flex items-center justify-between">
                            <p className="text-sm italic text-gray-400 dark:text-gray-500">
                              {t('favorites.noNotes', 'Sin notas')}
                            </p>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                setIsEditingNotes(true);
                              }}
                              className="text-xs"
                            >
                              {t('favorites.addNote', 'Añadir nota')}
                            </Button>
                          </div>
                        )}
                      </>
                    )}
                    </div>
                  )}
                  </div>
                </div>

                {/* Save Changes Button - Solo si hay cambios sin guardar en tags */}
                {JSON.stringify(editedTags) !== JSON.stringify(selectedDocument.tags || []) &&
                  !isEditingNotes && (
                    <div className="pt-2">
                      <Button
                        variant="primary"
                        onClick={handleSaveNotesAndTags}
                        disabled={isSavingChanges}
                        className="w-full flex items-center justify-center gap-2"
                      >
                        <Save className="w-4 h-4" />
                        {isSavingChanges ? t('favorites.saving', 'Guardando...') : t('favorites.saveChanges', 'Guardar cambios')}
                      </Button>
                    </div>
                  )}

                {/* Actions */}
                <div className="space-y-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex gap-2">
                    <Button
                      variant="primary"
                      onClick={() => window.open(selectedDocument.document_url, '_blank')}
                      className="flex-1"
                    >
                      <SourceLogo url={selectedDocument.document_url} size="sm" className="mr-2" />
                      {t('results.source')}
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={() => setDeleteConfirmModal({ isOpen: true, favoriteId: selectedDocument.id })}
                      className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                      aria-label={t('favorites.removeFromFavorites')}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>

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
                </div>
              </div>
            </div>
          )}

          {/* Favorites Grid - 3 columnas */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredFavorites.map((favorite) => (
                <div
                  key={favorite.id}
                  className={clsx(
                    'bg-white dark:bg-gray-800 rounded-lg shadow-md border overflow-hidden transition-all duration-200 relative group',
                    selectedDocument?.id === favorite.id
                      ? 'border-primary-500 ring-2 ring-primary-500 shadow-lg'
                      : 'border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-primary-300'
                  )}
                >
                  <div className="p-6 cursor-pointer" onClick={() => setSelectedDocument(selectedDocument?.id === favorite.id ? null : favorite)}>
                    {/* Category Badge y botón de favorito */}
                    <div className="flex items-start justify-between mb-3">
                      {favorite.category && (
                        <span className={clsx(
                          'inline-block px-3 py-1 text-xs font-medium rounded-full',
                          getCategoryColor(favorite.category)
                        )}>
                          <DynamicTranslation contentLanguage="es">
                            {favorite.category}
                          </DynamicTranslation>
                        </span>
                      )}
                      <div className="flex items-center gap-2">
                        {/* Indicators for notes and tags */}
                        {favorite.notes && (
                          <Edit3 className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                        )}
                        {favorite.tags && favorite.tags.length > 0 && (
                          <div className="flex items-center gap-1 text-xs text-primary-600 dark:text-primary-400">
                            <Tag className="w-3 h-3" />
                            <span>{favorite.tags.length}</span>
                          </div>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirmModal({ isOpen: true, favoriteId: favorite.id });
                          }}
                          className={clsx(
                            'p-2 transition-colors',
                            'text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300'
                          )}
                          aria-label={t('favorites.removeFromFavorites')}
                          title={t('favorites.removeFromFavorites')}
                        >
                          <Bookmark className="w-5 h-5 fill-current transition-all" />
                        </Button>
                      </div>
                    </div>

                    {/* Title */}
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 line-clamp-2 min-h-[3.5rem]">
                      <DynamicTranslation contentLanguage="en">
                        {favorite.document_title}
                      </DynamicTranslation>
                    </h3>

                    {/* Authors */}
                    {favorite.authors && favorite.authors.length > 0 && (
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400 mb-3">
                        <User className="w-4 h-4 mr-1 flex-shrink-0" />
                        <span className="truncate">
                          {favorite.authors.slice(0, 2).join(', ')}
                          {favorite.authors.length > 2 && ` +${favorite.authors.length - 2}`}
                        </span>
                      </div>
                    )}

                    {/* Date */}
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <Calendar className="w-4 h-4 mr-1" />
                      <span>{formatDate(favorite.publication_date)}</span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </>
      )}

      {/* Modal de confirmación para eliminar */}
      <Modal
        isOpen={deleteConfirmModal.isOpen}
        onClose={() => setDeleteConfirmModal({ isOpen: false, favoriteId: null })}
        title={t('favorites.confirmRemove')}
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            {t('favorites.confirmRemoveText')}
          </p>
          <div className="flex gap-3 justify-end">
            <Button
              variant="ghost"
              onClick={() => setDeleteConfirmModal({ isOpen: false, favoriteId: null })}
            >
              {t('favorites.cancel')}
            </Button>
            <Button
              variant="primary"
              onClick={() => handleRemoveFavorite(deleteConfirmModal.favoriteId)}
              className="bg-red-600 hover:bg-red-700"
            >
              {t('favorites.remove')}
            </Button>
          </div>
        </div>
      </Modal>

      {/* AI Assistant Modal */}
      <AIAssistantModal
        isOpen={isAIAssistantModalOpen}
        onClose={() => setIsAIAssistantModalOpen(false)}
      />
    </div>
  );
};

export default FavoritesPage;
