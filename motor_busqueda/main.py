import logging
import os
import sys


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("search_engine")

# comprobar que todas las dependencias estan disponibles
try:
    import fastapi
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import pydantic
    from pydantic import BaseModel, Field
    import pydantic_settings
    from pydantic_settings import BaseSettings
    
    from app.models.search import SearchQuery, SearchResponse
    from app.config import settings
    from app.search.vector_search import perform_vector_search
    
except ImportError as e:
    logger.error(f"Error importing required dependencies: {str(e)}")
    logger.error("Please install the required packages:")
    logger.error("pip install -U fastapi uvicorn pydantic==2.1.1 pydantic-settings==2.0.3 psycopg2-binary python-dotenv numpy")
    sys.exit(1)

# FastAPI app
app = FastAPI(
    title="ClinicCloud Search Engine",
    description="Motor de búsqueda para documentos médicos usando embeddings vectoriales",
    version="0.1.0"
)

#  CORS
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
        results, total = await perform_vector_search(
            query.query,
            id_categoria=query.id_categoria,
            limit=query.limit,
            offset=query.offset
        )
        
        logger.info(f"Búsqueda completada. Resultados encontrados: {total}")
        
        # Construir la respuesta
        response = SearchResponse(
            results=results,
            total=total,
            query=query.query
        )
        
        return response
    except Exception as e:
        logger.error(f"Error en la búsqueda: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la búsqueda: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)