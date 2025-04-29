# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2 # type: ignore
from datetime import datetime
import numpy as np # type: ignore
import traceback
import os
import logging
from inferencia.categorizador import obtener_mejor_categoria, obtener_categorias_recomendadas

# Configura un logger específico
logger = logging.getLogger('clinic_scraper.pipelines')

class ClinicScraperPipeline:
    def process_item(self, item, spider):
        return item

class PostgreSQLPipeline:
    def __init__(self, pg_host, pg_port, pg_db, pg_user, pg_password):
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_db = pg_db
        self.pg_user = pg_user
        self.pg_password = pg_password
        self.connection = None
        self.cursor = None
        # No cargar el modelo aquí para evitar problemas de importación
        self.model = None
        self.categoria_default_id = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            pg_host=crawler.settings.get('PG_HOST', 'db'),
            pg_port=crawler.settings.get('PG_PORT', '5432'),
            pg_db=crawler.settings.get('PG_DATABASE', 'cliniccloud'),
            pg_user=crawler.settings.get('PG_USER', 'admin'),
            pg_password=crawler.settings.get('PG_PASSWORD', 'admin123')
        )
    
    def open_spider(self, spider):
        try:
            spider.logger.info(f"Conectando a la base de datos: {self.pg_host}:{self.pg_port}/{self.pg_db}")
            self.connection = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                dbname=self.pg_db,
                user=self.pg_user,
                password=self.pg_password
            )
            self.cursor = self.connection.cursor()
            
            # Verificar que la tabla categoría existe
            self.cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'categoria')")
            tabla_existe = self.cursor.fetchone()[0]
            if not tabla_existe:
                spider.logger.error("La tabla 'categoria' no existe en la base de datos")
                raise Exception("Tabla 'categoria' no encontrada")
            
            # Comprobar la estructura de la tabla documento
            self.cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'documento'")
            columnas = {col[0]: col[1] for col in self.cursor.fetchall()}
            spider.logger.info(f"Estructura de la tabla 'documento': {columnas}")
            
            # Asegurarse de que existe la categoría "Medicina General"
            self.cursor.execute(
                "INSERT INTO categoria (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING",
                ("Medicina General",)
            )
            self.connection.commit()
            
            self.cursor.execute("SELECT id FROM categoria WHERE nombre = %s", ("Medicina General",))
            self.categoria_default_id = self.cursor.fetchone()[0]
            spider.logger.info(f"ID de categoría 'Medicina General': {self.categoria_default_id}")
            
            # Pre-crear las categorías médicas principales
            self._crear_categorias_principales(spider)
            
            # Inicializar el modelo de embedding cuando ya estamos seguros que todo está bien
            try:
                from sentence_transformers import SentenceTransformer # type: ignore
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                spider.logger.info("Modelo SentenceTransformer cargado correctamente")
            except ImportError as e:
                spider.logger.error(f"Error al cargar SentenceTransformer: {e}")
                spider.logger.warning("Se usarán vectores aleatorios como fallback")
                self.model = None
            
            spider.logger.info("Conexión a la base de datos establecida correctamente")
        except Exception as e:
            spider.logger.error(f"Error al conectar a la base de datos: {e}")
            spider.logger.error(traceback.format_exc())
            raise
    
    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        spider.logger.info("Conexión a la base de datos cerrada")
    
    def _crear_categorias_principales(self, spider):
        """Crea las categorías médicas principales en la base de datos"""
        categorias_principales = [
            "Oncología", "Cardiología", "Neurología", "Endocrinología", "Gastroenterología",
            "Neumología", "Nefrología", "Infectología", "Inmunología", "Hematología",
            "Dermatología", "Pediatría", "Geriatría", "Obstetricia y Ginecología",
            "Reumatología", "Oftalmología", "Otorrinolaringología", "Psiquiatría",
            "Traumatología", "Urología", "Genética Médica", "Medicina General"
        ]
        
        try:
            for categoria in categorias_principales:
                self.cursor.execute(
                    "INSERT INTO categoria (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING",
                    (categoria,)
                )
            self.connection.commit()
            spider.logger.info(f"Categorías médicas principales creadas: {len(categorias_principales)}")
        except Exception as e:
            spider.logger.error(f"Error al crear categorías principales: {e}")
            self.connection.rollback()
    
    def _get_categoria_id(self, titulo, abstract, spider):
        """
        Obtiene o crea una categoría apropiada basada en el contenido del documento
        
        Args:
            titulo: Título del documento
            abstract: Abstract o resumen del documento
            spider: Instancia del spider para logging
            
        Returns:
            ID de la categoría en la base de datos
        """
        try:
            # Usar el motor de inferencia para determinar la categoría
            categoria_nombre = obtener_mejor_categoria(titulo, abstract)
            spider.logger.info(f"Categoría inferida: {categoria_nombre}")
            
            # Intentar obtener el ID de la categoría
            self.cursor.execute("SELECT id FROM categoria WHERE nombre = %s", (categoria_nombre,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return resultado[0]
            
            # Si no existe la categoría (poco probable dado que pre-creamos las principales),
            # la creamos
            self.cursor.execute(
                "INSERT INTO categoria (nombre) VALUES (%s) RETURNING id",
                (categoria_nombre,)
            )
            self.connection.commit()
            nuevo_id = self.cursor.fetchone()[0]
            spider.logger.info(f"Creada nueva categoría '{categoria_nombre}' con ID {nuevo_id}")
            return nuevo_id
        except Exception as e:
            spider.logger.error(f"Error al obtener/crear categoría: {e}")
            return self.categoria_default_id  # Fallback a categoría default

    def _generate_embedding(self, text, spider):
        """Genera el embedding para el texto dado"""
        if self.model is not None:
            try:
                # Usar el modelo para generar el embedding
                embedding = self.model.encode(text)
                # Convertir a vector de 768 dimensiones
                return self._convert_embedding_to_pgvector(embedding)
            except Exception as e:
                spider.logger.error(f"Error al generar embedding: {e}")
        
        # Fallback: generar vector aleatorio
        spider.logger.warning("Usando vector aleatorio como fallback")
        return self._generate_random_vector()
    
    def _generate_random_vector(self):
        """Genera un vector aleatorio de 768 dimensiones"""
        return np.random.rand(768).tolist()

    def _convert_embedding_to_pgvector(self, embedding):
        """Convierte un array numpy a formato pgvector de 768 dimensiones"""
        # Creamos un array de 768 dimensiones lleno de ceros
        padded_embedding = np.zeros(768)
        
        # Copiamos el embedding original en las primeras posiciones
        padded_embedding[:len(embedding)] = embedding
        
        return padded_embedding.tolist()

    def process_item(self, item, spider):
        try:
            titulo = item.get('titulo', '')
            abstract = item.get('abstract', '')
            
            spider.logger.info(f"Procesando item: {titulo[:50]}...")
            
            # Generar el embedding del texto
            text_to_embed = f"{titulo} {abstract}"
            vector_768 = self._generate_embedding(text_to_embed, spider)
            spider.logger.info("Embedding generado correctamente")
            
            # Obtener el ID de la categoría mediante inferencia
            categoria_id = self._get_categoria_id(titulo, abstract, spider)
            spider.logger.info(f"Categoría ID obtenida: {categoria_id}")
            
            # Formatear la fecha
            fecha_pub = None
            if item.get('fecha_publicacion'):
                try:
                    for fmt in ['%Y-%m-%d', '%Y-%b-%d', '%Y-%B-%d']:
                        try:
                            fecha_pub = datetime.strptime(item.get('fecha_publicacion'), fmt)
                            break
                        except ValueError:
                            continue
                    
                    if not fecha_pub:
                        spider.logger.warning(f"No se pudo parsear la fecha: {item.get('fecha_publicacion')}")
                except Exception as fecha_error:
                    spider.logger.error(f"Error al procesar fecha: {fecha_error}")
            
            # Insertar el documento con su embedding
            spider.logger.info("Intentando insertar documento en la base de datos")
            self.cursor.execute(
                """
                INSERT INTO documento 
                (titulo, autor, fecha_publicacion, contenido_vectorizado, url_fuente, id_categoria)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    titulo,
                    item.get('autor', ''),
                    fecha_pub,
                    vector_768,
                    item.get('url_fuente', ''),
                    categoria_id
                )
            )
            documento_id = self.cursor.fetchone()[0]
            spider.logger.info(f"Documento insertado con ID: {documento_id}")
            
            # Generar el resumen e insertar en la tabla resumen
            if abstract:
                try:
                    from inferencia.motor_inferencia import generar_miniresumen
                    resumen_corto = generar_miniresumen(abstract)
                    
                    # Insertar en la tabla resumen con referencia al documento
                    self.cursor.execute(
                        "INSERT INTO resumen (id_documento, texto_resumen) VALUES (%s, %s)",
                        (documento_id, resumen_corto)
                    )
                    spider.logger.info(f"Resumen insertado para documento ID: {documento_id}")
                except Exception as e:
                    spider.logger.error(f"Error al generar o insertar resumen: {e}")
                    spider.logger.error(traceback.format_exc())
            
            # Obtener categorías adicionales recomendadas para futuras referencias
            try:
                categorias_recomendadas = obtener_categorias_recomendadas(titulo, abstract, n=3)
                spider.logger.info(f"Categorías recomendadas: {categorias_recomendadas}")
            except Exception as e:
                spider.logger.error(f"Error al obtener categorías recomendadas: {e}")
            
            self.connection.commit()
            spider.logger.info(f"Transacción completada exitosamente para '{titulo[:50]}...'")

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            spider.logger.error(f"Error al procesar item: {e}")
            spider.logger.error(traceback.format_exc())
            spider.logger.error(f"Detalles del item: {item}")

        return item

# Pipeline para pruebas locales
class PrintPipeline:
    def process_item(self, item, spider):
        print("\n" + "="*50)
        print(f"TÍTULO: {item.get('titulo', 'Sin título')}")
        print(f"AUTORES: {item.get('autor', 'Sin autores')}")
        print(f"FECHA: {item.get('fecha_publicacion', 'Sin fecha')}")
        print(f"URL: {item.get('url_fuente', 'Sin URL')}")
        print(f"RESUMEN: {item.get('abstract', 'Sin resumen')[:150]}..." if item.get('abstract') else "Sin resumen")
        print("="*50 + "\n")
        return item