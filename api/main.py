# -*- coding: utf-8 -*-
"""
ClinicCloud API - Main Application Entry Point

Copyright (C) 2025 Rubén García Rodríguez

This file is part of ClinicCloud.

ClinicCloud is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ClinicCloud is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse

from app.api.endpoints import search, documents, categories, translate, favorites, history, report_issue, health
from app.api.endpoints.auth import login, password_reset
from app.core.rate_limiter import RATE_LIMIT_ENABLED, REDIS_URL
from app.middleware.logging_middleware import RequestLoggingMiddleware

# Configurar logging estructurado (se inicializa automáticamente al importar)
from app.core.logging_config import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="ClinicCloud API",
    description="API para el motor de búsqueda de información médica con procesamiento de lenguaje natural",
    version="0.1.0"
)

# ============================================================================
# STARTUP / SHUTDOWN EVENTS
# ============================================================================
@app.on_event("startup")
async def startup():
    """Inicializar servicios al arrancar la aplicación"""

    # 1. Inicializar Connection Pool
    try:
        from app.db.pool import init_pool
        await init_pool()
    except Exception as e:
        logger.error(f"❌ Error al inicializar connection pool: {e}")
        logger.warning("⚠️ Connection pool NO disponible - usando conexiones directas")

    # 2. Inicializar Rate Limiting
    if RATE_LIMIT_ENABLED:
        try:
            import redis.asyncio as redis
            from fastapi_limiter import FastAPILimiter

            redis_connection = await redis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await FastAPILimiter.init(redis_connection)
            logger.info(f"✅ Rate limiting ACTIVADO con Redis: {REDIS_URL}")
        except Exception as e:
            logger.error(f"❌ Error al inicializar rate limiting: {e}")
            logger.warning("⚠️ Rate limiting NO disponible - continuando sin rate limits")
    else:
        logger.warning("⚠️ Rate limiting DESACTIVADO (RATE_LIMIT_ENABLED=false)")

@app.on_event("shutdown")
async def shutdown():
    """Cerrar servicios al apagar la aplicación"""

    # 1. Cerrar Connection Pool
    try:
        from app.db.pool import close_pool
        await close_pool()
    except Exception as e:
        logger.error(f"Error al cerrar connection pool: {e}")

    # 2. Cerrar Rate Limiting
    if RATE_LIMIT_ENABLED:
        try:
            from fastapi_limiter import FastAPILimiter
            await FastAPILimiter.close()
            logger.info("✅ Rate limiting cerrado correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar rate limiting: {e}")

# ============================================================================
# CORS - CONFIGURACIÓN SEGURA
# ============================================================================
# IMPORTANTE: NO usar "*" en producción con allow_credentials=True
# Definir SOLO los dominios autorizados

# Obtener orígenes permitidos desde variable de entorno o usar defaults seguros
ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if os.getenv("CORS_ALLOWED_ORIGINS") else [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:80",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]

# Limpiar espacios en blanco
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]

# Si APP_URL está configurado, añadirlo automáticamente
app_url = os.getenv("APP_URL")
if app_url and app_url not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(app_url)
    # Añadir también variante con/sin puerto
    try:
        parsed = urlparse(app_url)
        if parsed.port:
            no_port_url = f"{parsed.scheme}://{parsed.hostname}"
            if no_port_url not in ALLOWED_ORIGINS:
                ALLOWED_ORIGINS.append(no_port_url)
    except Exception:
        pass

# Log de orígenes permitidos (para debugging)
logger.info(f"✅ CORS: Orígenes permitidos configurados: {ALLOWED_ORIGINS}")

# Advertencia si se está usando wildcard en producción
if "*" in ALLOWED_ORIGINS and os.getenv("ENVIRONMENT") == "production":
    logger.error("⚠️ PELIGRO: CORS configurado con '*' en producción. Esto es una vulnerabilidad de seguridad.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ Solo dominios específicos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # ✅ Métodos específicos
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],  # ✅ Headers específicos
    max_age=3600,  # Cache preflight por 1 hora
)

# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================
# Añadir después de CORS para que capture todos los requests
app.add_middleware(RequestLoggingMiddleware)
logger.info("✅ Request logging middleware activado")

# Rutas de health check (sin autenticación para load balancers)
app.include_router(health.router, prefix="/api")

# Rutas de autenticación (sin prefix adicional porque ya está en el router)
app.include_router(login.router, prefix="/api")
app.include_router(password_reset.router, prefix="/api/auth", tags=["auth"])

# Rutas principales de la aplicación
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(translate.router, prefix="/api/translate", tags=["translate"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(report_issue.router, prefix="/api", tags=["support"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de ClinicCloud"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
