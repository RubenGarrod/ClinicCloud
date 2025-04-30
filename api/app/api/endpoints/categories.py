from fastapi import APIRouter, HTTPException
from typing import List

from app.api.models.document import Categoria
from app.db.database import execute_query

router = APIRouter()

@router.get("/", response_model=List[Categoria])
async def list_categories():
    """
    Recupera la lista de todas las categorías disponibles.
    """
    try:
        sql = "SELECT id, nombre FROM categoria ORDER BY nombre"
        results = execute_query(sql)
        
        categories = []
        for row in results:
            categories.append({
                "id": row[0],
                "nombre": row[1]
            })
        
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar categorías: {str(e)}")

@router.get("/{id_categoria}", response_model=Categoria)
async def get_category(id_categoria: int):
    """
    Recupera una categoría específica por su ID.
    """
    try:
        sql = "SELECT id, nombre FROM categoria WHERE id = %s"
        result = execute_query(sql, [id_categoria], fetchone=True)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Categoría con ID {id_categoria} no encontrada")
        
        category = {
            "id": result[0],
            "nombre": result[1]
        }
        
        return category
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al recuperar la categoría: {str(e)}")