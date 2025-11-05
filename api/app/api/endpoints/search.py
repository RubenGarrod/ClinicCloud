# -*- coding: utf-8 -*-
"""
Endpoint principal para la búsqueda de documentos en la API REST de ClinicCloud.
Este endpoint utiliza el microservicio de búsqueda para realizar consultas
con procesamiento de lenguaje natural.
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends
import httpx
from typing import List, Annotated
import os
import logging

from app.api.models.search import SearchQuery, SearchResponse, SearchResult
from app.core.rate_limiter import get_rate_limiter

router = APIRouter()
logger = logging.getLogger("search_router")

# URL del microservicio del motor de búsqueda
SEARCH_ENGINE_URL = os.getenv("SEARCH_ENGINE_URL", "http://localhost:8001")

logger.info(f"Configurado motor de búsqueda en: {SEARCH_ENGINE_URL}")

@router.post("/",
             response_model=SearchResponse,
             dependencies=[Depends(get_rate_limiter("search_authenticated"))])
async def search_documents(
    request: Request,
    query: SearchQuery
):
    """
    Endpoint para buscar documentos usando procesamiento de lenguaje natural.
    Este endpoint delega la búsqueda al microservicio del motor de búsqueda.
    """
    try:
        # Registrar información de la solicitud
        logger.info(f"Enviando consulta al motor de búsqueda: {query.query}")
        logger.info(f"URL del motor de búsqueda: {SEARCH_ENGINE_URL}")
        
        # Llamar al microservicio del motor de búsqueda con timeout y manejo de errores
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{SEARCH_ENGINE_URL}/search",
                    json=query.dict()
                )
                
                # Verificar respuesta
                if response.status_code != 200:
                    logger.error(f"Error del motor de búsqueda: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error del motor de búsqueda: {response.text}"
                    )
                
                # Procesar resultados
                search_results = response.json()
                logger.info(f"Recibidos {len(search_results.get('results', []))} resultados")
                
                # Transformar resultados al formato esperado por la API
                results = []
                for item in search_results.get("results", []):
                    try:
                        results.append(
                            SearchResult(
                                id_documento=item["id"],
                                titulo=item["titulo"],
                                autor=item["autor"] if "autor" in item else [],
                                url_fuente=item.get("url_fuente"),
                                texto_resumen=item.get("texto_resumen"),
                                fecha_publicacion=item.get("fecha_publicacion"),  # Añadido
                                categoria=item.get("categoria"),  # Añadido
                                score=item["score"]
                            )
                        )
                    except KeyError as e:
                        logger.error(f"Error al procesar resultado: {str(e)}, item: {item}")
                
                return SearchResponse(
                    results=results,
                    total=search_results.get("total", 0),
                    query=query.query,
                    has_more=search_results.get("has_more", False),
                    filtered_by_similarity=search_results.get("filtered_by_similarity", False)
                )
                
            except httpx.RequestError as e:
                logger.error(f"Error de comunicación con el motor de búsqueda: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                    detail=f"Error de comunicación con el motor de búsqueda: {str(e)}"
                )
    except Exception as e:
        logger.exception(f"Error inesperado en la búsqueda: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la búsqueda: {str(e)}"
        )