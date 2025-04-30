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

def execute_query(query, params=None, fetchone=False, commit=False):
    """Ejecuta una consulta en la base de datos."""
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        if fetchone:
            return cursor.fetchone()
        return cursor.fetchall()