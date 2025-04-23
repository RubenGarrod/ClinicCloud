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

# Configuraciones de la base de datos PostgreSQL
PG_HOST = 'db'  # Nombre del servicio en docker-compose
PG_PORT = '5432'
PG_DATABASE = 'cliniccloud'
PG_USER = 'admin'
PG_PASSWORD = 'admin123'

# Activar el pipeline - Comentar PostgreSQLPipeline y usar PrintPipeline para depuración
ITEM_PIPELINES = {
    #'clinic_scraper.pipelines.PrintPipeline': 300,
    'clinic_scraper.pipelines.PostgreSQLPipeline': 300,
}

# Configuraciones adicionales
USER_AGENT = 'ClinicCloud/1.0 (https://github.com/rubengarrod/clinic-cloud)'
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1  # Reducir delay para pruebas

# Configuraciones para optimización
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 1
RETRY_TIMES = 5
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]
LOG_LEVEL = 'DEBUG'  # Usar DEBUG para ver más información

# Configuraciones para JSON feed export
FEED_FORMAT = 'json'
FEED_URI = 'output.json'
FEED_EXPORT_ENCODING = 'utf-8'
FEED_EXPORT_INDENT = 2
