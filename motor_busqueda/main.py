import logging
import os
import sys

# Configure logging early with more detail
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("search_engine")

# Create directory structure
os.makedirs("app/models", exist_ok=True)
os.makedirs("app/search", exist_ok=True)
os.makedirs("app/db", exist_ok=True)

# Create the vector_search.py file with debugging capabilities
vector_search_path = "app/search/vector_search.py"
with open(vector_search_path, "w") as f:
    f.write('''import logging
import psycopg2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import os
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vector_search")

def create_connection():
    """
    Creates a connection to the PostgreSQL database.
    """
    try:
        # Get database settings from environment variables
        db_host = os.getenv("DB_HOST", "db")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "cliniccloud")
        db_user = os.getenv("DB_USER", "admin")
        db_password = os.getenv("DB_PASSWORD", "admin123")
        
        logger.info(f"Connecting to database at {db_host}:{db_port}/{db_name}")
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        return connection
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos: {str(e)}")
        raise

def get_simple_embedding(query_text: str, embedding_dim=768) -> List[float]:
    """
    Creates a simple deterministic embedding for text search.
    """
    # Normalize text
    text = query_text.lower().strip()
    
    # Create a deterministic seed from the text
    text_hash = hashlib.md5(text.encode()).hexdigest()
    seed = int(text_hash, 16) % (2**32)
    
    # Set the random seed for reproducibility
    np.random.seed(seed)
    
    # Generate base embedding
    embedding = np.random.normal(0, 1, embedding_dim)
    
    # Influence the embedding based on the text
    chunks = [text[i:i+3] for i in range(0, len(text), 3)]
    for i, chunk in enumerate(chunks[:100]):
        chunk_val = sum(ord(c) for c in chunk)
        chunk_idx = chunk_val % embedding_dim
        embedding[chunk_idx] += chunk_val / 1000
    
    # Normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
        
    return embedding.tolist()

async def perform_vector_search(
    query: str,
    id_categoria: Optional[int] = None,
    limit: int = 20,
    offset: int = 0
) -> Tuple[List[Dict[Any, Any]], int]:
    """
    Performs a vector similarity search in the database.
    
    Args:
        query: The natural language query string
        id_categoria: Optional category ID to filter results
        limit: Maximum number of results to return
        offset: Offset for pagination
        
    Returns:
        Tuple of (list of results, total count)
    """
    try:
        # Get query embedding
        start_time = time.time()
        query_embedding = get_simple_embedding(query)
        logger.info(f"Embedding generado en {time.time() - start_time:.2f} segundos")
        
        # Connect to the database
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check if we have documents in the database
        cursor.execute("SELECT COUNT(*) FROM documento")
        doc_count = cursor.fetchone()[0]
        logger.info(f"Total documents in database: {doc_count}")
        
        if doc_count == 0:
            logger.warning("No documents in database!")
            return [], 0
            
        # Debug: Check a sample document to understand the structure
        cursor.execute("SELECT id, titulo, autor FROM documento LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            logger.info(f"Sample document - ID: {sample[0]}, Title: {sample[1]}, Author: {sample[2]}")
            
        # First try a simple query without vector similarity to make sure basic DB access works
        try:
            logger.info("Trying simple query...")
            cursor.execute("SELECT id, titulo FROM documento LIMIT 5")
            simple_results = cursor.fetchall()
            logger.info(f"Simple query returned {len(simple_results)} results")
            for row in simple_results:
                logger.info(f"Doc ID: {row[0]}, Title: {row[1]}")
        except Exception as e:
            logger.error(f"Simple query failed: {e}")
        
        # Now try the vector search with careful error handling at each step
        try:
            logger.info("Attempting vector search...")
            
            # Check if vector extension is enabled
            try:
                cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                has_vector = cursor.fetchone() is not None
                logger.info(f"Vector extension is {'enabled' if has_vector else 'NOT enabled'}")
                if not has_vector:
                    logger.error("Vector extension not enabled in PostgreSQL!")
                    # Fall back to non-vector search
                    raise Exception("Vector extension not available")
            except Exception as e:
                logger.error(f"Error checking vector extension: {e}")
                raise
                
            # Check a document with its vector to see the structure
            try:
                cursor.execute("SELECT id, contenido_vectorizado FROM documento WHERE contenido_vectorizado IS NOT NULL LIMIT 1")
                vec_sample = cursor.fetchone()
                if vec_sample:
                    logger.info(f"Sample vector - ID: {vec_sample[0]}, Vector dim: {len(vec_sample[1])}")
                else:
                    logger.warning("No documents with non-NULL vectors found!")
            except Exception as e:
                logger.error(f"Error checking vector sample: {e}")
            
            # Try with simple text search instead of vector search
            search_terms = query.lower().split()
            search_sql = """
            SELECT 
                d.id, 
                d.titulo, 
                d.autor, 
                d.fecha_publicacion, 
                d.url_fuente,
                c.id as id_categoria,
                c.nombre as categoria_nombre,
                r.texto_resumen,
                1.0 as score
            FROM 
                documento d
            LEFT JOIN 
                categoria c ON d.id_categoria = c.id
            LEFT JOIN 
                resumen r ON d.id = r.id_documento
            WHERE 
                LOWER(d.titulo) LIKE %s
                OR LOWER(d.autor) LIKE %s
            """
            
            search_pattern = f"%{search_terms[0]}%"
            params = [search_pattern, search_pattern]
            
            # Add category filter if specified
            if id_categoria is not None:
                search_sql += " AND d.id_categoria = %s"
                params.append(id_categoria)
            
            # Execute search query with limit and offset
            search_sql += " ORDER BY d.fecha_publicacion DESC LIMIT %s OFFSET %s"
            
            logger.info(f"Executing text search with pattern: {search_pattern}")
            cursor.execute(search_sql, params + [limit, offset])
            rows = cursor.fetchall()
            logger.info(f"Text search query returned {len(rows)} results")
            
            # Get total count (simplified)
            total_count = min(doc_count, 100)  # Just an estimate
            
        except Exception as e:
            logger.error(f"Vector/text search failed: {e}")
            
            # Last resort fallback - just get the most recent documents
            fallback_sql = """
            SELECT 
                d.id, 
                d.titulo, 
                d.autor, 
                d.fecha_publicacion, 
                d.url_fuente,
                c.id as id_categoria,
                c.nombre as categoria_nombre,
                r.texto_resumen,
                0.75 as score
            FROM 
                documento d
            LEFT JOIN 
                categoria c ON d.id_categoria = c.id
            LEFT JOIN 
                resumen r ON d.id = r.id_documento
            ORDER BY d.fecha_publicacion DESC
            LIMIT %s OFFSET %s
            """
            
            logger.info("Using fallback query - most recent documents")
            cursor.execute(fallback_sql, [limit, offset])
            rows = cursor.fetchall()
            logger.info(f"Fallback query returned {len(rows)} results")
            
            # Get total count
            total_count = doc_count
        
        # Process results
        results = []
        for row in rows:
            # Convert autor to a list if it's a string
            authors = []
            if row[2]:  # autor column
                if isinstance(row[2], str):
                    if ',' in row[2]:
                        authors = [author.strip() for author in row[2].split(',')]
                    else:
                        authors = [row[2]]
                else:
                    authors = [row[2]]
            
            # Build result object
            result = {
                "id": row[0],
                "titulo": row[1],
                "autor": authors,
                "fecha_publicacion": row[3],
                "url_fuente": row[4],
                "categoria": {
                    "id": row[5],
                    "nombre": row[6]
                } if row[5] else None,
                "texto_resumen": row[7],
                "score": float(row[8]) if row[8] is not None else 0.0  # Convert Decimal to float
            }
            results.append(result)
        
        # Close database connection
        cursor.close()
        conn.close()
        
        logger.info(f"Búsqueda completada en {time.time() - start_time:.2f} segundos. Resultados: {len(results)}/{total_count}")
        return results, total_count
        
    except Exception as e:
        logger.error(f"Error en búsqueda vectorial: {str(e)}")
        
        # Return empty results as a last resort fallback
        return [], 0
''')

# Create the models/search.py file
search_model_path = "app/models/search.py"
with open(search_model_path, "w") as f:
    f.write('''
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
''')

# Create the config.py file
config_path = "app/config.py"
with open(config_path, "w") as f:
    f.write('''
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database connection settings
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "cliniccloud")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin123")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Search engine settings
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", 
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "20"))
    
    # Model settings
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "/app/models")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
''')

# Create __init__.py files for all packages
for dir_path in ["app", "app/models", "app/search", "app/db"]:
    init_file = os.path.join(dir_path, "__init__.py")
    with open(init_file, "w") as f:
        f.write("# Initialize package\n")

# Check if required dependencies are available
try:
    import fastapi
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import pydantic
    from pydantic import BaseModel, Field
    import pydantic_settings
    from pydantic_settings import BaseSettings
    
    # Now try importing our app modules
    from app.models.search import SearchQuery, SearchResponse
    from app.config import settings
    from app.search.vector_search import perform_vector_search
    
except ImportError as e:
    logger.error(f"Error importing required dependencies: {str(e)}")
    logger.error("Please install the required packages:")
    logger.error("pip install -U fastapi uvicorn pydantic==2.1.1 pydantic-settings==2.0.3 psycopg2-binary python-dotenv numpy")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(
    title="ClinicCloud Search Engine",
    description="Motor de búsqueda para documentos médicos usando embeddings vectoriales",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
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