# -*- coding: utf-8 -*-
"""
Health Check Endpoints
======================

Endpoints para monitoreo y verificación del estado de la aplicación.

Estos endpoints son cruciales para:
- Load balancers (verificar si la instancia está saludable)
- Sistemas de monitoreo (Prometheus, Datadog, etc.)
- Alertas automáticas cuando algo falla
- Debugging de problemas en producción
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check básico - verifica que la API esté respondiendo.

    Este endpoint debe responder rápidamente (< 100ms) y no realizar
    operaciones pesadas. Es usado por load balancers para verificar
    si la instancia debe recibir tráfico.

    Returns:
        dict: Estado de salud de la aplicación

    Status Codes:
        200: Todo OK
        503: Servicio no disponible (uno o más componentes fallan)
    """
    return {
        "status": "healthy",
        "service": "ClinicCloud API",
        "version": "0.1.0"
    }


@router.get("/health/detailed", tags=["health"])
async def detailed_health_check() -> Dict[str, Any]:
    """
    Health check detallado - verifica todos los componentes del sistema.

    Este endpoint verifica:
    - Conexión a la base de datos
    - Connection pool status
    - Rate limiting (Redis)
    - Motor de búsqueda

    ⚠️ Este endpoint puede tardar más que /health ya que prueba componentes.

    Returns:
        dict: Estado detallado de todos los componentes

    Status Codes:
        200: Todo OK
        503: Uno o más componentes fallan
    """
    health_status = {
        "status": "healthy",
        "service": "ClinicCloud API",
        "version": "0.1.0",
        "components": {}
    }

    all_healthy = True

    # 1. Verificar Connection Pool
    try:
        from app.db.pool import get_pool_stats
        pool_stats = await get_pool_stats()
        health_status["components"]["database_pool"] = {
            "status": "healthy",
            "stats": pool_stats
        }
    except Exception as e:
        logger.error(f"Database pool health check failed: {e}")
        health_status["components"]["database_pool"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        all_healthy = False

    # 2. Verificar conectividad a la base de datos
    try:
        from app.db.pool import fetch_one
        result = await fetch_one("SELECT 1 as test")
        if result and result["test"] == 1:
            health_status["components"]["database"] = {
                "status": "healthy"
            }
        else:
            raise Exception("Query test falló")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        all_healthy = False

    # 3. Verificar Redis (Rate Limiting)
    try:
        import redis.asyncio as redis
        import os
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        redis_client = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        await redis_client.close()
        health_status["components"]["redis"] = {
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        # Redis no es crítico, no marcamos como unhealthy
        # all_healthy = False

    # 4. Verificar Motor de Búsqueda
    try:
        import httpx
        import os
        search_engine_url = os.getenv("SEARCH_ENGINE_URL", "http://motor_busqueda:8001")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{search_engine_url}/")
            if response.status_code == 200:
                health_status["components"]["search_engine"] = {
                    "status": "healthy"
                }
            else:
                raise Exception(f"Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Search engine health check failed: {e}")
        health_status["components"]["search_engine"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        all_healthy = False

    # Determinar status general
    if not all_healthy:
        health_status["status"] = "unhealthy"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )

    return health_status


@router.get("/health/ready", tags=["health"])
async def readiness_check() -> Dict[str, str]:
    """
    Readiness check - verifica si la aplicación está lista para recibir tráfico.

    Diferencia con /health:
    - /health: "¿Está viva la aplicación?" (liveness)
    - /ready: "¿Está lista para procesar requests?" (readiness)

    Kubernetes usa estos dos endpoints por separado para:
    - Liveness: Reiniciar el pod si falla
    - Readiness: Quitar del load balancer temporalmente si no está listo

    Returns:
        dict: Estado de readiness
    """
    # Verificar que el pool esté inicializado
    try:
        from app.db.pool import get_pool
        pool = await get_pool()
        if pool is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "not_ready", "reason": "Database pool not initialized"}
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "reason": str(e)}
        )

    return {"status": "ready"}


@router.get("/health/live", tags=["health"])
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check - verifica que la aplicación no esté bloqueada o en deadlock.

    Este es el endpoint más simple y rápido. Solo verifica que FastAPI
    pueda responder requests.

    Si este endpoint no responde, Kubernetes reiniciará el pod.

    Returns:
        dict: Estado de liveness
    """
    return {"status": "alive"}
