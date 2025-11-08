"""
DEPENDENCIAS DE AUTENTICACIÓN
==============================

Funciones de dependencia para proteger rutas que requieren autenticación.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.models.user import UserResponse, UserInDB
from app.models.auth import verify_token
from app.db.database import execute_query

# Esquema de seguridad Bearer Token
security = HTTPBearer(auto_error=False)


def get_user_by_id(user_id) -> Optional[UserInDB]:
    """
    Busca un usuario por ID en la base de datos.

    Args:
        user_id: ID del usuario (puede ser int o string)

    Returns:
        UserInDB | None: Usuario si existe, None si no
    """
    query = """
        SELECT id, name, email, password_hash, title, country, region, avatar_url, avatar_icon, avatar_color,
               institution, specialty, language,
               is_active, email_verified, created_at, updated_at, last_login
        FROM auth.users
        WHERE id = %s AND is_active = true
    """

    # Convertir a int si es string
    try:
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
    except (ValueError, TypeError):
        return None

    row = execute_query(query, (user_id_int,), fetchone=True)

    if row:
        return UserInDB(
            id=str(row[0]),
            name=row[1],
            email=row[2],
            password_hash=row[3],
            title=row[4],
            country=row[5],
            region=row[6],
            avatar_url=row[7],
            avatar_icon=row[8],
            avatar_color=row[9],
            institution=row[10],
            specialty=row[11],
            language=row[12],
            is_active=row[13],
            email_verified=row[14],
            created_at=row[15],
            updated_at=row[16],
            last_login=row[17]
        )

    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """
    Dependencia que obtiene el usuario actual desde el token JWT.

    Args:
        credentials: Credenciales Bearer del header Authorization

    Returns:
        UserResponse: Usuario autenticado

    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionaron credenciales de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar y decodificar el token
    token_data = verify_token(credentials.credentials)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar el usuario en la base de datos
    # El token JWT usa 'sub' (subject) como campo estándar para el user_id
    if isinstance(token_data, dict):
        user_id = token_data.get('sub') or token_data.get('user_id')
    else:
        user_id = getattr(token_data, 'sub', None) or getattr(token_data, 'user_id', None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene ID de usuario válido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convertir a UserResponse (sin datos sensibles)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        avatar_icon=user.avatar_icon,
        avatar_color=user.avatar_color,
        institution=user.institution,
        specialty=user.specialty,
        language=user.language,
        is_active=user.is_active,
        email_verified=user.email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserResponse]:
    """
    Dependencia que obtiene el usuario actual si está autenticado.
    Si no hay token, devuelve None en lugar de lanzar excepción.

    Útil para endpoints que funcionan tanto con usuarios logueados como anónimos.

    Args:
        credentials: Credenciales Bearer del header Authorization

    Returns:
        UserResponse | None: Usuario autenticado o None
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"get_current_user_optional - credentials received: {credentials is not None}")

    if not credentials:
        logger.info("No credentials provided, returning None")
        return None

    try:
        user = await get_current_user(credentials)
        logger.info(f"User authenticated: {user.email if user else 'None'}")
        return user
    except HTTPException as e:
        logger.warning(f"Authentication failed: {e.detail}")
        return None
