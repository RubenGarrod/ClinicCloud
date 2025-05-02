import logging
from typing import List, Dict, Any, Optional
from .vectorizer import TextVectorizer
from .db_connector import DatabaseConnector
from .models import SearchQuery, SearchResult, DocumentResult

class SearchEngine:
    """Motor de búsqueda basado en vectores para Clinic Cloud"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """Inicializa el motor de búsqueda"""
        self.logger = logging.getLogger('search_engine')
        self.vectorizer = TextVectorizer()
        self.db_connector = DatabaseConnector(db_config)
        self.logger.info("Motor de búsqueda inicializado")
        
    def search(self, query: SearchQuery) -> List[DocumentResult]:
        """Realiza una búsqueda basada en la consulta proporcionada"""
        try:
            # 1. Vectorizar la consulta
            self.logger.info(f"Procesando consulta: {query.query}")
            query_vector = self.vectorizer.encode(query.query)
            
            # 2. Preparar parámetros adicionales
            category_filter = query.id_categoria
            limit = min(query.limit, 100)  # Limitar a 100 resultados máximo
            offset = query.offset
            
            # 3. Ejecutar búsqueda vectorial en base de datos
            results = self.db_connector.search_documents(
                query_vector=query_vector,
                category_id=category_filter,
                limit=limit,
                offset=offset,
                similarity_threshold=0.5  # Umbral configurable de similitud
            )
            
            # 4. Devolver resultados
            self.logger.info(f"Encontrados {len(results)} resultados para: {query.query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {str(e)}")
            raise