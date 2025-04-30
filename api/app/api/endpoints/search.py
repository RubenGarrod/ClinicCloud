from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.models.search import SearchQuery, SearchResponse, SearchResult
from app.db.database import execute_query
from app.config import SIMILARITY_THRESHOLD, MAX_SEARCH_RESULTS

# Este endpoint está preparado para interactuar con el motor de búsqueda
# La implementación actual es básica y deberá conectarse con el microservicio
# del motor de búsqueda cuando este sea implementado

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search_documents(query: SearchQuery):
    """
    Endpoint para buscar documentos usando procesamiento de lenguaje natural.
    
    Por ahora, realiza una búsqueda simple en la base de datos utilizando una
    comparación de texto. Cuando el motor de búsqueda esté completamente 
    implementado, este endpoint delegará la búsqueda a dicho microservicio.
    """
    try:
        # Búsqueda básica utilizando LIKE para simular la función del motor de búsqueda
        # Esta parte será reemplazada cuando se integre el microservicio de búsqueda
        search_term = f"%{query.query}%"
        
        sql = """
        SELECT d.id, d.titulo, d.autor, d.url_fuente, r.texto_resumen, 0.8 as score
        FROM documento d
        JOIN resumen r ON d.id = r.id_documento
        WHERE d.titulo ILIKE %s OR r.texto_resumen ILIKE %s
        """
        
        params = [search_term, search_term]
        
        # Añadir filtro por categoría si se especificó
        if query.id_categoria:
            sql += " AND d.id_categoria = %s"
            params.append(query.id_categoria)
        
        sql += f" LIMIT {min(query.limit, MAX_SEARCH_RESULTS)} OFFSET {query.offset}"
        
        results = execute_query(sql, params)
        
        # Obtener el total de resultados para paginación
        count_sql = """
        SELECT COUNT(*)
        FROM documento d
        JOIN resumen r ON d.id = r.id_documento
        WHERE d.titulo ILIKE %s OR r.texto_resumen ILIKE %s
        """
        count_params = [search_term, search_term]
        
        if query.id_categoria:
            count_sql += " AND d.id_categoria = %s"
            count_params.append(query.id_categoria)
            
        total_count = execute_query(count_sql, count_params, fetchone=True)[0]
        
        # Formatear resultados
        search_results = []
        for row in results:
            # Manejo consistente del campo autor como lista
            autor = []
            if row[2]:
                autor = [row[2]]

            search_results.append(
                SearchResult(
                    id_documento=row[0],
                    titulo=row[1],
                    autor=autor,  # Lista de autores
                    url_fuente=row[3],
                    texto_resumen=row[4],
                    score=row[5]
                )
            )
        
        return SearchResponse(
            results=search_results,
            total=total_count,
            query=query.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la búsqueda: {str(e)}")