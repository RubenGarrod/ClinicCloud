"""
MIDDLEWARE DE AUTENTICACIÓN
=========================

Este archivo contiene utilidades para proteger endpoints que requieren autenticación.
Proporciona decoradores y dependencias para FastAPI.

Comentarios en español para facilitar mantenimiento.
"""

import asyncpg
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Importar modelos y utilidades
from app.models.user import UserInDB, UserResponse
from app.models.auth import verify_token, AUTH_ERRORS
from app.db.database import get_database_connection

# Configurar esquema de seguridad Bearer Token
security = HTTPBearer(auto_error=False)


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

async def get_user_by_id(conn: asyncpg.Connection, user_id: str) -> Optional[UserInDB]:
    """
    Busca un usuario por ID en la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        user_id: ID del usuario a buscar
        
    Returns:
        UserInDB | None: Usuario si existe, None si no
    """
    query = """
        SELECT id, name, email, password_hash, avatar_url, 
               is_active, email_verified, created_at, updated_at
        FROM auth.users 
        WHERE id = $1 AND is_active = true
    """
    
    row = await conn.fetchrow(query, user_id)
    
    if row:
        return UserInDB(
            id=str(row['id']),
            name=row['name'],
            email=row['email'],
            password_hash=row['password_hash'],
            avatar_url=row['avatar_url'],
            is_active=row['is_active'],
            email_verified=row['email_verified'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    return None


async def verify_session_is_active(conn: asyncpg.Connection, token_hash: str) -> bool:
    """
    Verifica si una sesión sigue activa en la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        token_hash: Hash del token a verificar
        
    Returns:
        bool: True si la sesión está activa
    """
    query = """
        SELECT is_active 
        FROM auth.user_sessions 
        WHERE token_hash = $1 AND expires_at > NOW() AND is_active = true
    """
    
    row = await conn.fetchrow(query, token_hash)
    return row is not None


# =====================================================
# DEPENDENCIAS DE AUTENTICACIÓN
# =====================================================

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conn: asyncpg.Connection = Depends(get_database_connection)
) -> Optional[UserResponse]:
    """
    Dependencia que obtiene el usuario actual si está autenticado.
    NO lanza error si no hay token - retorna None.
    
    Útil para endpoints que tienen funcionalidad adicional para usuarios autenticados
    pero también funcionan sin autenticación.
    
    Args:
        credentials: Token Bearer del header Authorization
        conn: Conexión a la base de datos
        
    Returns:
        UserResponse | None: Usuario actual o None si no está autenticado
    """
    try:
        # Si no hay token, retornar None (sin error)
        if not credentials:
            return None
        
        # Verificar y decodificar token
        token_payload = verify_token(credentials.credentials)
        if not token_payload:
            return None
        
        # Buscar usuario en la BD
        user = await get_user_by_id(conn, token_payload["sub"])
        if not user:
            return None
        
        # Convertir a response público
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except Exception:
        # En caso de cualquier error, retornar None (sin autenticación)
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conn: asyncpg.Connection = Depends(get_database_connection)
) -> UserResponse:
    """
    Dependencia que requiere autenticación obligatoria.
    Lanza error HTTP 401 si no hay token válido.
    
    Usar esta dependencia en endpoints que REQUIEREN autenticación.
    
    Args:
        credentials: Token Bearer del header Authorization
        conn: Conexión a la base de datos
        
    Returns:
        UserResponse: Usuario actual autenticado
        
    Raises:
        HTTPException 401: Si no hay token o es inválido
    """
    # Verificar que se proporcione token
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTH_ERRORS["TOKEN_MISSING"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar y decodificar token
    token_payload = verify_token(credentials.credentials)
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTH_ERRORS["TOKEN_INVALID"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuario en la BD
    user = await get_user_by_id(conn, token_payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTH_ERRORS["USER_NOT_FOUND"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convertir a response público
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        email_verified=user.email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


async def get_current_user_with_session_check(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conn: asyncpg.Connection = Depends(get_database_connection)
) -> UserResponse:
    """
    Dependencia con verificación adicional de sesión en BD.
    Más segura pero con más overhead de base de datos.
    
    Usar solo en endpoints muy sensibles donde se requiera
    validación completa de la sesión.
    
    Args:
        credentials: Token Bearer del header Authorization
        conn: Conexión a la base de datos
        
    Returns:
        UserResponse: Usuario actual autenticado
        
    Raises:
        HTTPException 401: Si no hay token, es inválido o la sesión está invalidada
    """
    # Primero hacer la verificación básica
    user = await get_current_user(credentials, conn)
    
    # Verificar que la sesión siga activa en la BD
    from app.models.auth import create_token_hash
    token_hash = create_token_hash(credentials.credentials)
    
    session_active = await verify_session_is_active(conn, token_hash)
    if not session_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión invalidada",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# =====================================================
# DECORADORES DE PROTECCIÓN (OPCIONAL)
# =====================================================

def require_auth(func):
    """
    Decorador para proteger funciones que requieren autenticación.
    
    NOTA: En FastAPI es preferible usar las dependencias arriba,
    pero este decorador puede ser útil para funciones auxiliares.
    
    Example:
        @require_auth
        async def mi_funcion_protegida(user: UserResponse):
            # Esta función solo se ejecuta si el usuario está autenticado
            pass
    """
    from functools import wraps
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Buscar el parámetro 'user' en kwargs
        user = kwargs.get('user')
        if not user or not isinstance(user, UserResponse):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["TOKEN_MISSING"]
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


# =====================================================
# UTILIDADES ADICIONALES
# =====================================================

def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extrae el ID de usuario de un token JWT sin verificar la firma.
    
    ADVERTENCIA: Solo usar para logs o casos donde no se requiera seguridad.
    Para autenticación real usar siempre verify_token().
    
    Args:
        token: Token JWT
        
    Returns:
        str | None: ID del usuario o None si el token es inválido
    """
    try:
        import jwt
        # Decodificar sin verificar (solo para extraer datos)
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("sub")
    except Exception:
        return None


async def count_active_sessions(conn: asyncpg.Connection, user_id: str) -> int:
    """
    Cuenta las sesiones activas de un usuario.
    
    Args:
        conn: Conexión a la base de datos
        user_id: ID del usuario
        
    Returns:
        int: Número de sesiones activas
    """
    query = """
        SELECT COUNT(*) 
        FROM auth.user_sessions 
        WHERE user_id = $1 AND is_active = true AND expires_at > NOW()
    """
    
    result = await conn.fetchval(query, user_id)
    return result or 0


async def invalidate_all_user_sessions(conn: asyncpg.Connection, user_id: str) -> int:
    """
    Invalida todas las sesiones de un usuario.
    Útil para "logout everywhere" o cuando se compromete una cuenta.
    
    Args:
        conn: Conexión a la base de datos
        user_id: ID del usuario
        
    Returns:
        int: Número de sesiones invalidadas
    """
    query = """
        UPDATE auth.user_sessions 
        SET is_active = false 
        WHERE user_id = $1 AND is_active = true
    """
    
    result = await conn.execute(query, user_id)
    # Extraer número de filas afectadas del resultado
    return int(result.split()[-1]) if result else 0


async def cleanup_expired_sessions(conn: asyncpg.Connection) -> int:
    """
    Limpia sesiones expiradas de la base de datos.
    Se puede ejecutar periódicamente como tarea de mantenimiento.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        int: Número de sesiones eliminadas
    """
    query = """
        DELETE FROM auth.user_sessions 
        WHERE expires_at < NOW() - INTERVAL '7 days'
    """
    
    result = await conn.execute(query)
    return int(result.split()[-1]) if result else 0


# =====================================================
# CONSTANTES Y CONFIGURACIÓN
# =====================================================

# Headers de respuesta para autenticación
AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}

# Rutas que NO requieren autenticación (whitelist)
PUBLIC_ROUTES = {
    "/auth/login",
    "/auth/register", 
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/"
}

# Rutas que requieren autenticación OBLIGATORIA
PROTECTED_ROUTES = {
    "/auth/logout",
    "/auth/verify",
    "/user/profile",
    "/user/update",
    "/user/sessions"
}


def is_public_route(path: str) -> bool:
    """
    Verifica si una ruta es pública (no requiere autenticación).
    
    Args:
        path: Ruta de la request
        
    Returns:
        bool: True si la ruta es pública
    """
    return path in PUBLIC_ROUTES or path.startswith("/api/docs")


def requires_auth(path: str) -> bool:
    """
    Verifica si una ruta requiere autenticación obligatoria.
    
    Args:
        path: Ruta de la request
        
    Returns:
        bool: True si la ruta requiere autenticación
    """
    return path in PROTECTED_ROUTES or path.startswith("/admin")