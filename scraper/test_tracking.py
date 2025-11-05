#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de tracking de PMIDs
Verifica que el filtrado y tracking funcionen correctamente
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_tracking():
    """Prueba el sistema de tracking"""
    from scraper_masivo import DatabaseManager, PubMedFetcher

    logger.info("="*80)
    logger.info("🧪 TEST: Sistema de Tracking de PMIDs")
    logger.info("="*80)

    # 1. Conectar a BD
    logger.info("\n1️⃣ Conectando a base de datos...")
    db = DatabaseManager()
    logger.info("✅ Conectado")

    # 2. Test de fetcher con fechas
    logger.info("\n2️⃣ Probando búsqueda con filtro de fecha (últimos 7 días)...")
    fetcher = PubMedFetcher()
    pmids = fetcher.search_ids("cardiology", max_results=10, days_back=7)
    logger.info(f"✅ Obtenidos {len(pmids)} PMIDs recientes")

    if not pmids:
        logger.warning("⚠️  No se encontraron PMIDs, usando PMIDs de prueba")
        pmids = ["12345678", "87654321", "11111111"]

    # 3. Test de filtrado (primera vez)
    logger.info("\n3️⃣ Filtrando PMIDs (primera ejecución)...")
    no_procesados = db.filter_unprocessed_pmids(pmids)
    logger.info(f"✅ PMIDs no procesados: {len(no_procesados)}/{len(pmids)}")

    # 4. Marcar como procesados
    logger.info("\n4️⃣ Marcando PMIDs como procesados...")
    db.mark_pmids_as_processed(pmids[:5], query_origen="test_query")
    logger.info(f"✅ {len(pmids[:5])} PMIDs marcados")

    # 5. Test de filtrado (segunda vez - deben estar filtrados)
    logger.info("\n5️⃣ Filtrando PMIDs (segunda ejecución)...")
    no_procesados_2 = db.filter_unprocessed_pmids(pmids)
    logger.info(f"✅ PMIDs no procesados: {len(no_procesados_2)}/{len(pmids)}")

    # Verificación
    if len(no_procesados_2) < len(no_procesados):
        logger.info("✅ ÉXITO: El tracking está funcionando correctamente")
        logger.info(f"   - Primera ejecución: {len(no_procesados)} PMIDs nuevos")
        logger.info(f"   - Segunda ejecución: {len(no_procesados_2)} PMIDs nuevos")
        logger.info(f"   - Filtrados: {len(no_procesados) - len(no_procesados_2)} PMIDs")
    else:
        logger.error("❌ ERROR: El tracking no está filtrando correctamente")

    # 6. Test de limpieza
    logger.info("\n6️⃣ Probando limpieza de tracking...")
    db.cleanup_old_tracking(days=90)
    logger.info("✅ Limpieza ejecutada")

    # Cerrar
    db.close()

    logger.info("\n" + "="*80)
    logger.info("✅ Test completado")
    logger.info("="*80)

if __name__ == "__main__":
    try:
        test_tracking()
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
