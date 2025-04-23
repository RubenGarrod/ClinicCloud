import os
import time
import logging
import schedule
import psycopg2
import sys
import signal

# Instalar SelectReactor antes de importar otros módulos de Twisted
from twisted.internet import selectreactor
selectreactor.install()

from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from clinic_scraper.spiders.pubmed_spider import PubmedSpider
from scrapy.utils.ossignal import install_shutdown_handlers

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def wait_for_database(max_attempts=30, delay=2):
    """Espera a que la base de datos esté disponible"""
    for attempt in range(max_attempts):
        try:
            conn = psycopg2.connect(
                dbname="cliniccloud",
                user="admin",
                password="admin123",
                host="db"
            )
            conn.close()
            logger.info("Conexión a la base de datos establecida.")
            return True
        except Exception as e:
            logger.info(f"Esperando a que la base de datos esté disponible... Intento {attempt + 1}")
            time.sleep(delay)
    
    logger.error("No se pudo conectar a la base de datos.")
    return False

def run_spider():
    """Ejecuta el spider de PubMed"""
    logger.info("Iniciando proceso de scraping...")
    
    # Lista de términos de búsqueda médica
    search_terms = [
        "diabetes treatment",
        "cancer therapy",
        "cardiovascular disease",
        "antibiotic resistance",
        "neurological disorders"
    ]
    
    # Configuración personalizada de Scrapy
    settings = get_project_settings()
    settings.set('ROBOTSTXT_OBEY', False)
    settings.set('REQUEST_FINGERPRINTER_IMPLEMENTATION', '2.7')
    settings.set('FEEDS', {
        'output.json': {
            'format': 'json',
            'mode': 'append',  # Cambiar a modo append
            'overwrite': False
        }
    })
    
    # Crear el proceso de Scrapy
    process = CrawlerProcess(settings)
    
    # Programar múltiples spiders con diferentes términos de búsqueda
    # CAMBIO CLAVE: Pasar la CLASE del spider, no una instancia
    for term in search_terms:
        process.crawl(PubmedSpider, query=term, max_results=10)
    
    # Manejar errores y finalización
    def close_spider(result):
        logger.info("Scraping completado.")
        reactor.stop()
    
    # Iniciar y manejar el proceso
    try:
        d = process.join()
        d.addBoth(close_spider)
        reactor.run()
        
        logger.info("Proceso de scraping completado exitosamente")
    except Exception as e:
        logger.error(f"Error durante el proceso de scraping: {e}")
        import traceback
        traceback.print_exc()
        reactor.stop()

def main():
    # Configurar señales de sistema
    signal.signal(signal.SIGINT, lambda s, f: reactor.stop())
    signal.signal(signal.SIGTERM, lambda s, f: reactor.stop())
    
    # Esperar a que la base de datos esté disponible
    if not wait_for_database():
        logger.error("No se pudo conectar a la base de datos. Saliendo...")
        sys.exit(1)
    
    # Ejecutar el spider inmediatamente al iniciar
    run_spider()
    
    # Programar ejecuciones periódicas (una vez al día)
    schedule.every(24).hours.do(run_spider)
    logger.info("Programador configurado para ejecutar el scraper cada 24 horas")
    
    # Mantener el contenedor en ejecución
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Deteniendo el scraper...")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()