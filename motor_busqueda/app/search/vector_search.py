import logging
import psycopg2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import os
import hashlib
import time

# logging oara debugg
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vector_search")

def create_connection():
    """
    Genera la conexión con la base de datos PostgreSQL
    """
    try:
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
    Genera un embedding a partir de una cadena de texto
    """
    # normalizamos la cadena
    text = query_text.lower().strip()
    
    # Se genera una semilla a partir del hash de la cadena
    # Esto asegura que el embedding sea reproducible
    # y que no dependa de la longitud del texto
    text_hash = hashlib.md5(text.encode()).hexdigest()
    seed = int(text_hash, 16) % (2**32)

    np.random.seed(seed)
    
    # generamos un embedding aleatorio
    embedding = np.random.normal(0, 1, embedding_dim)
    
    # e influenciamos el embedding con la cadena de texto
    chunks = [text[i:i+3] for i in range(0, len(text), 3)]
    for i, chunk in enumerate(chunks[:100]):
        chunk_val = sum(ord(c) for c in chunk)
        chunk_idx = chunk_val % embedding_dim
        embedding[chunk_idx] += chunk_val / 1000
    
    # volvemos a normalizar
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
    """  Realiza una búsqueda por similitud vectorial en la base de datos. """
    try:
        start_time = time.time()
        # obtenemos el embedding de la query
        query_embedding = get_simple_embedding(query)
        logger.info(f"Embedding generado en {time.time() - start_time:.2f} segundos")
        
        # creamos la conexion 
        conn = create_connection()
        cursor = conn.cursor()
        
        # se comprueba que haya documentos en la database
        cursor.execute("SELECT COUNT(*) FROM documento")
        doc_count = cursor.fetchone()[0]
        logger.info(f"Total documents in database: {doc_count}")
        
        if doc_count == 0:
            logger.warning("No documents in database!")
            return [], 0
            
        # Debugging: muestra un documento de ejemplo
        cursor.execute("SELECT id, titulo, autor FROM documento LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            logger.info(f"Sample document - ID: {sample[0]}, Title: {sample[1]}, Author: {sample[2]}")
            
        # Primero, se intenta una consulta simple para verificar la conexión y la estructura de la base de datos
        # Esto es útil para depurar problemas de conexión o estructura de la base de datos
        try:
            logger.info("Trying simple query...")
            cursor.execute("SELECT id, titulo FROM documento LIMIT 5")
            simple_results = cursor.fetchall()
            logger.info(f"Simple query returned {len(simple_results)} results")
            for row in simple_results:
                logger.info(f"Doc ID: {row[0]}, Title: {row[1]}")
        except Exception as e:
            logger.error(f"Simple query failed: {e}")
        
        try:
            logger.info("Attempting vector search...")
            
            # Verificamos si la extensión de vector está habilitada
            cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            has_vector = cursor.fetchone() is not None
            logger.info(f"Vector extension is {'enabled' if has_vector else 'NOT enabled'}")
            
            # Verificamos que tengamos documentos con vectores
            cursor.execute("SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL")
            vectorized_count = cursor.fetchone()[0]
            logger.info(f"Documents with vectors: {vectorized_count}")
            
            if has_vector and vectorized_count > 0:
                # Si tenemos la extensión y documentos vectorizados, procedemos con la búsqueda
                logger.info("Executing vector search with embedding...")
                
                # SQL para búsqueda vectorial usando el operador de distancia coseno (<->)
                # Ordenamos por similitud (1 - distancia) para que los más similares aparezcan primero
                vector_sql = """
                SELECT 
                    d.id, 
                    d.titulo, 
                    d.autor, 
                    d.fecha_publicacion, 
                    d.url_fuente,
                    c.id as id_categoria,
                    c.nombre as categoria_nombre,
                    r.texto_resumen,
                    1 - (d.contenido_vectorizado <-> %s::vector) as score
                FROM 
                    documento d
                LEFT JOIN 
                    categoria c ON d.id_categoria = c.id
                LEFT JOIN 
                    resumen r ON d.id = r.id_documento
                WHERE 
                    d.contenido_vectorizado IS NOT NULL
                """
                
                # Parámetros para la consulta
                params = [query_embedding]
                
                # Añadir filtro de categoría si es necesario
                if id_categoria is not None:
                    vector_sql += " AND d.id_categoria = %s"
                    params.append(id_categoria)
                
                # Ordenar por score y aplicar límite y offset
                vector_sql += " ORDER BY score DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                try:
                    # Ejecutamos la consulta vectorial
                    logger.info(f"Executing vector query with {len(query_embedding)}-dimensional embedding")
                    cursor.execute(vector_sql, params)
                    rows = cursor.fetchall()
                    logger.info(f"Vector search returned {len(rows)} results")
                    
                    # Si tenemos resultados, calculamos el total aproximado
                    if rows:
                        # Consulta para estimar el total sin límite
                        if id_categoria is not None:
                            cursor.execute(
                                "SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL AND id_categoria = %s", 
                                [id_categoria]
                            )
                        else:
                            cursor.execute("SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL")
                        total_count = cursor.fetchone()[0]
                        logger.info(f"Estimated total matches: {total_count}")
                    else:
                        total_count = 0
                    
                    # Si la búsqueda vectorial no devuelve resultados, intentamos búsqueda de texto
                    if not rows:
                        logger.info("Vector search returned no results, falling back to text search...")
                        raise Exception("No vector search results")
                        
                except Exception as e:
                    logger.error(f"Vector search failed: {str(e)}")
                    raise  # Re-lanzamos la excepción para caer en la búsqueda de texto
            else:
                logger.warning("Vector search not possible: extension or vectorized documents missing")
                raise Exception("Vector search not possible")
                
        except Exception as e:
            logger.error(f"Vector search failed, falling back to text search: {str(e)}")
            
            # Búsqueda de texto como fallback
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
            
            # si se especifica una categoria se aplica como filtro
            if id_categoria is not None:
                search_sql += " AND d.id_categoria = %s"
                params.append(id_categoria)
            
            # se ejecuta la consulta
            search_sql += " ORDER BY d.fecha_publicacion DESC LIMIT %s OFFSET %s"
            
            logger.info(f"Executing text search with pattern: {search_pattern}")
            cursor.execute(search_sql, params + [limit, offset])
            rows = cursor.fetchall()
            logger.info(f"Text search query returned {len(rows)} results")
            
            # Si la búsqueda de texto también falla, usamos el último recurso
            if not rows:
                logger.info("Text search returned no results, using last resort fallback...")
                
                # Last resort fallback - simplemente devuelve los documentos más recientes
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
                """
                
                if id_categoria is not None:
                    fallback_sql += " WHERE d.id_categoria = %s"
                    cursor.execute(fallback_sql + " ORDER BY d.fecha_publicacion DESC LIMIT %s OFFSET %s", 
                                 [id_categoria, limit, offset])
                else:
                    cursor.execute(fallback_sql + " ORDER BY d.fecha_publicacion DESC LIMIT %s OFFSET %s",
                                 [limit, offset])
                
                rows = cursor.fetchall()
                logger.info(f"Fallback query returned {len(rows)} results")
            
            total_count = doc_count  # Estimación aproximada
        
        # Procesamos los resultados
        results = []
        for row in rows:
            # se convierte el autor a lista ya que suelen ser varios
            authors = []
            if row[2]:  
                if isinstance(row[2], str):
                    if ',' in row[2]:
                        authors = [author.strip() for author in row[2].split(',')]
                    else:
                        authors = [row[2]]
                else:
                    authors = [row[2]]
            
            # y se genera el diccionario de respuesta (JSON)
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
                "score": float(row[8]) if row[8] is not None else 0.0 
            }
            results.append(result)
        
        # cerramos conexion
        cursor.close()
        conn.close()
        
        logger.info(f"Búsqueda completada en {time.time() - start_time:.2f} segundos. Resultados: {len(results)}/{total_count}")
        return results, total_count
        
    except Exception as e:
        logger.error(f"Error en búsqueda vectorial: {str(e)}")
        
        # Se devuelve vacío como último fallback
        return [], 0