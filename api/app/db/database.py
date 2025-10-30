# -*- coding: utf-8 -*-
"""
Modulo para la conexion de la API REST con la base de datos PostgreSQL.
Este modulo proporciona funciones para ejecutar consultas SQL y manejar transacciones.
"""
import psycopg2
from contextlib import contextmanager
from app.config import DATABASE_URL

@contextmanager
def get_db_connection():
    """Proporciona un contexto para la conexión a la base de datos."""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    finally:
        if conn is not None:
            conn.close()

@contextmanager
def get_db_cursor(commit=False):
    """Proporciona un contexto para el cursor de la base de datos."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()

def execute_query(query, params=None, fetchone=False, fetchall=True, commit=False):
    """Ejecuta una consulta en la base de datos."""
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        return None

# Alias for compatibility
get_database_connection = get_db_connection