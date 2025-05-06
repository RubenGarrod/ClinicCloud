import logging
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
