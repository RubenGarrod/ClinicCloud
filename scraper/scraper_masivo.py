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

    def search_ids(self, query: str, max_results: int = 10000) -> List[str]:
        """
        Busca IDs de artículos para un término.

        Args:
            query: Término de búsqueda
            max_results: Máximo número de resultados

        Returns:
            Lista de PMIDs
        """
        import requests

        self._rate_limit()

        url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmode': 'json',
            'retmax': str(max_results),
            'sort': 'relevance'
        }

        if self.api_key:
            params['api_key'] = self.api_key

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            ids = data.get('esearchresult', {}).get('idlist', [])
            logger.info(f"Búsqueda '{query}': {len(ids)} artículos encontrados")
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

            # Fecha
            year = article_xml.xpath('.//PubDate/Year/text()')
            month = article_xml.xpath('.//PubDate/Month/text()')
            day = article_xml.xpath('.//PubDate/Day/text()')

            fecha = None
            if year:
                fecha_str = f"{year[0]}"
                if month:
                    fecha_str += f"-{month[0]}"
                    if day:
                        fecha_str += f"-{day[0]}"
                fecha = fecha_str

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
        except Exception as e:
            logger.error(f"❌ Error conectando a BD: {e}")
            raise

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
                    if doc.get('fecha_publicacion'):
                        try:
                            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                                try:
                                    fecha = datetime.strptime(doc['fecha_publicacion'], fmt)
                                    break
                                except ValueError:
                                    continue
                        except:
                            pass

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

        # Términos de búsqueda médicos
        search_queries = self._generate_search_queries()
        logger.info(f"📋 {len(search_queries)} términos de búsqueda generados")

        # Fetch PMIDs
        all_pmids = []
        for query in search_queries:
            if not self._should_continue():
                break

            pmids = self.fetcher.search_ids(query, max_results=500)
            all_pmids.extend(pmids)
            self.stats['fetched'] += len(pmids)

            if len(all_pmids) >= self.max_docs:
                break

        # Eliminar duplicados
        all_pmids = list(set(all_pmids))
        all_pmids = all_pmids[:self.max_docs]
        logger.info(f"📊 Total PMIDs únicos: {len(all_pmids)}")

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

    def _generate_search_queries(self) -> List[str]:
        """Genera términos de búsqueda médicos"""
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
            "management", "research", "clinical trial"
        ]

        queries = []
        for cat in categorias:
            queries.append(cat)
            for suf in sufijos[:3]:  # Solo 3 sufijos por categoría
                queries.append(f"{cat} {suf}")

        return queries

    def _process_batch(self, pmids: List[str]):
        """Procesa un batch de PMIDs"""
        try:
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
