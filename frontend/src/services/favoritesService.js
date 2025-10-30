/**
 * SERVICIO DE FAVORITOS
 * ====================
 * Gestión de documentos favoritos del usuario
 *
 * Copyright (C) 2025 Rubén García Rodríguez
 * Licensed under GPL-3.0
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Obtiene el token de autenticación del localStorage
 */
const getAuthToken = () => {
  return localStorage.getItem('auth_token');
};

/**
 * Obtiene headers con autenticación
 */
const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

/**
 * Añade un documento a favoritos
 * @param {Object} documentData - Datos del documento a guardar
 * @returns {Promise<Object>} - Documento favorito creado
 */
export const addFavorite = async (documentData) => {
  // Preparar los datos para enviar al backend
  // El backend espera Optional[List[str]] para authors y tags, por lo que null es válido
  // Pero vamos a enviar arrays vacíos si no hay datos

  // Convertir la fecha a formato ISO datetime si existe
  // El backend espera datetime, no solo date
  let publicationDate = null;
  if (documentData.fecha_publicacion) {
    // Si es solo una fecha (YYYY-MM-DD), añadir la hora
    const dateStr = documentData.fecha_publicacion;
    if (dateStr.length === 10) {
      // Formato: YYYY-MM-DD -> YYYY-MM-DDT00:00:00
      publicationDate = `${dateStr}T00:00:00`;
    } else {
      publicationDate = dateStr;
    }
  }

  const payload = {
    document_id: String(documentData.id_documento), // Convertir a string
    document_title: documentData.titulo,
    document_url: documentData.url_fuente || null,
    document_summary: documentData.texto_resumen || null,
    authors: Array.isArray(documentData.autor) && documentData.autor.length > 0 ? documentData.autor : [],
    category: documentData.categoria?.nombre || null,
    publication_date: publicationDate,
    notes: null,
    tags: []
  };

  const response = await fetch(`${API_URL}/api/favorites/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error al añadir favorito' }));
    throw new Error(error.detail || 'Error al añadir favorito');
  }

  return response.json();
};

/**
 * Obtiene todos los favoritos del usuario
 * @param {Object} filters - Filtros opcionales (category, tag, limit, offset)
 * @returns {Promise<Array>} - Lista de favoritos
 */
export const getFavorites = async (filters = {}) => {
  const params = new URLSearchParams();

  if (filters.category) params.append('category', filters.category);
  if (filters.tag) params.append('tag', filters.tag);
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.offset) params.append('offset', filters.offset.toString());

  const response = await fetch(`${API_URL}/api/favorites/?${params.toString()}`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al obtener favoritos');
  }

  return response.json();
};

/**
 * Obtiene un favorito específico por ID
 * @param {number} favoriteId - ID del favorito
 * @returns {Promise<Object>} - Favorito
 */
export const getFavoriteById = async (favoriteId) => {
  const response = await fetch(`${API_URL}/api/favorites/${favoriteId}`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al obtener favorito');
  }

  return response.json();
};

/**
 * Verifica si un documento está en favoritos
 * @param {string} documentId - ID del documento
 * @returns {Promise<Object>} - {is_favorite: boolean, favorite_id: number|null}
 */
export const checkIfFavorite = async (documentId) => {
  const response = await fetch(`${API_URL}/api/favorites/check/${documentId}`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al verificar favorito');
  }

  return response.json();
};

/**
 * Actualiza notas o tags de un favorito
 * @param {number} favoriteId - ID del favorito
 * @param {Object} updates - {notes?: string, tags?: string[]}
 * @returns {Promise<Object>} - Favorito actualizado
 */
export const updateFavorite = async (favoriteId, updates) => {
  const response = await fetch(`${API_URL}/api/favorites/${favoriteId}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify(updates)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al actualizar favorito');
  }

  return response.json();
};

/**
 * Elimina un documento de favoritos
 * @param {number} favoriteId - ID del favorito a eliminar
 * @returns {Promise<void>}
 */
export const removeFavorite = async (favoriteId) => {
  const response = await fetch(`${API_URL}/api/favorites/${favoriteId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al eliminar favorito');
  }
};

/**
 * Verifica el estado de múltiples documentos (optimización)
 * @param {string[]} documentIds - Array de IDs de documentos
 * @returns {Promise<Object>} - Mapa de {documentId: {is_favorite, favorite_id}}
 */
export const checkMultipleFavorites = async (documentIds) => {
  // Hacer requests en paralelo para cada documento
  const checks = await Promise.all(
    documentIds.map(id =>
      checkIfFavorite(id).catch(() => ({ is_favorite: false, favorite_id: null }))
    )
  );

  // Construir objeto de respuesta
  const result = {};
  documentIds.forEach((id, index) => {
    result[id] = checks[index];
  });

  return result;
};

const favoritesService = {
  addFavorite,
  getFavorites,
  getFavoriteById,
  checkIfFavorite,
  updateFavorite,
  removeFavorite,
  checkMultipleFavorites
};

export default favoritesService;
