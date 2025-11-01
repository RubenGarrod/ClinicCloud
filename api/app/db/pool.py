# -*- coding: utf-8 -*-
"""
Connection Pooling para PostgreSQL usando asyncpg
==================================================

Este módulo proporciona un pool de conexiones reutilizables para mejorar
el rendimiento y reducir la sobrecarga de crear/destruir conexiones.

Ventajas:
- Reutilización de conexiones
- Manejo automático de reconexión
- Límite de conexiones concurrentes
- Mejor rendimiento bajo carga

Uso:
    from app.db.pool import get_pool

    async def my_endpoint():
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT * FROM table")
"""

import asyncpg
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Pool global (inicializado en startup)
_pool: Optional[asyncpg.Pool] = None

# Configuración del pool desde variables de entorno
POOL_MIN_SIZE = int(os.getenv("DB_POOL_MIN_SIZE", "5"))  # Conexiones mínimas en el pool
POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", "20"))  # Conexiones máximas en el pool
POOL_MAX_QUERIES = int(os.getenv("DB_POOL_MAX_QUERIES", "50000"))  # Queries antes de reciclar conexión
POOL_MAX_INACTIVE_CONN_LIFETIME = float(os.getenv("DB_POOL_MAX_INACTIVE_CONN_LIFETIME", "300.0"))  # 5 minutos


async def init_pool() -> asyncpg.Pool:
    """
    Inicializa el pool de conexiones a PostgreSQL.

    Esta función debe llamarse al inicio de la aplicación (en startup event).

    Returns:
        asyncpg.Pool: Pool de conexiones listo para usar

    Raises:
        Exception: Si no se puede conectar a la base de datos
    """
    global _pool

    if _pool is not None:
        logger.warning("Pool ya estaba inicializado, cerrando el anterior")
        await close_pool()

    # Obtener configuración de base de datos desde variables de entorno
    db_host = os.getenv("DB_HOST", "db")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "cliniccloud")
    db_user = os.getenv("DB_USER", "cliniccloud")
    db_password = os.getenv("DB_PASSWORD", "changeme")

    try:
        _pool = await asyncpg.create_pool(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            min_size=POOL_MIN_SIZE,
            max_size=POOL_MAX_SIZE,
            max_queries=POOL_MAX_QUERIES,
            max_inactive_connection_lifetime=POOL_MAX_INACTIVE_CONN_LIFETIME,
            command_timeout=60.0,  # Timeout de 60 segundos para queries
        )

        logger.info(
            f"✅ Connection pool inicializado: "
            f"{POOL_MIN_SIZE}-{POOL_MAX_SIZE} conexiones, "
            f"host={db_host}, db={db_name}"
        )

        return _pool

    except Exception as e:
        logger.error(f"❌ Error al inicializar connection pool: {e}")
        raise


async def get_pool() -> asyncpg.Pool:
    """
    Obtiene el pool de conexiones.

    Si el pool no está inicializado, lo inicializa automáticamente.

    Returns:
        asyncpg.Pool: Pool de conexiones activo

    Raises:
        RuntimeError: Si el pool no está disponible
    """
    global _pool

    if _pool is None:
        logger.warning("Pool no inicializado, inicializando automáticamente...")
        await init_pool()

    if _pool is None:
        raise RuntimeError("Connection pool no disponible")

    return _pool


async def close_pool():
    """
    Cierra el pool de conexiones.

    Esta función debe llamarse al apagar la aplicación (en shutdown event).
    """
    global _pool

    if _pool is not None:
        await _pool.close()
        logger.info("✅ Connection pool cerrado correctamente")
        _pool = None
    else:
        logger.warning("Pool ya estaba cerrado")


async def get_connection():
    """
    Context manager para obtener una conexión del pool.

    Uso:
        async with get_connection() as conn:
            result = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

    Yields:
        asyncpg.Connection: Conexión lista para usar
    """
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection


# Funciones helper para queries comunes
async def fetch_one(query: str, *args):
    """
    Ejecuta una query y retorna una sola fila.

    Args:
        query: Query SQL
        *args: Parámetros de la query

    Returns:
        asyncpg.Record | None: Primera fila o None
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def fetch_all(query: str, *args):
    """
    Ejecuta una query y retorna todas las filas.

    Args:
        query: Query SQL
        *args: Parámetros de la query

    Returns:
        List[asyncpg.Record]: Lista de filas
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def execute(query: str, *args):
    """
    Ejecuta una query que no retorna resultados (INSERT, UPDATE, DELETE).

    Args:
        query: Query SQL
        *args: Parámetros de la query

    Returns:
        str: Status string (ej: "INSERT 0 1")
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)


async def execute_many(query: str, args_list):
    """
    Ejecuta una query múltiples veces con diferentes parámetros (batch insert).

    Args:
        query: Query SQL
        args_list: Lista de tuplas con parámetros

    Example:
        await execute_many(
            "INSERT INTO users (name, email) VALUES ($1, $2)",
            [("John", "john@example.com"), ("Jane", "jane@example.com")]
        )
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.executemany(query, args_list)


# Estadísticas del pool (útil para monitoring)
async def get_pool_stats() -> dict:
    """
    Obtiene estadísticas del pool de conexiones.

    Returns:
        dict: Estadísticas con size, free connections, etc.
    """
    pool = await get_pool()
    return {
        "size": pool.get_size(),
        "free_size": pool.get_idle_size(),
        "min_size": pool.get_min_size(),
        "max_size": pool.get_max_size(),
    }
