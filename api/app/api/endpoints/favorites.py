"""
ENDPOINTS DE DOCUMENTOS FAVORITOS
==================================

API REST para gestión de documentos favoritos de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional, Annotated
from datetime import datetime

from app.models.search import (
    FavoriteDocumentCreate,
    FavoriteDocumentUpdate,
    FavoriteDocumentResponse
)
from app.models.user import UserResponse
from app.api.endpoints.auth.dependencies import get_current_user
from app.db.database import get_db_cursor
from app.core.rate_limiter import get_rate_limiter

router = APIRouter()


@router.post("/", response_model=FavoriteDocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    request: Request,
    favorite: FavoriteDocumentCreate,
    current_user: UserResponse = Depends(get_current_user),
    _rate_limit: Annotated[None, Depends(get_rate_limiter("favorites"))] = None
):
    """
    Marca un documento como favorito para el usuario actual.
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            # Verificar si ya existe
            cursor.execute(
                """
                SELECT id FROM favorites
                WHERE user_id = %s AND document_id = %s
                """,
                (current_user.id, favorite.document_id)
            )
            existing = cursor.fetchone()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Este documento ya está en favoritos"
                )

            # Insertar favorito
            cursor.execute(
                """
                INSERT INTO favorites (
                    user_id, document_id, document_title, document_url, document_summary,
                    authors, category, publication_date, notes, tags
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
                """,
                (
                    current_user.id,
                    favorite.document_id,
                    favorite.document_title,
                    favorite.document_url,
                    favorite.document_summary,
                    favorite.authors,
                    favorite.category,
                    favorite.publication_date,
                    favorite.notes,
                    favorite.tags
                )
            )

            row = cursor.fetchone()

            return FavoriteDocumentResponse(
                id=row[0],
                document_id=favorite.document_id,
                document_title=favorite.document_title,
                document_url=favorite.document_url,
                document_summary=favorite.document_summary,
                authors=favorite.authors,
                category=favorite.category,
                publication_date=favorite.publication_date,
                notes=favorite.notes,
                tags=favorite.tags,
                created_at=row[1]
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al añadir favorito: {str(e)}"
        )


@router.get("/", response_model=List[FavoriteDocumentResponse])
async def get_favorites(
    request: Request,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_user),
    _rate_limit: Annotated[None, Depends(get_rate_limiter("favorites"))] = None
):
    """
    Obtiene la lista de documentos favoritos del usuario actual.
    Permite filtrar por categoría o tag.
    """
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT
                    id, document_id, document_title, document_url, document_summary,
                    authors, category, publication_date, notes, tags,
                    created_at
                FROM favorites
                WHERE user_id = %s
            """
            params = [current_user.id]

            # Filtros opcionales
            if category:
                query += " AND category = %s"
                params.append(category)

            if tag:
                query += " AND %s = ANY(tags)"
                params.append(tag)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                FavoriteDocumentResponse(
                    id=row[0],
                    document_id=row[1],
                    document_title=row[2],
                    document_url=row[3],
                    document_summary=row[4],
                    authors=row[5],
                    category=row[6],
                    publication_date=row[7],
                    notes=row[8],
                    tags=row[9],
                    created_at=row[10]
                )
                for row in rows
            ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener favoritos: {str(e)}"
        )


@router.get("/{favorite_id}", response_model=FavoriteDocumentResponse)
async def get_favorite_by_id(
    favorite_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtiene un favorito específico por ID.
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id, document_id, document_title, document_url, document_summary,
                    authors, category, publication_date, notes, tags,
                    created_at
                FROM favorites
                WHERE id = %s AND user_id = %s
                """,
                (favorite_id, current_user.id)
            )
            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Favorito no encontrado"
                )

            return FavoriteDocumentResponse(
                id=row[0],
                document_id=row[1],
                document_title=row[2],
                document_url=row[3],
                document_summary=row[4],
                authors=row[5],
                category=row[6],
                publication_date=row[7],
                notes=row[8],
                tags=row[9],
                favorited_at=row[10]
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener favorito: {str(e)}"
        )


@router.patch("/{favorite_id}", response_model=FavoriteDocumentResponse)
async def update_favorite(
    favorite_id: int,
    update_data: FavoriteDocumentUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Actualiza las notas o tags de un favorito.
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            # Verificar que existe y pertenece al usuario
            cursor.execute(
                "SELECT id FROM favorites WHERE id = %s AND user_id = %s",
                (favorite_id, current_user.id)
            )

            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Favorito no encontrado"
                )

            # Construir UPDATE dinámico
            set_clauses = []
            params = []

            if update_data.notes is not None:
                set_clauses.append("notes = %s")
                params.append(update_data.notes)

            if update_data.tags is not None:
                set_clauses.append("tags = %s")
                params.append(update_data.tags)

            if not set_clauses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay datos para actualizar"
                )

            params.append(favorite_id)
            params.append(current_user.id)

            query = f"""
                UPDATE favorites
                SET {', '.join(set_clauses)}
                WHERE id = %s AND user_id = %s
                RETURNING
                    id, document_id, document_title, document_url, document_summary,
                    authors, category, publication_date, notes, tags,
                    created_at
            """

            cursor.execute(query, params)
            row = cursor.fetchone()

            return FavoriteDocumentResponse(
                id=row[0],
                document_id=row[1],
                document_title=row[2],
                document_url=row[3],
                document_summary=row[4],
                authors=row[5],
                category=row[6],
                publication_date=row[7],
                notes=row[8],
                tags=row[9],
                favorited_at=row[10]
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar favorito: {str(e)}"
        )


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Elimina un documento de favoritos.
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                DELETE FROM favorites
                WHERE id = %s AND user_id = %s
                RETURNING id
                """,
                (favorite_id, current_user.id)
            )

            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Favorito no encontrado"
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar favorito: {str(e)}"
        )


@router.get("/check/{document_id}", response_model=dict)
async def check_if_favorite(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Verifica si un documento está en favoritos.
    Útil para mostrar/ocultar la estrella en el frontend.
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM favorites
                WHERE user_id = %s AND document_id = %s
                """,
                (current_user.id, document_id)
            )
            row = cursor.fetchone()

            return {
                "is_favorite": row is not None,
                "favorite_id": row[0] if row else None
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar favorito: {str(e)}"
        )
