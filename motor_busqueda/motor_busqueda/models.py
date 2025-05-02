from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class SearchQuery(BaseModel):
    """Modelo para la consulta de búsqueda"""
    query: str = Field(..., description="Consulta en lenguaje natural")
    id_categoria: Optional[int] = Field(None, description="ID de categoría para filtrar")
    limit: int = Field(20, description="Número máximo de resultados")
    offset: int = Field(0, description="Desplazamiento para paginación")

class DocumentResult(BaseModel):
    """Modelo para un documento resultado de búsqueda"""
    id: int
    titulo: str
    autor: List[str] = []
    fecha_publicacion: Optional[date] = None
    url_fuente: Optional[str] = None
    texto_resumen: Optional[str] = None
    categoria: Optional[Dict[str, Any]] = None
    score: float = Field(..., description="Puntuación de similitud")

class SearchResult(BaseModel):
    """Modelo para el resultado completo de una búsqueda"""
    results: List[DocumentResult]
    total: int
    query: str