import logging
import psycopg2
from typing import List, Dict, Any, Optional, Tuple, Union
from psycopg2.extras import RealDictCursor

from app.config import settings

logger = logging.getLogger("database")

def get_connection():
    """
    Crea una conexión a la base de datos PostgreSQL.
    """
    try:
        connection = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        return connection
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos: {str(e)}")
        raise

def execute_query(
    query: str, 
    params: Optional[List] = None,
    fetchone: bool = False
) -> Union[List[Tuple], Tuple, None]:
    """
    Ejecuta una consulta SQL y devuelve los resultados.
    
    Args:
        query: Cadena de consulta SQL
        params: Parámetros para la consulta SQL
        fetchone: Si se debe obtener un solo resultado o todos los resultados
        
    Returns:
        Resultados de la consulta o None si no hay resultados
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if cursor.description: 
            if fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            return result
            
        return None
    except Exception as e:
        logger.error(f"Error ejecutando consulta: {str(e)}")
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Params: {params}")
        raise
    finally:
        if connection:
            connection.close()

def execute_dict_query(
    query: str, 
    params: Optional[List] = None,
    fetchone: bool = False
) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
    """
    Ejecuta una consulta SQL y devuelve los resultados como diccionarios.
    
    Args:
        query: Cadena de consulta SQL
        params: Parámetros para la consulta SQL
        fetchone: Si se debe obtener un solo resultado o todos los resultados
        
    Returns:
        Resultados de la consulta como diccionarios o None si no hay resultados
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if cursor.description:  # If the query returns rows
            if fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            return result
            
        return None
    except Exception as e:
        logger.error(f"Error ejecutando consulta: {str(e)}")
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Params: {params}")
        raise
    finally:
        if connection:
            connection.close()