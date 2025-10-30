# -*- coding: utf-8 -*-
""""
Modelo de búsqueda para la API REST de ClinicCloud.
Este módulo define los modelos de datos utilizados para las consultas de búsqueda
y los resultados devueltos por la API.
"""
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field

class Categoria(BaseModel):
    id: int
    nombre: str

class SearchResult(BaseModel):
    id_documento: int
    titulo: str
    autor: List[str] = []
    fecha_publicacion: Optional[date] = None  # Añadido
    url_fuente: Optional[str] = None
    texto_resumen: Optional[str] = None
    score: float = Field(..., description="Puntuación de similitud con la consulta")
    categoria: Optional[Categoria] = None  # Añadido
    
class SearchQuery(BaseModel):
    query: str = Field(..., description="Consulta en lenguaje natural")
    id_categoria: Optional[int] = Field(None, description="ID de la categoría para filtrar resultados")
    limit: int = Field(25, description="Número máximo de resultados")
    offset: int = Field(0, description="Posición inicial para paginación")
    similarity_threshold: float = Field(0.80, description="Umbral mínimo de similitud (0-1, recomendado: 0.75-0.85 para búsquedas médicas precisas)")

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str
    has_more: bool = Field(False, description="Indica si hay más resultados disponibles")
    filtered_by_similarity: bool = Field(False, description="Indica si se filtraron resultados por similitud")