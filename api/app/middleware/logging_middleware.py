# -*- coding: utf-8 -*-
"""
Logging Middleware
==================

Middleware para request tracking y logging automático.

Funcionalidades:
- Genera un request_id único por request
- Captura user_id y client_ip automáticamente
- Loggea cada request con duración y status code
- Maneja excepciones con logging estructurado
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging_config import set_request_context, clear_request_context, get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging automático de requests.

    Para cada request:
    1. Genera un request_id único (UUID)
    2. Captura user_id del state (si está autenticado)
    3. Captura client_ip (con soporte para proxies)
    4. Loggea el request con método, path, user
    5. Loggea la respuesta con status_code y duración
    6. Maneja excepciones con logging detallado
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesa cada request añadiendo logging estructurado."""

        # Generar request_id único
        request_id = str(uuid.uuid4())

        # Obtener client IP (con soporte para proxies)
        client_ip = self._get_client_ip(request)

        # Establecer contexto (user_id se añadirá cuando esté autenticado)
        set_request_context(request_id=request_id, client_ip=client_ip)

        # Añadir request_id al request state para acceso posterior
        request.state.request_id = request_id

        # Timestamp de inicio
        start_time = time.time()

        # Log del inicio del request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                'extra_data': {
                    'event': 'request_started',
                    'method': request.method,
                    'path': request.url.path,
                    'query_params': dict(request.query_params) if request.query_params else None,
                }
            }
        )

        try:
            # Procesar request
            response = await call_next(request)

            # Calcular duración
            duration_ms = (time.time() - start_time) * 1000

            # Actualizar contexto con user_id si está disponible
            user = getattr(request.state, "user", None)
            if user and hasattr(user, "id"):
                from app.core.logging_config import user_id_var
                user_id_var.set(str(user.id))

            # Log del final del request
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} ({duration_ms:.2f}ms)",
                extra={
                    'extra_data': {
                        'event': 'request_completed',
                        'method': request.method,
                        'path': request.url.path,
                        'status_code': response.status_code,
                        'duration_ms': round(duration_ms, 2),
                        'user_id': str(user.id) if user and hasattr(user, "id") else None,
                    }
                }
            )

            # Añadir request_id al header de respuesta (útil para debugging)
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calcular duración hasta el error
            duration_ms = (time.time() - start_time) * 1000

            # Log del error
            logger.error(
                f"{request.method} {request.url.path} - ERROR ({duration_ms:.2f}ms): {str(e)}",
                exc_info=True,
                extra={
                    'extra_data': {
                        'event': 'request_failed',
                        'method': request.method,
                        'path': request.url.path,
                        'duration_ms': round(duration_ms, 2),
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                    }
                }
            )

            # Re-raise para que FastAPI maneje la excepción
            raise

        finally:
            # Limpiar contexto
            clear_request_context()

    def _get_client_ip(self, request: Request) -> str:
        """
        Obtiene la IP del cliente, considerando proxies.

        Revisa headers en orden de prioridad:
        1. X-Forwarded-For (si está detrás de proxy/load balancer)
        2. X-Real-IP (algunos proxies usan esto)
        3. client.host (conexión directa)
        """
        # X-Forwarded-For puede contener múltiples IPs: "client, proxy1, proxy2"
        # La primera es la del cliente original
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # X-Real-IP usado por algunos proxies
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback a conexión directa
        return request.client.host if request.client else "unknown"


# Helper para loggear eventos custom
def log_event(
    event_name: str,
    message: str,
    level: str = "info",
    **kwargs
) -> None:
    """
    Helper para loggear eventos custom con estructura consistente.

    Args:
        event_name: Nombre del evento (ej: "user_created", "payment_processed")
        message: Mensaje descriptivo
        level: Nivel de logging (debug, info, warning, error, critical)
        **kwargs: Datos adicionales del evento

    Example:
        log_event(
            "user_created",
            "Nuevo usuario registrado",
            user_id=user.id,
            email=user.email,
            source="registration_form"
        )
    """
    log_method = getattr(logger, level.lower())

    kwargs['event'] = event_name

    log_method(
        message,
        extra={'extra_data': kwargs}
    )
