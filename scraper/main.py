# -*- coding: utf-8 -*-
"""
ClinicCloud Scraper - PubMed Data Collection Service

Copyright (C) 2025 Rubén García Rodríguez

This file is part of ClinicCloud.

ClinicCloud is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ClinicCloud is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

---

Script principal para ejecutar el scraper de PubMed y programar su ejecución periódica.
Este script se encarga de conectarse a la base de datos, obtener las categorías médicas,
generar términos de búsqueda y ejecutar el spider de Scrapy para obtener artículos médicos.
"""
import os
import time
import logging
import schedule
import psycopg2
import sys
import signal
import random
from twisted.internet import selectreactor
selectreactor.install()

from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from clinic_scraper.spiders.pubmed_spider import PubmedSpider
from scrapy.utils.ossignal import install_shutdown_handlers

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
                dbname=os.getenv('POSTGRES_DB', 'cliniccloud'),
                user=os.getenv('POSTGRES_USER', 'cliniccloud'),
                password=os.getenv('POSTGRES_PASSWORD', ''),
                host=os.getenv('DB_HOST', 'db'),
                port=os.getenv('DB_PORT', '5432')
            )
            conn.close()
            logger.info("Conexión a la base de datos establecida.")
            return True
        except Exception as e:
            logger.info(f"Esperando a que la base de datos esté disponible... Intento {attempt + 1}")
            time.sleep(delay)

    logger.error("No se pudo conectar a la base de datos.")
    return False

def obtener_categorias_medicas():
    """Obtiene las categorías médicas de la base de datos"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'cliniccloud'),
            user=os.getenv('POSTGRES_USER', 'cliniccloud'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            host=os.getenv('DB_HOST', 'db'),
            port=os.getenv('DB_PORT', '5432')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM categoria")
        categorias = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return categorias
    except Exception as e:
        logger.error(f"Error al obtener categorías: {e}")
        # Si falla la conexión a la BD, usar categorías predefinidas
        return [
            "Oncología", "Cardiología", "Neurología", "Endocrinología",
            "Gastroenterología", "Neumología", "Nefrología", "Infectología",
            "Inmunología", "Hematología", "Dermatología", "Pediatría",
            "Geriatría", "Obstetricia y Ginecología", "Reumatología",
            "Oftalmología", "Otorrinolaringología", "Psiquiatría",
            "Traumatología", "Urología", "Genética Médica", "Medicina General"
        ]

def traducir_categoria(categoria):
    """Traduce los nombres de categorías médicas de español a inglés para PubMed"""
    traducciones = {
        "Oncología": "oncology",
        "Cardiología": "cardiology",
        "Neurología": "neurology",
        "Endocrinología": "endocrinology",
        "Gastroenterología": "gastroenterology",
        "Neumología": "pulmonology",
        "Nefrología": "nephrology",
        "Infectología": "infectious disease",
        "Inmunología": "immunology",
        "Hematología": "hematology",
        "Dermatología": "dermatology",
        "Pediatría": "pediatrics",
        "Geriatría": "geriatrics",
        "Obstetricia y Ginecología": "obstetrics gynecology",
        "Reumatología": "rheumatology",
        "Oftalmología": "ophthalmology",
        "Otorrinolaringología": "otolaryngology",
        "Psiquiatría": "psychiatry",
        "Traumatología": "traumatology",
        "Urología": "urology",
        "Genética Médica": "medical genetics",
        "Medicina General": "general medicine"
    }
    
    return traducciones.get(categoria, categoria)

def generar_terminos_busqueda(categorias):
    """Genera términos de búsqueda basados en las categorías médicas"""
    terminos_busqueda = []
    
    # Palabras comunes para combinar como sufijos con las categorías
    sufijos_medicos = [
        "treatment", "therapy", "advances", "research", 
        "diagnosis", "prevention", "management"
    ]
    
    # Generar combinaciones de categorías y términos
    for categoria in categorias:
        # Traducir nombre de categoría al inglés para PubMed
        categoria_ingles = traducir_categoria(categoria)
        terminos_busqueda.append(categoria_ingles)
        # Agregar los sufijos a la categoria 
        for sufijo in sufijos_medicos:
            terminos_busqueda.append(f"{categoria_ingles} {sufijo}")
    
    # Limitar a un número razonable para no sobrecargar PubMed
    if len(terminos_busqueda) > 30:
        terminos_busqueda = random.sample(terminos_busqueda, 30)
    
    return terminos_busqueda

def programar_spider(process, termino, retraso=0):
    """Programa un spider individual con el término de búsqueda dado"""
    if retraso > 0:
        logger.info(f"Programando spider para '{termino}' con retraso de {retraso}s")
        reactor.callLater(retraso, iniciar_spider, process, termino)
    else:
        iniciar_spider(process, termino)

def iniciar_spider(process, termino, max_results=10):
    """Inicia un spider con el término de búsqueda especificado"""
    process.crawl(PubmedSpider, query=termino, max_results=max_results)
    logger.info(f"Spider iniciado para el término: {termino} (max: {max_results} docs)")

def run_spider(max_docs_per_term=10):
    """Ejecuta el spider de PubMed con términos de búsqueda dinámicos"""
    logger.info("Iniciando proceso de scraping...")
    
    # Obtener categorías médicas de la base de datos
    # Si no se puede conectar a la base de datos, usamos las categorías predefinidas
    categorias = obtener_categorias_medicas()
    terminos_busqueda = generar_terminos_busqueda(categorias)
    
    logger.info(f"Se generaron {len(terminos_busqueda)} términos de búsqueda")
    
    # Configuración del proceso de Scrapy
    settings = get_project_settings()
    settings.set('ROBOTSTXT_OBEY', False)
    settings.set('REQUEST_FINGERPRINTER_IMPLEMENTATION', '2.7')
    
    # podemos borrar ya la config para el output.json que ya no es necesaria
    if 'FEEDS' in settings:
        settings.pop('FEEDS')
    
    # Crear el proceso de Scrapy
    process = CrawlerProcess(settings)
    
    # Programar múltiples spiders con diferentes términos de búsqueda, distribuyendo la carga
    for i, termino in enumerate(terminos_busqueda):
        # Escalonar el inicio de los spiders para evitar alcanzar límites de tasa
        retraso = i * 60  # 1 minuto entre spiders
        programar_spider(process, termino, retraso)
    
    def close_spider(result):
        """Metodo para cerrar el reactor al finalizar el scraping"""
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
    
    # Esperar a la BBDD
    if not wait_for_database():
        logger.error("No se pudo conectar a la base de datos. Saliendo...")
        sys.exit(1)
    
    # Ejecutar el spider inmediatamente al iniciar
    run_spider()
    
    # Programar ejecuciones periódicas
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