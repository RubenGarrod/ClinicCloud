#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClinicCloud - Scraper Masivo Optimizado para Ejecución Nocturna
================================================================

Este scraper está diseñado para:
1. Consumir todos los recursos disponibles del servidor durante la madrugada
2. Cargar modelos ML UNA SOLA VEZ y procesarlos en batch
3. Procesar miles de documentos en una sola ejecución
4. Auto-apagarse al finalizar o cuando llega el horario de producción

Optimizaciones:
- Batch processing de embeddings (100 docs a la vez)
- Batch processing de resúmenes (50 docs a la vez)
- Singleton para modelos ML (cargados una sola vez)
- Procesamiento paralelo con multiprocessing
- Uso eficiente de memoria con generators

Uso:
    python scraper_masivo.py --max-docs 10000 --batch-size 100
    python scraper_masivo.py --max-docs 50000 --start-hour 2 --stop-hour 7
"""

import os
import sys
import time
import logging
import argparse
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import signal
import multiprocessing as mp
from queue import Queue
import threading
import random

# Import query templates
try:
    from query_templates import MEDICAL_QUERIES, QUERY_MODIFIERS, TRENDING_TOPICS
except ImportError:
    logger.warning("query_templates.py not found. Using fallback queries.")
    MEDICAL_QUERIES = None

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(processName)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# =====================================================
# Singleton para Modelos ML
# =====================================================
class ModelManager:
    """
    Gestor singleton para todos los modelos ML.
    Carga los modelos UNA SOLA VEZ y los mantiene en memoria.
    """
    _instance = None
    _embedding_model = None
    _summarization_model = None
    _tokenizer = None
    _loading_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def get_embedding_model(self):
        """Obtiene el modelo de embeddings (S-PubMedBert)"""
        if self._embedding_model is None:
            with self._loading_lock:
                if self._embedding_model is None:  # Double-check
                    logger.info("🔄 Cargando modelo S-PubMedBert-MS-MARCO...")
                    from sentence_transformers import SentenceTransformer
                    self._embedding_model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
                    logger.info("✅ Modelo S-PubMedBert cargado (768 dims)")
        return self._embedding_model

    def get_summarization_model(self):
        """Obtiene el modelo de resúmenes (BART)"""
        if self._summarization_model is None or self._tokenizer is None:
            with self._loading_lock:
                if self._summarization_model is None:
                    logger.info("🔄 Cargando modelo BART para resúmenes...")
                    from transformers import BartForConditionalGeneration, BartTokenizer
                    model_name = "facebook/bart-large-cnn"
                    self._tokenizer = BartTokenizer.from_pretrained(model_name)
                    self._summarization_model = BartForConditionalGeneration.from_pretrained(model_name)
                    logger.info("✅ Modelo BART cargado")
        return self._summarization_model, self._tokenizer

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings en batch (mucho más eficiente).

        Args:
            texts: Lista de textos a procesar

        Returns:
            Lista de vectores de 768 dimensiones
        """
        model = self.get_embedding_model()
        embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
        return [emb.tolist() for emb in embeddings]

    def generate_summaries_batch(self, abstracts: List[str], max_length: int = 150) -> List[str]:
        """
        Genera resúmenes en batch (mucho más eficiente).

        Args:
            abstracts: Lista de abstracts a resumir
            max_length: Longitud máxima del resumen

        Returns:
            Lista de resúmenes
        """
        model, tokenizer = self.get_summarization_model()

        summaries = []
        batch_size = 8  # BART consume mucha memoria

        for i in range(0, len(abstracts), batch_size):
            batch = abstracts[i:i+batch_size]

            inputs = tokenizer(
                batch,
                max_length=1024,
                truncation=True,
                padding=True,
                return_tensors="pt"
            )

            summary_ids = model.generate(
                inputs["input_ids"],
                max_length=max_length,
                min_length=40,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )

            batch_summaries = [
                tokenizer.decode(s, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                for s in summary_ids
            ]
            summaries.extend(batch_summaries)

            logger.info(f"Resúmenes generados: {i+len(batch)}/{len(abstracts)}")

        return summaries


# =====================================================
# Fetcher de PubMed
# =====================================================
class PubMedFetcher:
    """
    Obtiene artículos de PubMed usando la API eUtils.
    Optimizado para scraping masivo.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('NCBI_API_KEY', '')
        self.base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        # Con API key: 10 requests/segundo. Sin API key: 3 requests/segundo
        self.delay = 0.1 if self.api_key else 0.34
        self.last_request_time = 0

    def _rate_limit(self):
        """Respeta los límites de tasa de PubMed"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def search_ids(self, query: str, max_results: int = 10000,
                   days_back: int = 30, offset: int = 0) -> List[str]:
        """
        Busca IDs de artículos para un término con filtro de fecha.

        Args:
            query: Término de búsqueda
            max_results: Máximo número de resultados
            days_back: Días hacia atrás para filtrar (default: 30)
            offset: Offset para paginación (retstart)

        Returns:
            Lista de PMIDs
        """
        import requests
        from datetime import datetime, timedelta

        self._rate_limit()

        # Calcular rango de fechas
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=days_back)

        # Formato PubMed: YYYY/MM/DD
        date_filter = f"({fecha_inicio.strftime('%Y/%m/%d')}:{fecha_fin.strftime('%Y/%m/%d')}[dp])"

        # Agregar filtro de fecha al query
        full_query = f"{query} AND {date_filter}"

        url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': full_query,
            'retmode': 'json',
            'retmax': str(max_results),
            'retstart': str(offset),  # Paginación
            'sort': 'pub_date',  # Ordenar por fecha de publicación (más recientes primero)
            'datetype': 'pdat'  # Publication date
        }

        if self.api_key:
            params['api_key'] = self.api_key

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            ids = data.get('esearchresult', {}).get('idlist', [])
            total_count = int(data.get('esearchresult', {}).get('count', 0))

            logger.info(f"Búsqueda '{query}' (últimos {days_back} días, offset {offset}): {len(ids)} de {total_count} encontrados")
            return ids
        except Exception as e:
            logger.error(f"Error en búsqueda '{query}': {e}")
            return []

    def fetch_articles(self, pmids: List[str]) -> List[Dict]:
        """
        Obtiene detalles de artículos por PMID.
        Procesa en lotes de 200 (límite de PubMed).

        Args:
            pmids: Lista de PMIDs

        Returns:
            Lista de diccionarios con datos de artículos
        """
        import requests
        from lxml import etree

        articles = []
        batch_size = 200

        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i+batch_size]
            self._rate_limit()

            url = f"{self.base_url}/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(batch_pmids),
                'retmode': 'xml'
            }

            if self.api_key:
                params['api_key'] = self.api_key

            try:
                response = requests.get(url, params=params, timeout=60)
                response.raise_for_status()

                # Parsear XML
                root = etree.fromstring(response.content)

                for article_xml in root.xpath('//PubmedArticle'):
                    article = self._parse_article_xml(article_xml)
                    if article:
                        articles.append(article)

                logger.info(f"Artículos obtenidos: {len(articles)}/{len(pmids)}")

            except Exception as e:
                logger.error(f"Error al obtener batch {i}-{i+batch_size}: {e}")
                continue

        return articles

    def _parse_article_xml(self, article_xml) -> Optional[Dict]:
        """Parsea un artículo XML de PubMed"""
        try:
            # PMID
            pmid_elem = article_xml.xpath('.//PMID/text()')
            pmid = pmid_elem[0] if pmid_elem else None

            # Título
            title_elem = article_xml.xpath('.//ArticleTitle/text()')
            title = ' '.join(title_elem) if title_elem else None

            # Abstract
            abstract_parts = article_xml.xpath('.//AbstractText/text()')
            abstract = ' '.join(abstract_parts) if abstract_parts else ''

            # Autores
            authors = []
            for author in article_xml.xpath('.//Author'):
                lastname = author.xpath('.//LastName/text()')
                firstname = author.xpath('.//ForeName/text()')
                if lastname:
                    name = f"{lastname[0]}"
                    if firstname:
                        name = f"{firstname[0]} {name}"
                    authors.append(name)
            author_str = ', '.join(authors[:20])  # Limitar a 20 autores

            # Fecha - Intentar extraer de múltiples ubicaciones
            # Primero intentar PubDate (fecha de publicación del journal)
            year = article_xml.xpath('.//PubDate/Year/text()')
            month = article_xml.xpath('.//PubDate/Month/text()')
            day = article_xml.xpath('.//PubDate/Day/text()')

            # Si PubDate no tiene info completa, intentar ArticleDate (fecha electrónica)
            if not year or not month:
                year = article_xml.xpath('.//ArticleDate/Year/text()') or year
                month = article_xml.xpath('.//ArticleDate/Month/text()') or month
                day = article_xml.xpath('.//ArticleDate/Day/text()') or day

            # Si aún no hay fecha, intentar DateCompleted o DateRevised
            if not year or not month:
                year = article_xml.xpath('.//DateCompleted/Year/text()') or year
                month = article_xml.xpath('.//DateCompleted/Month/text()') or month
                day = article_xml.xpath('.//DateCompleted/Day/text()') or day

            fecha = None
            if year:
                # Mapeo de meses textuales a numéricos
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
                    'January': '01', 'February': '02', 'March': '03', 'April': '04',
                    'June': '06', 'July': '07', 'August': '08',
                    'September': '09', 'October': '10', 'November': '11', 'December': '12'
                }

                year_str = year[0] if year else None
                month_str = '01'  # Default
                day_str = '01'    # Default

                if month:
                    month_val = month[0]
                    # Convertir mes textual a numérico si es necesario
                    if month_val in month_map:
                        month_str = month_map[month_val]
                    elif month_val.isdigit():
                        month_str = month_val.zfill(2)
                    else:
                        month_str = '01'

                if day and day[0].isdigit():
                    day_str = day[0].zfill(2)

                if year_str:
                    fecha = f"{year_str}-{month_str}-{day_str}"
                    logger.debug(f"PMID {pmid}: Fecha extraída: {fecha}")
                else:
                    logger.warning(f"PMID {pmid}: No se pudo extraer fecha")

            # MeSH Terms
            mesh_terms = article_xml.xpath('.//MeshHeading/DescriptorName/text()')

            # Journal
            journal = article_xml.xpath('.//Journal/Title/text()')
            journal = journal[0] if journal else None

            # DOI
            doi_elem = article_xml.xpath('.//ArticleId[@IdType="doi"]/text()')
            doi = doi_elem[0] if doi_elem else None

            # Publication Types
            pub_types = article_xml.xpath('.//PublicationType/text()')

            # Language
            lang = article_xml.xpath('.//Language/text()')
            language = lang[0] if lang else 'eng'

            if not title:
                return None

            return {
                'pmid': pmid,
                'titulo': title,
                'abstract': abstract,
                'autor': author_str,
                'fecha_publicacion': fecha,
                'mesh_terms': mesh_terms,
                'journal': journal,
                'doi': doi,
                'publication_types': pub_types,
                'language': language,
                'url_fuente': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }

        except Exception as e:
            logger.error(f"Error parseando artículo: {e}")
            return None


# =====================================================
# Database Manager
# =====================================================
class DatabaseManager:
    """Gestiona la conexión y operaciones de base de datos"""

    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """Conecta a la base de datos"""
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME', 'cliniccloud'),
                user=os.getenv('DB_USER', 'cliniccloud'),
                password=os.getenv('DB_PASSWORD', 'changeme'),
                host=os.getenv('DB_HOST', 'db'),
                port=os.getenv('DB_PORT', '5432')
            )
            self.cursor = self.conn.cursor()
            logger.info("✅ Conectado a la base de datos")
            self._ensure_tracking_table()
        except Exception as e:
            logger.error(f"❌ Error conectando a BD: {e}")
            raise

    def _ensure_tracking_table(self):
        """Asegura que la tabla de tracking existe"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pmid_procesado (
                    id SERIAL PRIMARY KEY,
                    pmid VARCHAR(20) NOT NULL UNIQUE,
                    fecha_procesado TIMESTAMP NOT NULL DEFAULT NOW(),
                    query_origen VARCHAR(500),
                    insertado BOOLEAN DEFAULT FALSE
                )
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pmid_procesado_pmid
                ON pmid_procesado(pmid)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pmid_procesado_fecha
                ON pmid_procesado(fecha_procesado)
            """)
            self.conn.commit()
        except Exception as e:
            logger.warning(f"Tabla pmid_procesado ya existe o error: {e}")
            self.conn.rollback()

    def filter_unprocessed_pmids(self, pmids: List[str]) -> List[str]:
        """
        Filtra PMIDs que ya fueron procesados.

        Args:
            pmids: Lista de PMIDs a verificar

        Returns:
            Lista de PMIDs no procesados
        """
        if not pmids:
            return []

        try:
            # Buscar PMIDs ya procesados
            placeholders = ','.join(['%s'] * len(pmids))
            query = f"SELECT pmid FROM pmid_procesado WHERE pmid IN ({placeholders})"
            self.cursor.execute(query, pmids)

            procesados = {row[0] for row in self.cursor.fetchall()}
            no_procesados = [pmid for pmid in pmids if pmid not in procesados]

            logger.info(f"🔍 PMIDs: {len(pmids)} total, {len(procesados)} ya procesados, {len(no_procesados)} nuevos")
            return no_procesados

        except Exception as e:
            logger.error(f"Error filtrando PMIDs: {e}")
            return pmids  # En caso de error, retornar todos

    def mark_pmids_as_processed(self, pmids: List[str], query_origen: str = None):
        """
        Marca PMIDs como procesados en el tracking.

        Args:
            pmids: Lista de PMIDs procesados
            query_origen: Query que originó estos PMIDs
        """
        if not pmids:
            return

        try:
            for pmid in pmids:
                self.cursor.execute(
                    """
                    INSERT INTO pmid_procesado (pmid, query_origen, insertado)
                    VALUES (%s, %s, FALSE)
                    ON CONFLICT (pmid) DO NOTHING
                    """,
                    (pmid, query_origen)
                )
            self.conn.commit()
            logger.debug(f"✓ {len(pmids)} PMIDs marcados como procesados")

        except Exception as e:
            logger.error(f"Error marcando PMIDs como procesados: {e}")
            self.conn.rollback()

    def mark_pmid_as_inserted(self, pmid: str):
        """Marca un PMID como insertado exitosamente"""
        try:
            self.cursor.execute(
                "UPDATE pmid_procesado SET insertado = TRUE WHERE pmid = %s",
                (pmid,)
            )
        except Exception as e:
            logger.error(f"Error marcando PMID {pmid} como insertado: {e}")

    def cleanup_old_tracking(self, days: int = 90):
        """
        Limpia registros de tracking antiguos.

        Args:
            days: Días de antigüedad para eliminar
        """
        try:
            self.cursor.execute(
                """
                DELETE FROM pmid_procesado
                WHERE fecha_procesado < NOW() - INTERVAL '%s days'
                """,
                (days,)
            )
            deleted = self.cursor.rowcount
            self.conn.commit()
            if deleted > 0:
                logger.info(f"🧹 Limpieza: {deleted} registros de tracking eliminados (>{days} días)")
        except Exception as e:
            logger.error(f"Error en limpieza de tracking: {e}")
            self.conn.rollback()

    def get_categoria_id(self, categoria_nombre: str) -> int:
        """Obtiene o crea una categoría"""
        try:
            self.cursor.execute(
                "SELECT id FROM categoria WHERE nombre = %s",
                (categoria_nombre,)
            )
            result = self.cursor.fetchone()

            if result:
                return result[0]

            # Crear categoría
            self.cursor.execute(
                "INSERT INTO categoria (nombre) VALUES (%s) RETURNING id",
                (categoria_nombre,)
            )
            self.conn.commit()
            return self.cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Error obteniendo categoría: {e}")
            self.conn.rollback()
            # Retornar categoría por defecto (Medicina General)
            self.cursor.execute("SELECT id FROM categoria WHERE nombre = 'Medicina General'")
            return self.cursor.fetchone()[0]

    def insert_documents_batch(self, documents: List[Dict], embeddings: List[List[float]],
                               summaries: List[str], categorias_ids: List[int]):
        """
        Inserta documentos en batch (mucho más rápido).

        Args:
            documents: Lista de diccionarios con datos de documentos
            embeddings: Lista de vectores de embeddings
            summaries: Lista de resúmenes
            categorias_ids: Lista de IDs de categorías
        """
        try:
            inserted_count = 0
            skipped_count = 0

            for doc, embedding, summary, categoria_id in zip(documents, embeddings, summaries, categorias_ids):
                try:
                    # Verificar si ya existe (por título o PMID)
                    self.cursor.execute(
                        "SELECT id FROM documento WHERE titulo = %s OR url_fuente = %s",
                        (doc['titulo'], doc['url_fuente'])
                    )
                    if self.cursor.fetchone():
                        skipped_count += 1
                        continue

                    # Parsear fecha
                    fecha = None
                    fecha_str = doc.get('fecha_publicacion')
                    if fecha_str:
                        try:
                            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                                try:
                                    fecha = datetime.strptime(fecha_str, fmt)
                                    logger.debug(f"Fecha parseada correctamente: {fecha_str} -> {fecha}")
                                    break
                                except ValueError:
                                    continue
                            if not fecha:
                                logger.warning(f"No se pudo parsear fecha '{fecha_str}' para documento: {doc.get('titulo', 'N/A')[:50]}")
                        except Exception as e:
                            logger.error(f"Error parseando fecha '{fecha_str}': {e}")
                    else:
                        logger.warning(f"Documento sin fecha: {doc.get('titulo', 'N/A')[:50]}")

                    # Insertar documento
                    self.cursor.execute(
                        """
                        INSERT INTO documento
                        (titulo, autor, fecha_publicacion, contenido_vectorizado, url_fuente, id_categoria,
                         mesh_terms, journal, doi, publication_types, language)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            doc['titulo'],
                            doc['autor'],
                            fecha,
                            embedding,
                            doc['url_fuente'],
                            categoria_id,
                            doc['mesh_terms'],
                            doc['journal'],
                            doc['doi'],
                            doc['publication_types'],
                            doc['language']
                        )
                    )
                    doc_id = self.cursor.fetchone()[0]

                    # Insertar resumen si existe
                    if summary and doc.get('abstract'):
                        self.cursor.execute(
                            "INSERT INTO resumen (id_documento, texto_resumen) VALUES (%s, %s)",
                            (doc_id, summary)
                        )

                    # Marcar PMID como insertado
                    if doc.get('pmid'):
                        self.mark_pmid_as_inserted(doc['pmid'])

                    inserted_count += 1

                    # Commit cada 100 documentos
                    if inserted_count % 100 == 0:
                        self.conn.commit()
                        logger.info(f"📝 Insertados: {inserted_count}, Saltados: {skipped_count}")

                except Exception as e:
                    logger.error(f"Error insertando documento '{doc.get('titulo', 'N/A')[:50]}': {e}")
                    self.conn.rollback()
                    continue

            # Commit final
            self.conn.commit()
            logger.info(f"✅ Batch completado - Insertados: {inserted_count}, Saltados: {skipped_count}")

        except Exception as e:
            logger.error(f"❌ Error en insert_documents_batch: {e}")
            self.conn.rollback()

    def track_query_execution(self, query_text: str, categoria: str,
                               pmids_encontrados: int, pmids_nuevos: int,
                               pmids_insertados: int, duracion: int):
        """
        Registra la ejecución de una query para tracking.

        Args:
            query_text: Texto de la query ejecutada
            categoria: Categoría médica asociada
            pmids_encontrados: PMIDs totales encontrados
            pmids_nuevos: PMIDs que no estaban procesados
            pmids_insertados: PMIDs insertados exitosamente
            duracion: Duración en segundos
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO query_tracking
                (query_text, categoria, pmids_encontrados, pmids_nuevos, pmids_insertados, duracion_segundos)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (query_text, categoria, pmids_encontrados, pmids_nuevos, pmids_insertados, duracion)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error registrando query tracking: {e}")
            self.conn.rollback()

    def get_category_priorities(self) -> List[Dict]:
        """
        Obtiene prioridades de categorías basadas en cobertura.

        Returns:
            Lista de diccionarios con categoría y prioridad
        """
        try:
            # Actualizar cobertura
            self.cursor.execute("SELECT update_categoria_coverage()")
            self.conn.commit()

            # Obtener prioridades
            self.cursor.execute(
                """
                SELECT categoria, priority_score, total_documentos, dias_desde_ultimo_scrape
                FROM query_priority
                ORDER BY priority_score DESC
                LIMIT 50
                """
            )

            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'categoria': row[0],
                    'priority_score': row[1],
                    'total_documentos': row[2],
                    'dias_desde_ultimo_scrape': row[3]
                })

            return results

        except Exception as e:
            logger.error(f"Error obteniendo prioridades: {e}")
            return []

    def get_recently_scraped_queries(self, days: int = 7) -> List[str]:
        """
        Obtiene queries ejecutadas recientemente.

        Args:
            days: Días hacia atrás a considerar

        Returns:
            Lista de query texts ejecutadas recientemente
        """
        try:
            self.cursor.execute(
                """
                SELECT DISTINCT query_text
                FROM query_tracking
                WHERE fecha_ejecutada > NOW() - INTERVAL '%s days'
                """,
                (days,)
            )
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo queries recientes: {e}")
            return []

    def close(self):
        """Cierra la conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Conexión a BD cerrada")


# =====================================================
# Scraper Masivo Principal
# =====================================================
class MassiveScraper:
    """
    Scraper masivo optimizado para ejecución nocturna.
    """

    def __init__(self, max_docs: int = 10000, batch_size: int = 100,
                 start_hour: int = 2, stop_hour: int = 7):
        self.max_docs = max_docs
        self.batch_size = batch_size
        self.start_hour = start_hour
        self.stop_hour = stop_hour
        self.should_stop = False

        # Componentes
        self.fetcher = PubMedFetcher()
        self.db = DatabaseManager()
        self.model_manager = ModelManager()

        # Estadísticas
        self.stats = {
            'fetched': 0,
            'processed': 0,
            'inserted': 0,
            'errors': 0,
            'start_time': time.time()
        }

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Maneja señales de interrupción"""
        logger.warning("⚠️  Señal de interrupción recibida. Finalizando...")
        self.should_stop = True

    def _should_continue(self) -> bool:
        """Verifica si debe continuar el scraping"""
        if self.should_stop:
            return False

        current_hour = datetime.now().hour
        if not (self.start_hour <= current_hour < self.stop_hour):
            logger.warning(f"⏰ Fuera del horario permitido ({self.start_hour}:00 - {self.stop_hour}:00). Deteniendo...")
            return False

        if self.stats['processed'] >= self.max_docs:
            logger.info(f"✅ Meta de {self.max_docs} documentos alcanzada")
            return False

        return True

    def run(self):
        """Ejecuta el scraping masivo"""
        logger.info("="*80)
        logger.info("🚀 INICIANDO SCRAPER MASIVO")
        logger.info(f"   Max docs: {self.max_docs}")
        logger.info(f"   Batch size: {self.batch_size}")
        logger.info(f"   Horario: {self.start_hour}:00 - {self.stop_hour}:00")
        logger.info("="*80)

        # Verificar horario
        if not self._should_continue():
            logger.error("❌ No se puede iniciar fuera del horario permitido")
            return

        # Pre-cargar modelos
        logger.info("🔄 Pre-cargando modelos ML...")
        self.model_manager.get_embedding_model()
        self.model_manager.get_summarization_model()
        logger.info("✅ Modelos cargados en memoria")

        # Limpieza periódica de tracking (cada ejecución)
        self.db.cleanup_old_tracking(days=90)

        # Términos de búsqueda médicos
        search_queries = self._generate_search_queries()
        logger.info(f"📋 {len(search_queries)} términos de búsqueda generados")

        # Fetch PMIDs con filtro de fecha (últimos 30 días)
        all_pmids = []
        all_pmids_by_query = {}  # Para tracking
        days_back = int(os.getenv('SCRAPER_DAYS_BACK', '30'))  # Configurable vía env

        for query_text, categoria in search_queries:
            if not self._should_continue():
                break

            # Buscar con filtro de fecha
            query_start = time.time()
            pmids = self.fetcher.search_ids(query_text, max_results=500, days_back=days_back)
            query_duration = int(time.time() - query_start)

            # Filtrar PMIDs nuevos (no procesados)
            pmids_nuevos = self.db.filter_unprocessed_pmids(pmids)

            # Tracking de esta query
            all_pmids_by_query[query_text] = {
                'categoria': categoria,
                'pmids_encontrados': len(pmids),
                'pmids_nuevos': len(pmids_nuevos),
                'duracion': query_duration
            }

            # Registrar query execution
            self.db.track_query_execution(
                query_text=query_text,
                categoria=categoria,
                pmids_encontrados=len(pmids),
                pmids_nuevos=len(pmids_nuevos),
                pmids_insertados=0,  # Se actualizará después
                duracion=query_duration
            )

            all_pmids.extend(pmids_nuevos)
            self.stats['fetched'] += len(pmids)

            logger.info(f"📥 Query: '{query_text[:60]}...' → {len(pmids)} encontrados, {len(pmids_nuevos)} nuevos")

            if len(all_pmids) >= self.max_docs:
                break

        # Eliminar duplicados en la lista
        all_pmids = list(set(all_pmids))
        logger.info(f"📊 PMIDs únicos obtenidos: {len(all_pmids)}")

        if not all_pmids:
            logger.warning("⚠️  No hay PMIDs nuevos para procesar")
            return

        # Limitar al máximo de documentos
        all_pmids = all_pmids[:self.max_docs]
        logger.info(f"📊 PMIDs a procesar: {len(all_pmids)}")

        # Procesar en batches
        for i in range(0, len(all_pmids), self.batch_size):
            if not self._should_continue():
                break

            batch_pmids = all_pmids[i:i+self.batch_size]
            logger.info(f"\n{'='*80}")
            logger.info(f"📦 BATCH {i//self.batch_size + 1}: Procesando {len(batch_pmids)} documentos")
            logger.info(f"{'='*80}")

            self._process_batch(batch_pmids)

        # Reporte final
        self._print_final_report()

    def _generate_search_queries(self) -> List[Tuple[str, str]]:
        """
        Genera términos de búsqueda médicos con sistema híbrido.

        Sistema híbrido que combina:
        1. Queries específicas del query_templates.py
        2. Rotación inteligente basada en prioridad de categorías
        3. Randomización para evitar repetición
        4. Balance automático basado en cobertura

        Returns:
            Lista de tuplas (query_text, categoria)
        """
        logger.info("🔄 Generando queries con sistema híbrido...")

        # Obtener prioridades de categorías desde BD
        priorities = self.db.get_category_priorities()
        recently_scraped = set(self.db.get_recently_scraped_queries(days=3))

        logger.info(f"📊 Categorías con prioridad (top 10):")
        for i, p in enumerate(priorities[:10], 1):
            logger.info(f"   {i}. {p['categoria']}: score={p['priority_score']}, docs={p['total_documentos']}, días={p['dias_desde_ultimo_scrape']}")

        queries_with_category = []

        # Si tenemos MEDICAL_QUERIES, usarlo; sino, fallback
        if MEDICAL_QUERIES:
            # Crear pool de queries por categoría
            for category_data in priorities:
                categoria_key = category_data['categoria'].replace(' ', ' ')

                # Buscar en MEDICAL_QUERIES (key matching flexible)
                matching_key = None
                for key in MEDICAL_QUERIES.keys():
                    if key.lower().replace(' ', '') == categoria_key.lower().replace(' ', ''):
                        matching_key = key
                        break

                if not matching_key:
                    # Fallback: usar queries generales
                    queries_with_category.append((categoria_key, categoria_key))
                    continue

                cat_queries = MEDICAL_QUERIES[matching_key]

                # Mezclar specific queries y mesh terms
                available_queries = []

                # Agregar specific queries
                if 'specific' in cat_queries:
                    available_queries.extend(cat_queries['specific'])

                # Agregar MeSH terms (más específicos)
                if 'mesh_terms' in cat_queries:
                    available_queries.extend(cat_queries['mesh_terms'])

                # Agregar queries generales
                if 'general' in cat_queries:
                    available_queries.extend(cat_queries['general'])

                # Filtrar queries recientemente ejecutadas
                available_queries = [q for q in available_queries if q not in recently_scraped]

                # Randomizar y seleccionar según prioridad
                random.shuffle(available_queries)

                # Número de queries por categoría basado en prioridad
                num_queries = max(1, int(category_data['priority_score'] / 10))
                selected = available_queries[:num_queries]

                for query in selected:
                    queries_with_category.append((query, categoria_key))

            # Agregar trending topics (10% del total)
            if TRENDING_TOPICS:
                num_trending = max(5, len(queries_with_category) // 10)
                trending_queries = random.sample(TRENDING_TOPICS, min(num_trending, len(TRENDING_TOPICS)))
                for query in trending_queries:
                    if query not in recently_scraped:
                        queries_with_category.append((query, "General Medicine"))

        else:
            # Fallback: sistema antiguo mejorado
            logger.warning("⚠️  Usando sistema de queries fallback")
            categorias = [
                "oncology", "cardiology", "neurology", "endocrinology",
                "gastroenterology", "pulmonology", "nephrology", "infectious disease",
                "immunology", "hematology", "dermatology", "pediatrics",
                "geriatrics", "obstetrics gynecology", "rheumatology",
                "ophthalmology", "otolaryngology", "psychiatry",
                "traumatology", "urology", "medical genetics", "general medicine"
            ]

            sufijos = [
                "treatment", "therapy", "diagnosis", "prevention",
                "management", "research", "clinical trial", "guidelines"
            ]

            # Randomizar orden de categorías
            random.shuffle(categorias)

            for cat in categorias:
                # Query general
                queries_with_category.append((cat, cat))

                # Randomizar sufijos y seleccionar algunos
                random.shuffle(sufijos)
                for suf in sufijos[:3]:
                    query = f"{cat} {suf}"
                    if query not in recently_scraped:
                        queries_with_category.append((query, cat))

        # Randomizar orden final para evitar sesgo
        random.shuffle(queries_with_category)

        logger.info(f"✅ {len(queries_with_category)} queries generadas con sistema híbrido")
        logger.info(f"🔒 {len(recently_scraped)} queries filtradas (ejecutadas recientemente)")

        return queries_with_category

    def _process_batch(self, pmids: List[str]):
        """Procesa un batch de PMIDs"""
        try:
            # Marcar PMIDs como procesados antes de comenzar
            self.db.mark_pmids_as_processed(pmids, query_origen="batch_processing")

            # 1. Fetch articles
            logger.info("📥 Obteniendo artículos de PubMed...")
            articles = self.fetcher.fetch_articles(pmids)
            if not articles:
                logger.warning("⚠️  No se obtuvieron artículos")
                return

            logger.info(f"✅ {len(articles)} artículos obtenidos")

            # 2. Generar embeddings en batch
            logger.info("🔢 Generando embeddings en batch...")
            texts = [f"{a['titulo']} {a['abstract']}" for a in articles]
            embeddings = self.model_manager.generate_embeddings_batch(texts)
            logger.info(f"✅ {len(embeddings)} embeddings generados")

            # 3. Generar resúmenes en batch (solo para los que tienen abstract)
            logger.info("📝 Generando resúmenes en batch...")
            abstracts = [a['abstract'] for a in articles]
            summaries = []
            if any(abstracts):
                summaries = self.model_manager.generate_summaries_batch(abstracts)
            else:
                summaries = [''] * len(articles)
            logger.info(f"✅ {len([s for s in summaries if s])} resúmenes generados")

            # 4. Categorizar documentos
            logger.info("🏷️  Categorizando documentos...")
            from inferencia.categorizador_mesh import obtener_mejor_categoria_con_mesh
            categorias_ids = []
            for article in articles:
                cat_nombre = obtener_mejor_categoria_con_mesh(
                    article['titulo'],
                    article['abstract'],
                    article['mesh_terms']
                )
                cat_id = self.db.get_categoria_id(cat_nombre)
                categorias_ids.append(cat_id)
            logger.info(f"✅ {len(categorias_ids)} documentos categorizados")

            # 5. Insertar en BD
            logger.info("💾 Insertando en base de datos...")
            self.db.insert_documents_batch(articles, embeddings, summaries, categorias_ids)

            self.stats['processed'] += len(articles)

        except Exception as e:
            logger.error(f"❌ Error procesando batch: {e}")
            self.stats['errors'] += 1

    def _print_final_report(self):
        """Imprime reporte final"""
        elapsed = time.time() - self.stats['start_time']
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)

        logger.info("\n" + "="*80)
        logger.info("📊 REPORTE FINAL")
        logger.info("="*80)
        logger.info(f"⏱️  Tiempo total: {hours}h {minutes}m")
        logger.info(f"📥 PMIDs obtenidos: {self.stats['fetched']}")
        logger.info(f"📝 Documentos procesados: {self.stats['processed']}")
        logger.info(f"❌ Errores: {self.stats['errors']}")
        logger.info(f"⚡ Velocidad: {self.stats['processed']/(elapsed/3600):.0f} docs/hora")
        logger.info("="*80)


# =====================================================
# Main
# =====================================================
def main():
    parser = argparse.ArgumentParser(description='Scraper masivo de PubMed')
    parser.add_argument('--max-docs', type=int, default=10000,
                       help='Máximo número de documentos a procesar')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Tamaño de batch para procesamiento')
    parser.add_argument('--start-hour', type=int, default=2,
                       help='Hora de inicio permitida (0-23)')
    parser.add_argument('--stop-hour', type=int, default=7,
                       help='Hora de fin permitida (0-23)')

    args = parser.parse_args()

    scraper = MassiveScraper(
        max_docs=args.max_docs,
        batch_size=args.batch_size,
        start_hour=args.start_hour,
        stop_hour=args.stop_hour
    )

    scraper.run()


if __name__ == "__main__":
    main()
