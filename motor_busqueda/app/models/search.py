
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

class Categoria(BaseModel):
    id: int
    nombre: str

class SearchResult(BaseModel):
    id: int
    titulo: str
    autor: List[str] = []
    fecha_publicacion: Optional[date] = None
    url_fuente: Optional[str] = None
    texto_resumen: Optional[str] = None
    score: float = Field(..., description="Puntuación de similitud con la consulta")
    categoria: Optional[Categoria] = None

class SearchQuery(BaseModel):
    query: str = Field(..., description="Consulta en lenguaje natural")
    id_categoria: Optional[int] = Field(None, description="ID de la categoría para filtrar resultados")
    limit: int = Field(20, description="Número máximo de resultados")
    offset: int = Field(0, description="Posición inicial para paginación")

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str
