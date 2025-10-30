# Scrapy settings for clinic_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "clinic_scraper"

SPIDER_MODULES = ["clinic_scraper.spiders"]
NEWSPIDER_MODULE = "clinic_scraper.spiders"

# Config para la BD del sistema
import os
PG_HOST = os.getenv('DB_HOST', 'db')  # nombre del servicio en docker-compose
PG_PORT = os.getenv('DB_PORT', '5432') # puerto de PostgreSQL
PG_DATABASE = os.getenv('DB_NAME', 'cliniccloud') # nombre de la base de datos
PG_USER = os.getenv('DB_USER', 'admin') # nombre de usuario
PG_PASSWORD = os.getenv('DB_PASSWORD', 'admin123') # contraseña

ITEM_PIPELINES = {
    #'clinic_scraper.pipelines.PrintPipeline': 300,
    'clinic_scraper.pipelines.PostgreSQLPipeline': 300,
}

# Configuraciones de Scrapy
USER_AGENT = 'ClinicCloud/1.0 (https://github.com/rubengarrod/cliniccloud)'
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1 # Retraso entre peticiones
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 1
RETRY_TIMES = 5
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]
LOG_LEVEL = 'DEBUG'  

# Configuraciones para JSON feed export (para pruebas locales)
#FEED_FORMAT = 'json'
#FEED_URI = 'output.json'
#FEED_EXPORT_ENCODING = 'utf-8'
#FEED_EXPORT_INDENT = 2
