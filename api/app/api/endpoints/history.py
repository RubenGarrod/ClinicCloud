"""
ENDPOINTS DE HISTORIAL DE BÚSQUEDAS
====================================

Endpoints para gestionar el historial de búsquedas de usuarios.
Permite listar, agregar y eliminar búsquedas del historial.

Comentarios en español para facilitar mantenimiento.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

# Importar utilidades
from app.db.database import execute_query
from app.api.endpoints.auth.dependencies import get_current_user
from app.models.user import UserResponse

router = APIRouter(prefix="/history", tags=["Historial"])


# ============================================
# MODELOS PYDANTIC
# ============================================

class SearchHistoryCreate(BaseModel):
    """Request para crear una entrada en el historial"""
    query: str = Field(..., description="Texto de la búsqueda")
    results_count: int = Field(default=0, description="Número de resultados obtenidos")
    categories: Optional[List[str]] = Field(default=None, description="Categorías filtradas")
    date_from: Optional[str] = Field(default=None, description="Fecha desde (filtro)")
    date_to: Optional[str] = Field(default=None, description="Fecha hasta (filtro)")


class SearchHistoryItem(BaseModel):
    """Respuesta con un item del historial"""
    id: int
    query: str
    results_count: int
    categories: Optional[List[str]]
    date_from: Optional[str]
    date_to: Optional[str]
    created_at: str


class SearchHistoryResponse(BaseModel):
    """Respuesta con lista de historial"""
    total: int
    items: List[SearchHistoryItem]


class MessageResponse(BaseModel):
    """Respuesta genérica con mensaje"""
    message: str


# ============================================
# ENDPOINTS
# ============================================

@router.get("", response_model=SearchHistoryResponse)
async def get_search_history(
    current_user: UserResponse = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Obtiene el historial de búsquedas del usuario actual.

    Args:
        current_user: Usuario autenticado
        limit: Número máximo de resultados (default: 50)
        offset: Offset para paginación (default: 0)

    Returns:
        SearchHistoryResponse con el historial
    """
    # Obtener total de búsquedas
    count_query = """
        SELECT COUNT(*)
        FROM search_history
        WHERE user_id = %s
    """
    total_row = execute_query(count_query, (current_user.id,), fetchone=True)
    total = total_row[0] if total_row else 0

    # Obtener historial con paginación
    query = """
        SELECT
            id,
            query,
            results_count,
            categories,
            date_from,
            date_to,
            created_at
        FROM search_history
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """

    rows = execute_query(query, (current_user.id, limit, offset), fetchall=True)

    items = []
    for row in rows:
        items.append(SearchHistoryItem(
            id=row[0],
            query=row[1],
            results_count=row[2],
            categories=row[3] if row[3] else None,
            date_from=row[4].isoformat() if row[4] else None,
            date_to=row[5].isoformat() if row[5] else None,
            created_at=row[6].isoformat()
        ))

    return SearchHistoryResponse(total=total, items=items)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_search_to_history(
    search: SearchHistoryCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Agrega una nueva búsqueda al historial del usuario.

    Args:
        search: Datos de la búsqueda
        current_user: Usuario autenticado

    Returns:
        MessageResponse confirmando la creación
    """
    query = """
        INSERT INTO search_history (
            user_id,
            query,
            results_count,
            categories,
            date_from,
            date_to
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """

    result = execute_query(
        query,
        (
            current_user.id,
            search.query,
            search.results_count,
            search.categories,
            search.date_from,
            search.date_to
        ),
        fetchone=True,
        commit=True
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al guardar en el historial"
        )

    return MessageResponse(message="Búsqueda agregada al historial")


@router.delete("/{history_id}", response_model=MessageResponse)
async def delete_search_from_history(
    history_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Elimina una búsqueda específica del historial.

    Args:
        history_id: ID de la búsqueda en el historial
        current_user: Usuario autenticado

    Returns:
        MessageResponse confirmando la eliminación
    """
    # Verificar que la búsqueda pertenece al usuario
    check_query = """
        SELECT id FROM search_history
        WHERE id = %s AND user_id = %s
    """

    exists = execute_query(check_query, (history_id, current_user.id), fetchone=True)

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Búsqueda no encontrada"
        )

    # Eliminar la búsqueda
    delete_query = """
        DELETE FROM search_history
        WHERE id = %s AND user_id = %s
    """

    execute_query(delete_query, (history_id, current_user.id), fetchall=False, commit=True)

    return MessageResponse(message="Búsqueda eliminada del historial")


@router.delete("", response_model=MessageResponse)
async def clear_search_history(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Elimina todo el historial de búsquedas del usuario.

    Args:
        current_user: Usuario autenticado

    Returns:
        MessageResponse confirmando la eliminación
    """
    query = """
        DELETE FROM search_history
        WHERE user_id = %s
    """

    execute_query(query, (current_user.id,), fetchall=False, commit=True)

    return MessageResponse(message="Historial limpiado correctamente")
