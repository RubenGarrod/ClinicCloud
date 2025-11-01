"""
Rate Limiting Configuration
============================

Implementa rate limiting para proteger la API contra:
- Ataques de fuerza bruta (login, register)
- Abuso de recursos (búsquedas)
- DDoS simple

Usa fastapi-limiter con Redis como backend.
Compatible con response_model de FastAPI.
"""

from fastapi import Request
from fastapi_limiter.depends import RateLimiter
import os
import logging

logger = logging.getLogger(__name__)


# Rate limits específicos por tipo de endpoint
# Formato: RateLimiter(times=N, seconds=S) o RateLimiter(times=N, minutes=M)
RATE_LIMITS = {
    # Autenticación - muy restrictivo
    "auth_login": RateLimiter(times=5, minutes=1),  # 5 intentos de login por minuto
    "auth_register": RateLimiter(times=3, hours=1),  # 3 registros por hora (por IP)
    "auth_reset_password": RateLimiter(times=3, hours=1),  # 3 intentos de reset por hora

    # Búsquedas - moderado
    "search_authenticated": RateLimiter(times=30, minutes=1),  # 30 búsquedas/min para usuarios autenticados
    "search_anonymous": RateLimiter(times=10, minutes=1),  # 10 búsquedas/min para anónimos

    # Documentos - permisivo
    "documents_read": RateLimiter(times=100, minutes=1),  # Leer documentos
    "documents_write": RateLimiter(times=20, minutes=1),  # Crear/modificar documentos

    # Favoritos y historial - permisivo
    "favorites": RateLimiter(times=50, minutes=1),
    "history": RateLimiter(times=50, minutes=1),

    # Reportes y contacto - restrictivo
    "report_issue": RateLimiter(times=5, hours=1),  # 5 reportes por hora
    "contact": RateLimiter(times=5, hours=1),  # 5 mensajes de contacto por hora
}


async def rate_limit_with_cors_support(request: Request, limit_type: str):
    """
    Rate limiter wrapper que no aplica límites a OPTIONS requests (CORS preflight).

    Los preflight requests CORS deben pasar sin rate limiting para que
    el navegador pueda verificar permisos antes del request real.
    """
    # Skip rate limiting para OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return None

    # Aplicar rate limiting normalmente para otros métodos
    limiter = RATE_LIMITS.get(limit_type)
    if not limiter:
        logger.warning(f"Rate limiter no encontrado para {limit_type}, usando default")
        limiter = RateLimiter(times=100, hours=1)

    logger.debug(f"Rate limiter para {limit_type}: {limiter}")
    # Ejecutar el rate limiter
    await limiter(request)
    return None


def get_rate_limiter(limit_type: str):
    """
    Obtiene el rate limiter configurado para un tipo de endpoint.
    Automáticamente excluye OPTIONS requests (CORS preflight).

    Args:
        limit_type: Tipo de endpoint (ej: "auth_login", "search_authenticated")

    Returns:
        Dependency que aplica rate limiting (pero no a OPTIONS)
    """
    async def rate_limit_dependency(request: Request):
        return await rate_limit_with_cors_support(request, limit_type)

    return rate_limit_dependency


async def get_client_identifier(request: Request) -> str:
    """
    Obtiene un identificador único para el cliente.

    Si el usuario está autenticado, usa user_id.
    Si no, usa la IP del cliente.

    Esto permite rate limits más estrictos para usuarios no autenticados.
    """
    # Intentar obtener user_id del request state (si está autenticado)
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        client_id = f"user:{user.id}"
        logger.debug(f"Rate limit identifier: {client_id}")
        return client_id

    # Fallback a IP address
    # Considerar X-Forwarded-For si está detrás de proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"

    logger.debug(f"Rate limit identifier: ip:{ip}")
    return f"ip:{ip}"


# Variables de entorno para configuración
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

if RATE_LIMIT_ENABLED:
    logger.info(f"✅ Rate limiting configurado con Redis: {REDIS_URL}")
else:
    logger.warning("⚠️ Rate limiting DESHABILITADO (RATE_LIMIT_ENABLED=false)")
