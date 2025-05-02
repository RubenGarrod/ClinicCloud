import scrapy
import json
import time
from datetime import datetime
from scrapy.exceptions import CloseSpider
import os

class PubmedSpider(scrapy.Spider):
    name = 'pubmed'
    allowed_domains = ['pubmed.ncbi.nlm.nih.gov', 'eutils.ncbi.nlm.nih.gov']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # Añade un retraso entre solicitudes
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  # Una solicitud a la vez
        'RETRY_TIMES': 5,  # Número de reintentos
        'RETRY_HTTP_CODES': [429, 500, 502, 503, 504],  # Códigos de error a reintentar
    }
    
    def __init__(self, query='cancer treatment', max_results=10, *args, **kwargs):
        super(PubmedSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.max_results = int(max_results)
        self.base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        
        # Intentar obtener la clave API de las variables de entorno
        self.api_key = os.environ.get('NCBI_API_KEY', '')
        if self.api_key:
            self.logger.info("Clave API de NCBI configurada correctamente")
        else:
            self.logger.warning("No se encontró clave API de NCBI. Se usarán límites estándar")
    
    def start_requests(self):
        # Paso 1: Buscar IDs de artículos usando esearch
        esearch_url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': self.query,
            'retmode': 'json',
            'retmax': str(self.max_results)
        }
        
        # Añadir API key si está disponible
        if self.api_key:
            params['api_key'] = self.api_key
        
        self.logger.info(f"Iniciando búsqueda para: {self.query}")
        
        yield scrapy.FormRequest(
            url=esearch_url, 
            formdata=params, 
            callback=self.parse_search,
            errback=self.handle_error,
            meta={'dont_retry': False}  # Permitir reintentos para esta solicitud
        )
    
    def parse_search(self, response):
        try:
            # Extraer los ids de los resultados de la query
            data = json.loads(response.body)
            id_list = data.get('esearchresult', {}).get('idlist', [])
            
            if not id_list:
                self.logger.warning(f"No se han encontrado artículos para la query: {self.query}")
                return
            
            self.logger.info(f"Se encontraron {len(id_list)} artículos para: {self.query}")
            
            # 2: Obtener detalles de los artículos usando efetch
            ids = ','.join(id_list)
            efetch_url = f"{self.base_url}/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ids,
                'retmode': 'xml'
            }
            
            # Añadir API key si está disponible
            if self.api_key:
                params['api_key'] = self.api_key

            yield scrapy.FormRequest(
                url=efetch_url, 
                formdata=params, 
                callback=self.parse_articles,
                errback=self.handle_error,
                meta={'dont_retry': False}  # Permitir reintentos
            )
        except Exception as e:
            self.logger.error(f"Error parseando los resultados de la búsqueda: {e}")
            raise CloseSpider(f"Parse error: {e}")
    
    def parse_articles(self, response):
        """ Método para extraer los datos de los XML de los artículos"""
        articles = response.xpath('//PubmedArticle')
        
        self.logger.info(f"Procesando {len(articles)} artículos")
        
        for article in articles:
            try:
                # Extraer titulo
                title = article.xpath('.//ArticleTitle/text()').get('')
                
                # Extraer autores
                authors = []
                author_list = article.xpath('.//Author')
                for author in author_list:
                    last_name = author.xpath('./LastName/text()').get('')
                    first_name = author.xpath('./ForeName/text()').get('')
                    if last_name and first_name:
                        authors.append(f"{last_name} {first_name}")
                
                # Extraer fecha de publicación con manejo mejorado
                year = article.xpath('.//PubDate/Year/text()').get('')
                month = article.xpath('.//PubDate/Month/text()').get('01')
                day = article.xpath('.//PubDate/Day/text()').get('01')
                
                # Convertir mes textual a número si es necesario
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                    'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                
                if month in month_map:
                    month = month_map[month]
                
                # formatearla para la base de datos
                pub_date = None
                if year:
                    try:
                        # Asegurar formato correcto
                        month = month.zfill(2) if month.isdigit() else '01'
                        day = day.zfill(2) if day.isdigit() else '01'
                        pub_date = f"{year}-{month}-{day}"
                    except Exception as e:
                        self.logger.warning(f"Error formateando fecha: {e}")
                        pub_date = None
                
                # Extraemos la URL
                pmid = article.xpath('.//PMID/text()').get('')
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                
                # y el resumen del artículo con manejo mejorado:
                abstract_parts = article.xpath('.//AbstractText/text()').getall()
                abstract = ' '.join(abstract_parts) if abstract_parts else ""
                
                # Si no hay resumen, intentar extraerlo de otras partes
                if not abstract:
                    # Intentar obtener de OtherAbstract
                    other_abstract = article.xpath('.//OtherAbstract/AbstractText/text()').getall()
                    if other_abstract:
                        abstract = ' '.join(other_abstract)
                
                # Solo proceder si tenemos al menos título y URL
                if title and url:
                    yield {
                        'titulo': title,
                        'autor': ', '.join(authors) if authors else '',
                        'fecha_publicacion': pub_date,
                        'url_fuente': url,
                        'abstract': abstract,
                        'origen': 'PubMed',
                        'categoria': 'Sin categoría',  # Será asignada por el pipeline
                        'termino_busqueda': self.query
                    }
                else:
                    self.logger.warning(f"Artículo descartado por falta de título o URL: {pmid}")
                    
            except Exception as e:
                self.logger.error(f"Error parseando el artículo: {e}")
    
    def handle_error(self, failure):
        """Maneja errores de manera más robusta"""
        self.logger.error(f"Request failed: {failure}")
        
        # Información específica para rate limiting
        if failure.check(scrapy.exceptions.HttpError):
            response = failure.value.response
            status = response.status
            
            if status == 429:
                self.logger.warning("Rate limit alcanzado. Esperando antes de reintentar...")
                # Extraer tiempo de espera del encabezado si está disponible
                retry_after = response.headers.get('Retry-After')
                wait_time = int(retry_after) if retry_after else 60
                
                self.logger.info(f"Esperando {wait_time} segundos antes de reintentar...")
                time.sleep(wait_time)
            elif status in [500, 502, 503, 504]:
                self.logger.warning(f"Error del servidor ({status}). Esperando antes de reintentar...")
                time.sleep(30)  # Esperar 30 segundos para errores del servidor
            else:
                self.logger.error(f"Error HTTP {status}. Detalles: {response.text}")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """Método de clase para configurar el spider"""
        spider = super(PubmedSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        """Método llamado cuando el spider se cierra"""
        spider.logger.info(f"Spider {spider.name} terminó el scraping para la consulta: {self.query}")