import logging
import psycopg2
from typing import List, Dict, Any, Optional, Tuple
from .models import DocumentResult

class DatabaseConnector:
    """Conector para realizar búsquedas vectoriales en PostgreSQL con pgvector"""
    
    def __init__(self, config: Dict[str, str]):
        """Inicializa la conexión a la base de datos"""
        self.logger = logging.getLogger('db_connector')
        self.config = config
        self.connection = None
        self.cursor = None
        
    def connect(self) -> None:
        """Establece la conexión a la base de datos"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', '5432'),
                dbname=self.config.get('dbname', 'cliniccloud'),
                user=self.config.get('user', 'admin'),
                password=self.config.get('password', 'admin123')
            )
            self.cursor = self.connection.cursor()
            self.logger.info("Conexión a la base de datos establecida")
        except Exception as e:
            self.logger.error(f"Error al conectar a la base de datos: {e}")
            raise
    
    def close(self) -> None:
        """Cierra la conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.logger.info("Conexión a la base de datos cerrada")
    
    def search_documents(self, 
                        query_vector: List[float], 
                        category_id: Optional[int] = None, 
                        limit: int = 20, 
                        offset: int = 0,
                        similarity_threshold: float = 0.5) -> List[DocumentResult]:
        """
        Realiza una búsqueda vectorial en la base de datos
        
        Args:
            query_vector: Vector de la consulta
            category_id: ID de categoría para filtrar (opcional)
            limit: Número máximo de resultados
            offset: Desplazamiento para paginación
            similarity_threshold: Umbral mínimo de similitud
            
        Returns:
            Lista de documentos resultantes
        """
        try:
            # Conectar si aún no lo está
            if not self.connection or self.connection.closed:
                self.connect()
                
            sql = """
            SELECT d.id, d.titulo, d.autor, d.fecha_publicacion, d.url_fuente,
                r.texto_resumen, c.id as categoria_id, c.nombre as categoria_nombre,
                1 - (d.contenido_vectorizado <=> %s::vector) as score
            FROM documento d
            JOIN resumen r ON d.id = r.id_documento
            LEFT JOIN categoria c ON d.id_categoria = c.id
            """

            params = [query_vector]

            # Condición para filtrar por categoría
            where_clause = " WHERE 1 - (d.contenido_vectorizado <=> %s::vector) > %s "
            params.append(query_vector)
            params.append(similarity_threshold)

            
            if category_id:
                where_clause += " AND d.id_categoria = %s"
                params.append(category_id)
                
            # Añadir cláusula WHERE
            sql += where_clause
            
            # Ordenar por puntuación de similitud
            sql += " ORDER BY score DESC LIMIT %s OFFSET %s"
            params.append(limit)
            params.append(offset)
            
            # Ejecutar consulta
            self.cursor.execute(sql, params)
            results = self.cursor.fetchall()
            
            # Convertir a objetos DocumentResult
            documents = []
            for row in results:
                # Procesar autor (convertir a lista si es una cadena)
                autor = []
                if row[2]:  # row[2] es el campo 'autor'
                    if isinstance(row[2], str):
                        # Si hay múltiples autores separados por comas
                        autor = [a.strip() for a in row[2].split(',') if a.strip()]
                    else:
                        autor = [row[2]]
                
                # Crear objeto de documento
                document = DocumentResult(
                    id=row[0],
                    titulo=row[1],
                    autor=autor,
                    fecha_publicacion=row[3],
                    url_fuente=row[4],
                    texto_resumen=row[5],
                    categoria={
                        "id": row[6],
                        "nombre": row[7]
                    } if row[6] else None,
                    score=row[8]
                )
                documents.append(document)
                
            return documents
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda vectorial: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.close()