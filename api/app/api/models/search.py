from typing import Optional, List
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    query: str = Field(..., description="Consulta en lenguaje natural")
    id_categoria: Optional[int] = Field(None, description="ID de la categoría para filtrar resultados")
    limit: int = Field(20, description="Número máximo de resultados")
    offset: int = Field(0, description="Posición inicial para paginación")

class SearchResult(BaseModel):
    id_documento: int
    titulo: str
    autor: List[str] = []  # Ahora es una lista de autores
    url_fuente: Optional[str] = None
    texto_resumen: Optional[str] = None
    score: float = Field(..., description="Puntuación de similitud con la consulta")
    
class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str