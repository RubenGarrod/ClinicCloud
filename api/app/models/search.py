"""
MODELOS PARA BÚSQUEDAS Y FAVORITOS
===================================

Modelos Pydantic para historial de búsquedas, documentos favoritos y analytics.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# =====================================================
# MODELOS PARA HISTORIAL DE BÚSQUEDAS
# =====================================================

class SearchHistoryCreate(BaseModel):
    """Modelo para crear una entrada en el historial de búsquedas"""
    query: str = Field(..., description="Texto de la búsqueda")
    results_count: int = Field(default=0, description="Número de resultados obtenidos")
    categories: Optional[List[str]] = Field(default=None, description="Categorías filtradas")
    date_from: Optional[datetime] = Field(default=None, description="Fecha desde (filtro)")
    date_to: Optional[datetime] = Field(default=None, description="Fecha hasta (filtro)")
    session_id: Optional[str] = Field(default=None, description="ID de sesión para usuarios anónimos")


class SearchHistoryResponse(BaseModel):
    """Modelo para respuesta de historial de búsquedas"""
    id: int
    query: str
    results_count: int
    categories: Optional[List[str]]
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    searched_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# =====================================================
# MODELOS PARA DOCUMENTOS FAVORITOS
# =====================================================

class FavoriteDocumentCreate(BaseModel):
    """Modelo para marcar un documento como favorito"""
    document_id: int = Field(..., description="ID del documento")
    document_title: str = Field(..., description="Título del documento")
    document_url: Optional[str] = Field(None, description="URL del documento")
    document_summary: Optional[str] = Field(None, description="Resumen del documento")
    authors: Optional[List[str]] = Field(default=None, description="Lista de autores")
    category: Optional[str] = Field(None, description="Categoría del documento")
    publication_date: Optional[datetime] = Field(None, description="Fecha de publicación")
    notes: Optional[str] = Field(None, description="Notas personales")
    tags: Optional[List[str]] = Field(default=None, description="Tags personales")


class FavoriteDocumentUpdate(BaseModel):
    """Modelo para actualizar un favorito"""
    notes: Optional[str] = Field(None, description="Notas personales")
    tags: Optional[List[str]] = Field(default=None, description="Tags personales")


class FavoriteDocumentResponse(BaseModel):
    """Modelo para respuesta de documento favorito"""
    id: int
    document_id: int
    document_title: str
    document_url: Optional[str]
    document_summary: Optional[str]
    authors: Optional[List[str]]
    category: Optional[str]
    publication_date: Optional[datetime]
    notes: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# =====================================================
# MODELOS PARA ANALYTICS/INTERACCIONES
# =====================================================

class DocumentInteractionCreate(BaseModel):
    """Modelo para registrar una interacción con un documento"""
    document_id: str = Field(..., description="ID del documento")
    interaction_type: str = Field(..., description="Tipo de interacción")
    search_query: Optional[str] = Field(None, description="Query que llevó a este documento")


class DocumentInteractionResponse(BaseModel):
    """Modelo para respuesta de interacción"""
    id: int
    document_id: str
    interaction_type: str
    search_query: Optional[str]
    interacted_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# =====================================================
# MODELOS PARA ESTADÍSTICAS
# =====================================================

class SearchStatsResponse(BaseModel):
    """Estadísticas de búsquedas"""
    total_searches: int
    total_users: int
    avg_results_per_search: float
    top_queries: List[dict]  # [{"query": str, "count": int}, ...]
    top_categories: List[dict]  # [{"category": str, "count": int}, ...]
    searches_by_date: List[dict]  # [{"date": str, "count": int}, ...]


class FavoriteStatsResponse(BaseModel):
    """Estadísticas de favoritos"""
    total_favorites: int
    top_documents: List[dict]  # [{"document_id": str, "title": str, "count": int}, ...]
    favorites_by_category: List[dict]  # [{"category": str, "count": int}, ...]


class UserActivityResponse(BaseModel):
    """Actividad de un usuario"""
    user_id: str
    total_searches: int
    total_favorites: int
    last_search: Optional[datetime]
    last_favorite: Optional[datetime]
    most_searched_categories: List[str]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
