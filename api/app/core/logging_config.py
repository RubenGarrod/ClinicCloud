# -*- coding: utf-8 -*-
"""
Structured Logging Configuration
=================================

Sistema de logging estructurado para producción con:
- Formato JSON para integración con sistemas de monitoreo
- Context enrichment (request_id, user_id, IP, etc.)
- Niveles configurables por entorno
- Integración con FastAPI middleware

Ventajas:
- Búsqueda y filtrado eficiente en ELK/Datadog/CloudWatch
- Correlación de logs por request_id
- Auditoría con user_id e IP
- Performance tracking con timestamps precisos
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar

# Context variables para request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
client_ip_var: ContextVar[Optional[str]] = ContextVar('client_ip', default=None)


class JSONFormatter(logging.Formatter):
    """
    Formateador JSON para logs estructurados.

    Añade automáticamente:
    - timestamp en ISO 8601
    - level (INFO, ERROR, etc.)
    - logger name
    - message
    - request_id (si está disponible)
    - user_id (si está disponible)
    - client_ip (si está disponible)
    - exception info (si existe)
    """

    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log record como JSON."""

        # Estructura base del log
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Añadir request context si está disponible
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        client_ip = client_ip_var.get()
        if client_ip:
            log_data["client_ip"] = client_ip

        # Añadir información de excepción si existe
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None
            }

        # Añadir campos custom del record (si existen)
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False)


class HumanReadableFormatter(logging.Formatter):
    """
    Formateador legible para desarrollo local.

    Formato más amigable para lectura directa en consola.
    """

    # Colores ANSI para diferentes niveles
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log record de forma legible."""

        # Color según nivel
        color = self.COLORS.get(record.levelname, '')

        # Timestamp
        timestamp = datetime.utcnow().strftime('%H:%M:%S')

        # Request ID si existe
        request_id = request_id_var.get()
        request_str = f" [{request_id[:8]}]" if request_id else ""

        # User ID si existe
        user_id = user_id_var.get()
        user_str = f" user={user_id}" if user_id else ""

        # Formatear mensaje
        msg = f"{color}{timestamp} {record.levelname:8}{self.RESET} {record.name}:{record.lineno}{request_str}{user_str} - {record.getMessage()}"

        # Añadir excepción si existe
        if record.exc_info:
            msg += "\n" + self.formatException(record.exc_info)

        return msg


def configure_logging(
    environment: str = "development",
    log_level: str = "INFO"
) -> None:
    """
    Configura el sistema de logging de la aplicación.

    Args:
        environment: "development" o "production"
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """

    # Determinar formato según entorno
    if environment == "production":
        formatter = JSONFormatter()
    else:
        formatter = HumanReadableFormatter()

    # Configurar handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configurar logging root
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers = []  # Limpiar handlers existentes
    root_logger.addHandler(handler)

    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Log de confirmación
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configurado: environment={environment}, level={log_level}, format={'JSON' if environment == 'production' else 'human-readable'}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado.

    Args:
        name: Nombre del logger (típicamente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
) -> None:
    """
    Log con context adicional.

    Args:
        logger: Logger a usar
        level: Nivel (debug, info, warning, error, critical)
        message: Mensaje a loggear
        **kwargs: Datos adicionales a incluir en el log

    Example:
        log_with_context(
            logger,
            "info",
            "Usuario creado",
            user_id=user.id,
            email=user.email,
            action="user_created"
        )
    """
    log_method = getattr(logger, level.lower())

    # Crear un LogRecord con extra_data
    if kwargs:
        # Usar extra parameter de logging
        log_method(message, extra={'extra_data': kwargs})
    else:
        log_method(message)


# Helper functions para context management
def set_request_context(request_id: str, user_id: Optional[str] = None, client_ip: Optional[str] = None):
    """Establece el contexto del request actual."""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if client_ip:
        client_ip_var.set(client_ip)


def clear_request_context():
    """Limpia el contexto del request."""
    request_id_var.set(None)
    user_id_var.set(None)
    client_ip_var.set(None)


def get_request_id() -> Optional[str]:
    """Obtiene el request_id actual."""
    return request_id_var.get()


# Configurar al importar (usa variables de entorno)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

configure_logging(ENVIRONMENT, LOG_LEVEL)
