#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la extracción de fechas desde PubMed
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper_masivo import PubMedFetcher
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_fecha_extraction():
    """Prueba la extracción de fechas con PMIDs conocidos"""

    # PMIDs de prueba (de los documentos que están en tu BD sin fecha)
    test_pmids = [
        '41064809',  # El que revisamos en el XML
        '41140349',
        '41194451',
        '41158418',
        '41133763'
    ]

    logger.info("="*80)
    logger.info("PRUEBA DE EXTRACCIÓN DE FECHAS")
    logger.info("="*80)

    fetcher = PubMedFetcher()

    # Obtener artículos
    logger.info(f"Obteniendo {len(test_pmids)} artículos de prueba...")
    articles = fetcher.fetch_articles(test_pmids)

    logger.info(f"\n{'='*80}")
    logger.info("RESULTADOS")
    logger.info(f"{'='*80}\n")

    # Verificar fechas extraídas
    fechas_ok = 0
    fechas_faltantes = 0

    for article in articles:
        pmid = article.get('pmid', 'N/A')
        titulo = article.get('titulo', 'N/A')[:60]
        fecha = article.get('fecha_publicacion', None)

        if fecha:
            logger.info(f"✅ PMID {pmid}: {fecha}")
            logger.info(f"   Título: {titulo}...")
            fechas_ok += 1
        else:
            logger.warning(f"❌ PMID {pmid}: SIN FECHA")
            logger.warning(f"   Título: {titulo}...")
            fechas_faltantes += 1

        logger.info("")

    logger.info(f"{'='*80}")
    logger.info(f"RESUMEN: {fechas_ok}/{len(articles)} artículos con fecha")
    logger.info(f"         {fechas_faltantes}/{len(articles)} artículos sin fecha")
    logger.info(f"{'='*80}")

    if fechas_faltantes == 0:
        logger.info("🎉 ¡TODAS LAS FECHAS SE EXTRAJERON CORRECTAMENTE!")
        return 0
    else:
        logger.error("⚠️  Algunos artículos aún no tienen fecha")
        return 1

if __name__ == "__main__":
    exit_code = test_fecha_extraction()
    sys.exit(exit_code)
