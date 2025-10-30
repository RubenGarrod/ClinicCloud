#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Continuo para ClinicCloud
==================================

Ejecuta el scraper masivo en modo continuo mientras el contenedor esté encendido.
Se puede controlar con docker-compose up/down programados con cron.

Características:
- Carga modelos ML una sola vez al inicio (S-PubMedBert + BART)
- Ejecuta scraper_masivo.py en loop con pausas configurables
- Respeta horario de ejecución (START_HOUR - STOP_HOUR)
- Se puede detener con docker-compose down

Variables de entorno:
- SCRAPER_MAX_DOCS: Documentos por ejecución (default: 1000)
- SCRAPER_BATCH_SIZE: Documentos por batch (default: 25)
- SCRAPER_START_HOUR: Hora de inicio 0-23 (default: 0)
- SCRAPER_STOP_HOUR: Hora de parada 0-23 (default: 23)
- SCRAPER_LOOP_DELAY: Segundos entre ejecuciones (default: 1800 = 30min)

Uso:
    docker-compose --profile scraper up -d scraper    # Inicia en background
    docker-compose logs -f scraper                    # Ver logs en tiempo real
    docker-compose down scraper                       # Detener

Cron para programar (ejemplo: ejecutar de 22h a 8h):
    0 22 * * * cd /root/ClinicCloud && docker-compose --profile scraper up -d scraper
    0 8 * * * cd /root/ClinicCloud && docker-compose down scraper
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
# =============================================================================

MAX_DOCS = int(os.getenv('SCRAPER_MAX_DOCS', '1000'))
BATCH_SIZE = int(os.getenv('SCRAPER_BATCH_SIZE', '25'))
START_HOUR = int(os.getenv('SCRAPER_START_HOUR', '0'))
STOP_HOUR = int(os.getenv('SCRAPER_STOP_HOUR', '23'))
LOOP_DELAY = int(os.getenv('SCRAPER_LOOP_DELAY', '1800'))  # 30 minutos

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def esta_en_horario():
    """Verifica si la hora actual está dentro del horario de ejecución"""
    hora_actual = datetime.now().hour

    if START_HOUR <= STOP_HOUR:
        # Rango normal: ej. 8-22 (8am a 10pm)
        return START_HOUR <= hora_actual <= STOP_HOUR
    else:
        # Rango que cruza medianoche: ej. 22-8 (10pm a 8am)
        return hora_actual >= START_HOUR or hora_actual <= STOP_HOUR


def ejecutar_scraper():
    """Ejecuta el scraper masivo con los parámetros configurados"""
    try:
        logger.info("="*80)
        logger.info("🚀 INICIANDO EJECUCIÓN DEL SCRAPER MASIVO")
        logger.info("="*80)
        logger.info(f"   Max documentos: {MAX_DOCS}")
        logger.info(f"   Batch size: {BATCH_SIZE}")
        logger.info(f"   Horario: {START_HOUR}:00 - {STOP_HOUR}:00")
        logger.info("="*80)

        # Ejecutar scraper_masivo.py
        cmd = [
            'python',
            'scraper_masivo.py',
            '--max-docs', str(MAX_DOCS),
            '--batch-size', str(BATCH_SIZE),
            '--start-hour', str(START_HOUR),
            '--stop-hour', str(STOP_HOUR)
        ]

        resultado = subprocess.run(
            cmd,
            cwd='/app',
            capture_output=False,  # Mostrar output en tiempo real
            text=True
        )

        if resultado.returncode == 0:
            logger.info("✅ Scraper completado exitosamente")
        else:
            logger.error(f"❌ Scraper terminó con código de error: {resultado.returncode}")

        return resultado.returncode

    except Exception as e:
        logger.error(f"❌ Error al ejecutar scraper: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


def main():
    """Loop principal del scraper continuo"""
    logger.info("="*80)
    logger.info("🤖 SCRAPER CONTINUO DE CLINICCLOUD")
    logger.info("="*80)
    logger.info(f"📋 Configuración:")
    logger.info(f"   - Max documentos por ejecución: {MAX_DOCS}")
    logger.info(f"   - Batch size: {BATCH_SIZE}")
    logger.info(f"   - Horario de ejecución: {START_HOUR}:00 - {STOP_HOUR}:00")
    logger.info(f"   - Pausa entre ejecuciones: {LOOP_DELAY}s ({LOOP_DELAY/60:.1f} min)")
    logger.info("="*80)
    logger.info("💡 Para detener: docker-compose down scraper")
    logger.info("="*80)

    ejecucion_count = 0

    while True:
        try:
            ejecucion_count += 1
            logger.info(f"\n📊 Ejecución #{ejecucion_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Verificar horario
            if not esta_en_horario():
                hora_actual = datetime.now().hour
                logger.info(f"⏸️  Fuera de horario (actual: {hora_actual}h, permitido: {START_HOUR}h-{STOP_HOUR}h)")
                logger.info(f"   Esperando {LOOP_DELAY}s antes de verificar nuevamente...")
                time.sleep(LOOP_DELAY)
                continue

            # Ejecutar scraper
            ejecutar_scraper()

            # Pausa antes de la siguiente ejecución
            logger.info("="*80)
            logger.info(f"⏳ Esperando {LOOP_DELAY}s ({LOOP_DELAY/60:.1f} min) antes de la siguiente ejecución...")
            logger.info(f"   Próxima ejecución aproximada: {datetime.fromtimestamp(time.time() + LOOP_DELAY).strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80)

            time.sleep(LOOP_DELAY)

        except KeyboardInterrupt:
            logger.info("\n🛑 Interrupción recibida. Deteniendo scraper continuo...")
            break
        except Exception as e:
            logger.error(f"❌ Error en el loop principal: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.info(f"⏳ Esperando {LOOP_DELAY}s antes de reintentar...")
            time.sleep(LOOP_DELAY)

    logger.info("="*80)
    logger.info("👋 Scraper continuo detenido")
    logger.info("="*80)


if __name__ == "__main__":
    main()
