# -*- coding: utf-8 -*-
"""
Módulo para realizar búsquedas vectoriales en una base de datos PostgreSQL
utilizando embeddings generados por SentenceTransformer.
"""
import logging
import psycopg2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import os
import hashlib
import time
from sentence_transformers import SentenceTransformer

# Configuración de logging para depuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vector_search")

# ============================================================================
# CONFIGURACIÓN DEL MODELO DE EMBEDDINGS
# ============================================================================
# Usamos un modelo especializado en textos médicos para mejorar la calidad
# de las búsquedas en documentos científicos de salud.
#
# MODELO: pritamdeka/S-PubMedBert-MS-MARCO
# - BioBERT fine-tuned en MS-MARCO para semantic search
# - Optimizado específicamente para similitud semántica en textos médicos
# - Dimensión nativa: 768 (NO requiere padding)
# - Genera embeddings más discriminativos que el modelo base
#
# IMPORTANTE: Este modelo DEBE ser el mismo que se usa en el scraper
# para garantizar que las búsquedas funcionen correctamente.
# ============================================================================

# Variable global para almacenar el modelo (patrón singleton)
# Esto evita cargar el modelo múltiples veces en memoria, lo cual sería
# costoso en términos de RAM y tiempo de inicialización
_model = None

def get_model():
    """
    Retorna una instancia única del modelo SentenceTransformer médico.

    Implementa el patrón Singleton para cargar el modelo una sola vez
    y reutilizarlo en todas las búsquedas posteriores.

    Returns:
        SentenceTransformer: Instancia del modelo BiomedNLP-PubMedBERT
        None: Si hubo error al cargar el modelo

    Nota:
        El modelo se descarga automáticamente la primera vez desde HuggingFace.
        Ocupa aproximadamente 420MB y se cachea localmente.
    """
    global _model
    if _model is None:
        try:
            logger.info("Cargando modelo S-PubMedBert-MS-MARCO para semantic search...")
            logger.info("Esto puede tardar unos minutos la primera vez (descarga del modelo)")

            # Cargar el modelo especializado en semantic search médico
            _model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

            logger.info("✓ Modelo S-PubMedBert-MS-MARCO cargado correctamente")
            logger.info("  - Dimensión: 768 (nativa, sin padding)")
            logger.info("  - Especialización: Semantic search en textos médicos")

        except Exception as e:
            logger.error(f"✗ Error al cargar modelo BiomedNLP-PubMedBERT: {e}")
            logger.error("Las búsquedas usarán embeddings de fallback (baja calidad)")
            _model = None

    return _model

def create_connection():
    """
    Genera la conexión con la base de datos PostgreSQL
    """
    try:
        db_host = os.getenv("DB_HOST", "db")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "cliniccloud")
        db_user = os.getenv("DB_USER", "cliniccloud")
        db_password = os.getenv("DB_PASSWORD", "changeme")
        
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
    Usado como fallback si SentenceTransformer falla.
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


def get_transformer_embedding(query_text: str) -> List[float]:
    """
    Genera un embedding para la query usando BiomedNLP-PubMedBERT.

    Este modelo médico especializado convierte texto en un vector de 768 dimensiones
    que captura el significado semántico de la query en el contexto médico.

    El proceso es:
    1. Tokeniza el texto usando el tokenizador del modelo (comprende terminología médica)
    2. Pasa los tokens por el transformer (BERT entrenado en PubMed)
    3. Genera un vector de 768 dimensiones que representa el significado

    Args:
        query_text (str): Texto de búsqueda del usuario (puede ser keywords o lenguaje natural)

    Returns:
        List[float]: Vector de 768 dimensiones representando el significado de la query

    Ejemplos:
        >>> get_transformer_embedding("diabetes treatment")
        [0.23, -0.15, 0.89, ...]  # 768 valores

        >>> get_transformer_embedding("chronic pain management in elderly patients")
        [0.12, 0.45, -0.23, ...]  # 768 valores

    Nota:
        - El modelo BiomedNLP-PubMedBERT genera 768 dimensiones nativas (sin padding)
        - Estos embeddings se compararán con los de la BD usando similitud de coseno
        - Queries similares semánticamente tendrán vectores cercanos en el espacio
    """
    if not query_text or not query_text.strip():
        logger.warning("⚠ Texto vacío recibido para embedding, usando vector aleatorio")
        return get_simple_embedding("", 768)

    try:
        model = get_model()
        if model:
            # Generar el embedding usando BiomedNLP-PubMedBERT
            # El modelo automáticamente:
            # - Convierte a minúsculas (uncased)
            # - Tokeniza con vocabulario médico
            # - Genera vector de 768 dimensiones
            embedding = model.encode(query_text)

            # Verificar dimensión (debe ser 768 para BiomedNLP-PubMedBERT)
            if len(embedding) != 768:
                logger.error(
                    f"⚠ Dimensión incorrecta del embedding: {len(embedding)} "
                    f"(se esperaban 768). Esto indica un problema con el modelo."
                )
                # Intentar ajustar la dimensión como medida de emergencia
                return _adjust_embedding_to_768(embedding)

            logger.debug(f"✓ Embedding generado: 768 dimensiones (modelo médico)")
            return embedding.tolist()

        else:
            logger.warning("⚠ Modelo médico no disponible, usando método fallback")
            return get_simple_embedding(query_text, 768)

    except Exception as e:
        logger.error(f"✗ Error al generar embedding con BiomedNLP-PubMedBERT: {e}")
        logger.warning("Usando método fallback debido al error")
        return get_simple_embedding(query_text, 768)

def _adjust_embedding_to_768(embedding: np.ndarray) -> List[float]:
    """
    Ajusta un embedding a 768 dimensiones si tiene tamaño incorrecto.

    Método de emergencia que solo debería ejecutarse si hay un problema
    con el modelo. Normalmente BiomedNLP-PubMedBERT genera 768 dim directamente.

    Args:
        embedding: Array numpy con embedding de dimensión incorrecta

    Returns:
        List[float]: Embedding ajustado a 768 dimensiones

    Nota:
        - Si > 768: trunca las dimensiones extra
        - Si < 768: rellena con ceros (subóptimo pero funcional)
    """
    current_dim = len(embedding)
    target_dim = 768

    if current_dim > target_dim:
        logger.warning(f"Truncando embedding de {current_dim} a {target_dim} dimensiones")
        return embedding[:target_dim].tolist()
    else:
        logger.warning(f"Rellenando embedding de {current_dim} a {target_dim} con ceros")
        padded = np.zeros(target_dim)
        padded[:current_dim] = embedding
        return padded.tolist()
    
def diagnose_embeddings(query_text: str):
    """
    Función para diagnóstico de embeddings.
    Genera embeddings con ambos métodos y los compara.
    """
    logger.info(f"Diagnosticando generación de embeddings para: '{query_text}'")
    
    try:
        # Generar con método transformer
        start = time.time()
        emb_transformer = get_transformer_embedding(query_text)
        transformer_time = time.time() - start
        
        # Generar con método simple
        start = time.time()
        emb_simple = get_simple_embedding(query_text)
        simple_time = time.time() - start
        
        # Comparar dimensiones
        logger.info(f"Dimensión transformer: {len(emb_transformer)}, dimensión simple: {len(emb_simple)}")
        
        # Comparar algunos valores
        if len(emb_transformer) > 0 and len(emb_simple) > 0:
            logger.info(f"Primeros 5 valores transformer: {emb_transformer[:5]}")
            logger.info(f"Primeros 5 valores simple: {emb_simple[:5]}")
            
        # Comparar tiempo
        logger.info(f"Tiempo transformer: {transformer_time:.4f}s, tiempo simple: {simple_time:.4f}s")
        
        # Verificar si son diferentes
        if np.allclose(np.array(emb_transformer[:10]), np.array(emb_simple[:10]), atol=1e-3):
            logger.warning("Los embeddings son muy similares, posible problema en la generación!")
        else:
            logger.info("Los embeddings son diferentes, como se esperaba")
            
    except Exception as e:
        logger.error(f"Error en diagnóstico de embeddings: {e}")


async def perform_vector_search(
    query: str,
    id_categoria: Optional[int] = None,
    limit: int = 25,
    offset: int = 0,
    similarity_threshold: float = 0.15
) -> Tuple[List[Dict[Any, Any]], int, bool, bool]:
    """
    Realiza una búsqueda semántica de documentos médicos usando embeddings.

    Esta función implementa búsqueda vectorial por similitud usando el modelo
    BiomedNLP-PubMedBERT. El proceso completo es:

    1. Convierte la query del usuario en un embedding de 768 dimensiones
    2. Compara este embedding con todos los documentos en la BD usando similitud de coseno
    3. Filtra resultados que superen el threshold de similitud
    4. Ordena por similitud (mayor a menor)
    5. Retorna los resultados más relevantes

    Args:
        query (str): Texto de búsqueda del usuario
            Ejemplos: "diabetes treatment", "chronic pain management"

        id_categoria (Optional[int]): ID de categoría médica para filtrar resultados
            None = buscar en todas las categorías
            Ejemplo: 5 para buscar solo en "Cardiología"

        limit (int): Número máximo de resultados a retornar (paginación)
            Default: 25 documentos

        offset (int): Posición inicial para paginación
            Default: 0 (primera página)

        similarity_threshold (float): Umbral mínimo de similitud (0-1)
            - 0.0 = cualquier similitud (muy permisivo)
            - 0.15 = similitud baja/media (default, equilibrado)
            - 0.3 = similitud media/alta (más restrictivo)
            - 0.5+ = similitud muy alta (muy restrictivo)

    Returns:
        Tuple con 4 elementos:
        - results (List[Dict]): Lista de documentos encontrados, cada uno con:
            * id: ID del documento
            * titulo: Título del artículo
            * autor: Lista de autores
            * fecha_publicacion: Fecha de publicación
            * url_fuente: URL al artículo original
            * categoria: Categoría médica
            * texto_resumen: Resumen del abstract
            * score: Similitud con la query (0-1, mayor = más similar)

        - total (int): Número total de resultados encontrados

        - has_more (bool): Si hay más resultados disponibles
            True = hay más páginas
            False = última página

        - filtered_by_similarity (bool): Si se filtraron resultados por baja similitud
            True = algunos resultados fueron excluidos por no superar el threshold
            False = todos los resultados superaron el threshold

    Raises:
        Exception: Si hay error de conexión a la BD o al generar embeddings

    Ejemplos:
        >>> # Búsqueda simple
        >>> results, total, has_more, filtered = await perform_vector_search("diabetes")
        >>> print(f"Encontrados {total} documentos sobre diabetes")

        >>> # Búsqueda en categoría específica con threshold alto
        >>> results, total, _, _ = await perform_vector_search(
        ...     query="heart failure treatment",
        ...     id_categoria=2,  # Cardiología
        ...     similarity_threshold=0.3
        ... )

    Notas Técnicas:
        - Usa índice IVFFLAT en PostgreSQL para búsquedas rápidas
        - Similitud de coseno: mide el ángulo entre vectores (0-1)
        - El modelo médico mejora mucho la búsqueda vs modelos genéricos
        - Primer búsqueda puede tardar ~500ms (carga del modelo)
        - Búsquedas subsecuentes ~50-100ms
    """
    try:
        # Diagnóstico de embeddings
        diagnose_embeddings(query)

        # Obtenemos el embedding de la query con el transformer
        start_time = time.time()
        query_embedding = get_transformer_embedding(query)
        logger.info(f"Embedding generado en {time.time() - start_time:.2f} segundos con método transformer")
        
        # Creamos la conexión con la base de datos
        conn = create_connection()
        cursor = conn.cursor()
        
        # Si es una búsqueda específica de "lungs", realizamos un diagnóstico especial
        if query.lower() == "lungs":
            logger.info("¡Búsqueda de 'lungs' detectada! Realizando diagnóstico extendido...")
            try:
                # Búsqueda directa para verificar si existen documentos con "lung" en alguna parte
                cursor.execute("""
                SELECT COUNT(*) FROM documento d 
                LEFT JOIN resumen r ON d.id = r.id_documento
                WHERE 
                    LOWER(d.titulo) LIKE '%lung%' OR 
                    LOWER(d.titulo) LIKE '%pulm%' OR
                    LOWER(r.texto_resumen) LIKE '%lung%' OR
                    LOWER(r.texto_resumen) LIKE '%pulm%'
                """)
                lung_docs = cursor.fetchone()[0]
                logger.info(f"Found {lung_docs} documents containing 'lung' or 'pulm' in title or summary")
                
                # Mostrar ejemplos de documentos que contienen estos términos
                if lung_docs > 0:
                    cursor.execute("""
                    SELECT d.id, d.titulo, r.texto_resumen 
                    FROM documento d 
                    LEFT JOIN resumen r ON d.id = r.id_documento
                    WHERE 
                        LOWER(d.titulo) LIKE '%lung%' OR 
                        LOWER(d.titulo) LIKE '%pulm%' OR
                        LOWER(r.texto_resumen) LIKE '%lung%' OR
                        LOWER(r.texto_resumen) LIKE '%pulm%'
                    LIMIT 2
                    """)
                    examples = cursor.fetchall()
                    for ex in examples:
                        logger.info(f"Ejemplo ID: {ex[0]}, Título: {ex[1][:50]}...")
                        if ex[2]:
                            logger.info(f"Resumen: {ex[2][:100]}...")
            except Exception as e:
                logger.error(f"Error en diagnóstico de 'lungs': {e}")
        
        # Comprobamos que haya documentos en la base de datos
        cursor.execute("SELECT COUNT(*) FROM documento")
        doc_count = cursor.fetchone()[0]
        logger.info(f"Total documents in database: {doc_count}")
        
        if doc_count == 0:
            logger.warning("No documents in database!")
            return [], 0, False, False
            
        # Debugging: mostramos un documento de ejemplo
        cursor.execute("SELECT id, titulo, autor FROM documento LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            logger.info(f"Sample document - ID: {sample[0]}, Title: {sample[1]}, Author: {sample[2]}")
            
        # Primero, probamos una consulta simple para verificar la conexión
        try:
            logger.info("Trying simple query...")
            cursor.execute("SELECT id, titulo FROM documento LIMIT 5")
            simple_results = cursor.fetchall()
            logger.info(f"Simple query returned {len(simple_results)} results")
            for row in simple_results:
                logger.info(f"Doc ID: {row[0]}, Title: {row[1]}")
        except Exception as e:
            logger.error(f"Simple query failed: {e}")
        
        # Intentamos realizar la búsqueda vectorial
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
            
            if not has_vector or vectorized_count == 0:
                logger.warning("Vector search not possible: extension or vectorized documents missing")
                raise Exception("Vector search not possible")
            
            # Si tenemos la extensión y documentos vectorizados, procedemos con la búsqueda
            logger.info("Executing vector search with embedding...")
            
            # Primero, verificamos el tipo de la columna contenido_vectorizado
            cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'documento' AND column_name = 'contenido_vectorizado'")
            column_info = cursor.fetchone()
            if column_info:
                logger.info(f"Column type: {column_info[1]}")
            
            # CORRECCIÓN: Convertimos la lista a una cadena adecuada para el tipo vector
            embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
            logger.info(f"Prepared vector string format with length: {len(embedding_str)}")

            # SQL para búsqueda vectorial usando el operador de distancia coseno (<=>)
            # Recuperamos más resultados de los necesarios y filtramos en Python para mayor precisión
            # La paginación se hará en el frontend para simplificar

            # Límite de recuperación inicial (traemos más para filtrar después)
            initial_fetch = 1000

            # Convertimos explícitamente el parámetro al tipo vector
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
                (1 - (d.contenido_vectorizado <=> %s::vector)) as score
            FROM
                documento d
            LEFT JOIN
                categoria c ON d.id_categoria = c.id
            LEFT JOIN
                resumen r ON d.id = r.id_documento
            WHERE
                d.contenido_vectorizado IS NOT NULL
            """

            params = [embedding_str]

            # Añadir filtro por categoría si está especificado
            if id_categoria is not None:
                vector_sql += " AND d.id_categoria = %s"
                params.append(id_categoria)

            # Ordenar por similitud (mayor score primero)
            vector_sql += " ORDER BY score DESC LIMIT %s"
            params.append(initial_fetch)

            logger.info(f"Ejecutando búsqueda vectorial (recuperando top {initial_fetch} por similitud)")
            cursor.execute(vector_sql, params)
            all_rows = cursor.fetchall()
            logger.info(f"Búsqueda vectorial retornó {len(all_rows)} resultados totales")

            # FILTRAR en Python por threshold de similitud
            # Manejar casos donde row[8] (score) puede ser None si el documento no tiene vector
            filtered_rows = [row for row in all_rows if row[8] is not None and row[8] >= similarity_threshold]
            logger.info(f"Después de filtrar por similitud >= {similarity_threshold}: {len(filtered_rows)} resultados")

            # Log de scores para debugging
            if filtered_rows:
                scores = [row[8] for row in filtered_rows]
                logger.info(f"Score máximo: {max(scores):.4f}, Score mínimo: {min(scores):.4f}, Score promedio: {sum(scores)/len(scores):.4f}")
                if len(filtered_rows) >= 5:
                    logger.info(f"Top 5 scores: {[f'{s:.4f}' for s in sorted(scores, reverse=True)[:5]]}")
                    logger.info(f"Bottom 5 scores: {[f'{s:.4f}' for s in sorted(scores)[:5]]}")

            # Limitar a máximo 500 resultados después del filtrado
            max_results = 500
            if len(filtered_rows) > max_results:
                logger.info(f"Limitando resultados de {len(filtered_rows)} a {max_results}")
                filtered_rows = filtered_rows[:max_results]

            # Retornamos los resultados filtrados
            rows = filtered_rows
            total_count = len(filtered_rows)
            has_more = False  # Ya no aplicamos paginación en backend
            filtered_by_similarity = len(filtered_rows) < len(all_rows)  # True si filtramos algunos

            logger.info(f"Retornando {len(rows)} resultados totales (filtrados: {filtered_by_similarity})")

            # Si tenemos resultados, retornamos
            if not rows:
                total_count = 0
                has_more = False
                filtered_by_similarity = False
                # Si la búsqueda vectorial no devuelve resultados, pasaremos al fallback
                logger.info("Vector search returned no results after filtering, will fall back to text search...")
                raise Exception("No vector search results")
                
        except Exception as e:
            logger.error(f"Vector search failed, falling back to text search: {str(e)}")
            
            # Búsqueda de texto como fallback - MEJORADA para buscar todos los términos
            search_terms = query.lower().split()
            search_conditions = []
            params = []
            
            # Construimos condiciones para cada término de búsqueda
            for term in search_terms:
                search_pattern = f"%{term}%"
                search_conditions.append("(LOWER(d.titulo) LIKE %s OR LOWER(d.autor) LIKE %s OR LOWER(r.texto_resumen) LIKE %s)")
                params.extend([search_pattern, search_pattern, search_pattern])
            
            # Construimos la consulta SQL con todas las condiciones
            search_sql = f"""
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
                {" OR ".join(search_conditions)}
            """
            
            # Si se especifica una categoría, se aplica como filtro
            if id_categoria is not None:
                search_sql += f" AND d.id_categoria = %s"
                params.append(id_categoria)
            
            # Se ejecuta la consulta con límite y offset
            search_sql += " ORDER BY d.fecha_publicacion DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            logger.info(f"Executing text search with {len(search_terms)} terms")
            cursor.execute(search_sql, params)
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
            has_more = (offset + limit) < total_count
            filtered_by_similarity = False
        
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
        return results, total_count, has_more, filtered_by_similarity

    except Exception as e:
        logger.error(f"Error en búsqueda vectorial: {str(e)}")

        # Se devuelve vacío como último fallback
        return [], 0, False, False