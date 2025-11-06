#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migración: Regenerar Embeddings sin Normalización
============================================================

Este script regenera todos los embeddings de documentos existentes en la base de datos
utilizando el parámetro normalize_embeddings=False para mejorar la discriminación semántica.

PROBLEMA ANTERIOR:
- Los embeddings normalizados causaban que todos los documentos tuvieran scores muy similares (0.93-0.94)
- Esto resultaba en búsquedas poco discriminatorias donde casi todo parecía relevante

SOLUCIÓN:
- Regenerar embeddings SIN normalización (normalize_embeddings=False)
- Esto permite mejor diferenciación entre documentos relevantes e irrelevantes
- Los scores ahora serán más informativos (rango más amplio)

ADVERTENCIA:
- Este script MODIFICARÁ todos los embeddings en la base de datos
- Es IRREVERSIBLE sin un backup
- Se recomienda hacer backup de la BD antes de ejecutar

Uso:
    python scripts/regenerate_embeddings.py --batch-size 100 [--dry-run]
"""

import sys
import os
import logging
import argparse
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import time

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de base de datos (usar variables de entorno)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'cliniccloud'),
    'user': os.getenv('DB_USER', 'cliniccloud'),
    'password': os.getenv('DB_PASSWORD', 'changeme')
}


class EmbeddingRegenerator:
    """Regenerador de embeddings para documentos existentes"""

    def __init__(self, batch_size=100, dry_run=False):
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.model = None
        self.conn = None
        self.cursor = None

    def connect_db(self):
        """Conectar a la base de datos PostgreSQL"""
        try:
            logger.info(f"Conectando a la base de datos: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            logger.info("✅ Conexión a la base de datos establecida")
        except Exception as e:
            logger.error(f"❌ Error al conectar a la base de datos: {e}")
            sys.exit(1)

    def load_model(self):
        """Cargar el modelo de embeddings"""
        try:
            logger.info("🔄 Cargando modelo S-PubMedBert-MS-MARCO...")
            self.model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
            logger.info("✅ Modelo cargado correctamente")
        except Exception as e:
            logger.error(f"❌ Error al cargar el modelo: {e}")
            sys.exit(1)

    def get_document_count(self):
        """Obtener el número total de documentos"""
        self.cursor.execute("SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL")
        count = self.cursor.fetchone()[0]
        logger.info(f"📊 Total de documentos con embeddings: {count}")
        return count

    def fetch_documents_batch(self, offset):
        """Obtener un lote de documentos"""
        query = """
            SELECT d.id, d.titulo, r.texto_resumen
            FROM documento d
            LEFT JOIN resumen r ON d.id = r.id_documento
            WHERE d.contenido_vectorizado IS NOT NULL
            ORDER BY d.id
            LIMIT %s OFFSET %s
        """
        self.cursor.execute(query, (self.batch_size, offset))
        return self.cursor.fetchall()

    def generate_embedding(self, texto):
        """Generar embedding sin normalización"""
        try:
            # IMPORTANTE: normalize_embeddings=False para vectores no normalizados
            embedding = self.model.encode(texto, normalize_embeddings=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error al generar embedding: {e}")
            return None

    def update_embeddings_batch(self, updates):
        """Actualizar un lote de embeddings en la base de datos"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Se actualizarían {len(updates)} documentos")
            return

        try:
            query = "UPDATE documento SET contenido_vectorizado = %s WHERE id = %s"
            execute_values(
                self.cursor,
                query,
                [(embedding, doc_id) for doc_id, embedding in updates],
                template="(%s, %s)"
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"❌ Error al actualizar embeddings: {e}")
            self.conn.rollback()
            raise

    def run(self):
        """Ejecutar el proceso de regeneración"""
        logger.info("="*80)
        logger.info("🚀 INICIANDO REGENERACIÓN DE EMBEDDINGS")
        logger.info("="*80)

        if self.dry_run:
            logger.warning("⚠️  MODO DRY RUN: No se realizarán cambios en la base de datos")

        # Conectar y cargar modelo
        self.connect_db()
        self.load_model()

        # Obtener total de documentos
        total_docs = self.get_document_count()

        if total_docs == 0:
            logger.warning("⚠️  No hay documentos con embeddings para regenerar")
            return

        # Procesar en lotes
        processed = 0
        errors = 0
        start_time = time.time()

        with tqdm(total=total_docs, desc="Regenerando embeddings") as pbar:
            offset = 0
            while offset < total_docs:
                # Obtener lote de documentos
                batch = self.fetch_documents_batch(offset)

                if not batch:
                    break

                # Generar nuevos embeddings
                updates = []
                for doc_id, titulo, resumen in batch:
                    # Combinar título y resumen (igual que en el scraper)
                    texto = f"{titulo} {resumen or ''}"

                    embedding = self.generate_embedding(texto)

                    if embedding:
                        updates.append((doc_id, embedding))
                        processed += 1
                    else:
                        errors += 1
                        logger.warning(f"⚠️  Error generando embedding para documento ID {doc_id}")

                # Actualizar en base de datos
                if updates:
                    self.update_embeddings_batch(updates)

                # Actualizar progreso
                pbar.update(len(batch))
                offset += self.batch_size

        # Resumen final
        elapsed = time.time() - start_time
        logger.info("="*80)
        logger.info("✅ REGENERACIÓN COMPLETADA")
        logger.info(f"📊 Documentos procesados: {processed}/{total_docs}")
        logger.info(f"❌ Errores: {errors}")
        logger.info(f"⏱️  Tiempo total: {elapsed:.2f} segundos")
        logger.info(f"⚡ Velocidad: {processed/elapsed:.2f} docs/seg")
        logger.info("="*80)

        # Verificar resultados
        if not self.dry_run:
            self.verify_results()

    def verify_results(self):
        """Verificar que los nuevos embeddings están correctos"""
        logger.info("🔍 Verificando resultados...")

        # Verificar magnitud de vectores (NO deben estar normalizados)
        query = """
            SELECT
                id,
                (contenido_vectorizado <#> contenido_vectorizado) as self_inner_product
            FROM documento
            WHERE contenido_vectorizado IS NOT NULL
            LIMIT 10
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        logger.info("📊 Muestra de magnitudes (inner product):")
        for doc_id, inner_product in results:
            logger.info(f"  Doc {doc_id}: {inner_product:.2f}")

        # Los vectores NO normalizados deben tener inner product mucho mayor (en valor absoluto)
        avg_magnitude = sum(abs(r[1]) for r in results) / len(results)

        if avg_magnitude < 500:
            logger.warning(f"⚠️  ADVERTENCIA: Magnitud promedio baja ({avg_magnitude:.2f}). Los vectores podrían estar normalizados.")
        else:
            logger.info(f"✅ Magnitud promedio: {avg_magnitude:.2f} (vectores NO normalizados)")

    def close(self):
        """Cerrar conexiones"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔒 Conexión cerrada")


def main():
    parser = argparse.ArgumentParser(
        description="Regenerar embeddings de documentos sin normalización"
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Tamaño del lote para procesamiento (default: 100)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Ejecutar sin realizar cambios en la BD (prueba)'
    )

    args = parser.parse_args()

    # Confirmar acción (si no es dry run)
    if not args.dry_run:
        logger.warning("⚠️  ADVERTENCIA: Este script MODIFICARÁ todos los embeddings en la base de datos")
        logger.warning("⚠️  Es IRREVERSIBLE sin un backup")
        response = input("¿Desea continuar? (escriba 'SI' para confirmar): ")

        if response != 'SI':
            logger.info("❌ Operación cancelada por el usuario")
            sys.exit(0)

    # Ejecutar regeneración
    regenerator = EmbeddingRegenerator(
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )

    try:
        regenerator.run()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        regenerator.close()


if __name__ == "__main__":
    main()
