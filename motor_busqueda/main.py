# -*- coding: utf-8 -*-
"""
ClinicCloud Search Engine - Main Application Entry Point

Copyright (C) 2025 Rubén García Rodríguez

This file is part of ClinicCloud.

ClinicCloud is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ClinicCloud is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("search_engine")

# Lista de paquetes requeridos
required_packages = [
    "fastapi", "uvicorn", "pydantic==2.1.1", "pydantic-settings==2.0.3", 
    "psycopg2-binary", "python-dotenv", "numpy"
]

# Comprobar que todas las dependencias estén disponibles
try:
    # Importar los módulos principales
    import fastapi
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    
    import pydantic
    from pydantic import BaseModel, Field
    
    # Verificar que pydantic_settings esté disponible
    try:
        import pydantic_settings
        from pydantic_settings import BaseSettings
    except ImportError:
        logger.error("Error importing pydantic_settings. Installing...")
        os.system("pip install pydantic-settings==2.0.3")
        import pydantic_settings
        from pydantic_settings import BaseSettings
    
    # Intentar importar las dependencias de la aplicación
    try:
        from app.models.search import SearchQuery, SearchResponse
        from app.config import settings
        from app.search.vector_search import perform_vector_search
    except ImportError as e:
        logger.error(f"Error importing app modules: {str(e)}")
        logger.error("Check if the PYTHONPATH is set correctly")
        logger.error(f"Current PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
        
        # Intenta solucionar el problema automáticamente
        logger.info("Attempting to fix by setting PYTHONPATH...")
        os.environ["PYTHONPATH"] = "/app"
        
        try:
            # Intentar importar de nuevo
            from app.models.search import SearchQuery, SearchResponse
            from app.config import settings
            from app.search.vector_search import perform_vector_search
            logger.info("Successfully imported app modules after PYTHONPATH fix")
        except ImportError as e:
            # Si todavía no funciona, mostrar mensaje de error y salir
            logger.error(f"Still unable to import app modules: {str(e)}")
            logger.error("Please check your directory structure and module paths")
            sys.exit(1)
    
except ImportError as e:
    logger.error(f"Error importing required dependencies: {str(e)}")
    logger.error("Please install the required packages:")
    logger.error("pip install -U " + " ".join(required_packages))
    sys.exit(1)

# FastAPI app
app = FastAPI(
    title="ClinicCloud Search Engine",
    description="Motor de búsqueda para documentos médicos usando embeddings vectoriales",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "ClinicCloud Search Engine API", "status": "running"}

@app.post("/search", response_model=SearchResponse)
async def search_documents(query: SearchQuery):
    """
    Endpoint para buscar documentos utilizando similitud vectorial.
    """
    try:
        logger.info(f"Búsqueda recibida: {query.query}")
        
        # Realizar la búsqueda vectorial
        results, total, has_more, filtered_by_similarity = await perform_vector_search(
            query.query,
            id_categoria=query.id_categoria,
            limit=query.limit,
            offset=query.offset,
            similarity_threshold=query.similarity_threshold
        )

        logger.info(f"Búsqueda completada. Resultados encontrados: {total}, has_more: {has_more}, filtered: {filtered_by_similarity}")

        # Construir la respuesta
        response = SearchResponse(
            results=results,
            total=total,
            query=query.query,
            has_more=has_more,
            filtered_by_similarity=filtered_by_similarity
        )

        return response
    except Exception as e:
        logger.error(f"Error en la búsqueda: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la búsqueda: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)