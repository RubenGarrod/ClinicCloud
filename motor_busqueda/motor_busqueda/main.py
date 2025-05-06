# main.py
import logging
import os
from fastapi import FastAPI, HTTPException
from .search_engine import SearchEngine
from .models import SearchQuery, SearchResult

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('motor_busqueda')

# Configuración de la base de datos
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': os.getenv('DB_NAME', 'cliniccloud'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'admin123')
}

# Log de configuración para depuración
logger.info(f"Configuración de base de datos: host={db_config['host']}, port={db_config['port']}, dbname={db_config['dbname']}")

# Inicializar motor de búsqueda
search_engine = SearchEngine(db_config)

# Crear aplicación FastAPI
app = FastAPI(
    title="Motor de Búsqueda Clinic Cloud",
    description="Motor de búsqueda vectorial para información médica",
    version="0.1.0"
)

@app.post("/search", response_model=SearchResult)
async def search(query: SearchQuery):
    """Endpoint para realizar búsquedas vectoriales"""
    try:
        logger.info(f"Recibida consulta: {query.query}")

        # Realizar búsqueda
        results = search_engine.search(query)
        
        logger.info(f"Búsqueda completada: {len(results)} resultados")
        
        # Construir respuesta
        return SearchResult(
            results=results,
            total=len(results),  
            query=query.query
        )
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servicio"""
    return {"status": "ok"}

@app.get("/config")
async def get_config():
    """Endpoint para verificar la configuración del servicio"""
    # Devuelve información no sensible
    return {
        "database": {
            "host": db_config['host'],
            "port": db_config['port'],
            "dbname": db_config['dbname']
        },
        "engine": {
            "similarity_threshold": 0.2,  # El umbral reducido recomendado
            "vectorizer": "Modelo en uso por TextVectorizer" 
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("motor_busqueda.main:app", host="0.0.0.0", port=8001, reload=True)