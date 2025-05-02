from fastapi import APIRouter, HTTPException
import httpx
from typing import List
import os

from app.api.models.search import SearchQuery, SearchResponse, SearchResult

router = APIRouter()

# URL del microservicio del motor de búsqueda
SEARCH_ENGINE_URL = os.getenv("SEARCH_ENGINE_URL", "http://motor_busqueda:8001")

@router.post("/", response_model=SearchResponse)
async def search_documents(query: SearchQuery):
    """
    Endpoint para buscar documentos usando procesamiento de lenguaje natural.
    Este endpoint delega la búsqueda al microservicio del motor de búsqueda.
    """
    try:
        # Llamar al microservicio del motor de búsqueda
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SEARCH_ENGINE_URL}/search",
                json=query.dict()
            )
            
            # Verificar respuesta
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error del motor de búsqueda: {response.text}"
                )
            
            # Procesar resultados
            search_results = response.json()
            
            # Transformar resultados al formato esperado por la API
            results = []
            for item in search_results.get("results", []):
                results.append(
                    SearchResult(
                        id_documento=item["id"],
                        titulo=item["titulo"],
                        autor=item["autor"],
                        url_fuente=item["url_fuente"],
                        texto_resumen=item["texto_resumen"],
                        score=item["score"]
                    )
                )
            
            return SearchResponse(
                results=results,
                total=search_results.get("total", 0),
                query=query.query
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Error de comunicación con el motor de búsqueda: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en la búsqueda: {str(e)}"
        )