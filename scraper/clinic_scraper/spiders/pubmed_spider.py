import scrapy
import json
import time
from datetime import datetime
from scrapy.exceptions import CloseSpider

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
        self.api_key = ''  # Opcional: agrega tu API key de NCBI
    
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
        
        yield scrapy.FormRequest(
            url=esearch_url, 
            formdata=params, 
            callback=self.parse_search,
            errback=self.handle_error
        )
    
    def parse_search(self, response):
        try:
            # Extraer IDs de los resultados de búsqueda
            data = json.loads(response.body)
            id_list = data.get('esearchresult', {}).get('idlist', [])
            
            if not id_list:
                self.logger.warning(f"No articles found for the query: {self.query}")
                return
            
            # Paso 2: Obtener detalles de los artículos usando efetch
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
                errback=self.handle_error
            )
        except Exception as e:
            self.logger.error(f"Error parsing search results: {e}")
            raise CloseSpider(f"Parse error: {e}")
    
    def parse_articles(self, response):
        # Extraer información de los artículos del XML
        articles = response.xpath('//PubmedArticle')
        
        for article in articles:
            try:
                # Extraer título
                title = article.xpath('.//ArticleTitle/text()').get('')
                
                # Extraer autores
                authors = []
                author_list = article.xpath('.//Author')
                for author in author_list:
                    last_name = author.xpath('./LastName/text()').get('')
                    first_name = author.xpath('./ForeName/text()').get('')
                    if last_name and first_name:
                        authors.append(f"{last_name} {first_name}")
                
                # Extraer fecha de publicación
                year = article.xpath('.//PubDate/Year/text()').get('')
                month = article.xpath('.//PubDate/Month/text()').get('01')
                day = article.xpath('.//PubDate/Day/text()').get('01')
                
                # Formatear fecha para la base de datos
                pub_date = None
                if year:
                    try:
                        pub_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    except:
                        pub_date = None
                
                # Extraer URL
                pmid = article.xpath('.//PMID/text()').get('')
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                
                # Abstracts
                abstract_parts = article.xpath('.//AbstractText/text()').getall()
                abstract = ' '.join(abstract_parts)
                
                yield {
                    'titulo': title,
                    'autor': ', '.join(authors) if authors else '',
                    'fecha_publicacion': pub_date,
                    'url_fuente': url,
                    'abstract': abstract,
                    'origen': 'PubMed',
                    'categoria': 'Sin categoría',
                    'termino_busqueda': self.query
                }
            except Exception as e:
                self.logger.error(f"Error parsing individual article: {e}")
    
    def handle_error(self, failure):
        """Maneja errores de manera más robusta"""
        self.logger.error(f"Request failed: {failure}")
        
        # Información específica para rate limiting
        if failure.check(scrapy.exceptions.HttpError):
            response = failure.value.response
            if response.status == 429:
                self.logger.warning("Rate limit alcanzado. Esperando antes de reintentar...")
                time.sleep(60)  # Espera 1 minuto antes de reintentar

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """Método de clase para configurar el spider"""
        spider = super(PubmedSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        """Método llamado cuando el spider se cierra"""
        spider.logger.info(f"Spider {spider.name} finished scraping for query: {self.query}")