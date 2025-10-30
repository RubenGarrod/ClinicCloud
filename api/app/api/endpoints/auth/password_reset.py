"""
ENDPOINTS DE RECUPERACIÓN DE CONTRASEÑA
========================================

Endpoints para el flujo de recuperación de contraseña:
1. Solicitar reset (envía email con token)
2. Verificar token
3. Establecer nueva contraseña

Comentarios en español para facilitar mantenimiento.
"""

import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Importar utilidades
from app.db.database import execute_query
from app.models.auth import hash_password
from app.services.email_service import email_service

router = APIRouter()


# ============================================
# MODELOS PYDANTIC
# ============================================

class ForgotPasswordRequest(BaseModel):
    """Request para solicitar recuperación de contraseña"""
    email: EmailStr = Field(..., description="Email del usuario")


class VerifyResetTokenRequest(BaseModel):
    """Request para verificar si un token es válido"""
    token: str = Field(..., min_length=32, description="Token de reset")


class ResetPasswordRequest(BaseModel):
    """Request para establecer nueva contraseña"""
    token: str = Field(..., min_length=32, description="Token de reset")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")


class MessageResponse(BaseModel):
    """Respuesta genérica con mensaje"""
    message: str


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def generate_reset_token() -> str:
    """
    Genera un token seguro y único para reset de contraseña.
    Usa secrets.token_urlsafe() que es criptográficamente seguro.
    """
    return secrets.token_urlsafe(32)  # Genera token de 43 caracteres


def create_password_reset_token(
    user_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> str:
    """
    Crea un token de reset de contraseña en la base de datos.

    Args:
        user_id: ID del usuario
        ip_address: IP desde donde se solicita (opcional)
        user_agent: User agent del navegador (opcional)

    Returns:
        str: Token generado

    Raises:
        Exception: Si hay error al crear el token
    """
    token = generate_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # Válido por 1 hora

    query = """
        INSERT INTO auth.password_reset_tokens (user_id, token, expires_at, ip_address, user_agent)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """

    result = execute_query(
        query,
        (user_id, token, expires_at, ip_address, user_agent),
        fetchone=True,
        commit=True
    )

    if not result:
        raise Exception("Failed to create reset token")

    return token


def get_user_by_reset_token(token: str) -> Optional[dict]:
    """
    Obtiene el usuario asociado a un token de reset válido.

    Args:
        token: Token de reset

    Returns:
        dict: Datos del usuario si el token es válido, None en caso contrario

    Validaciones:
    - Token existe
    - Token no ha expirado
    - Token no ha sido usado
    """
    query = """
        SELECT
            u.id,
            u.email,
            u.name,
            prt.expires_at,
            prt.used_at
        FROM auth.password_reset_tokens prt
        INNER JOIN auth.users u ON prt.user_id = u.id
        WHERE prt.token = %s
        LIMIT 1
    """

    row = execute_query(query, (token,), fetchone=True)

    if not row:
        return None

    user_id, email, name, expires_at, used_at = row

    # Verificar que no haya expirado
    if expires_at < datetime.now(timezone.utc):
        return None

    # Verificar que no haya sido usado
    if used_at is not None:
        return None

    return {
        "id": user_id,
        "email": email,
        "name": name
    }


def mark_token_as_used(token: str) -> bool:
    """
    Marca un token como usado para que no pueda reutilizarse.

    Args:
        token: Token a marcar como usado

    Returns:
        bool: True si se marcó correctamente
    """
    query = """
        UPDATE auth.password_reset_tokens
        SET used_at = NOW()
        WHERE token = %s AND used_at IS NULL
    """

    execute_query(query, (token,), fetchall=False, commit=True)
    return True


def invalidate_user_reset_tokens(user_id: int) -> None:
    """
    Invalida todos los tokens de reset activos de un usuario.
    Útil cuando se cambia la contraseña exitosamente.

    Args:
        user_id: ID del usuario
    """
    query = """
        UPDATE auth.password_reset_tokens
        SET used_at = NOW()
        WHERE user_id = %s AND used_at IS NULL
    """

    execute_query(query, (user_id,), fetchall=False, commit=True)


# ============================================
# ENDPOINTS
# ============================================

@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest, req: Request):
    """
    Endpoint para solicitar recuperación de contraseña.

    Flujo:
    1. Verifica que el email exista
    2. Genera token de reset
    3. Envía email con link de recuperación

    IMPORTANTE: Siempre retorna éxito aunque el email no exista
    (por seguridad, para no revelar qué emails están registrados)
    """
    try:
        # Buscar usuario por email
        query = "SELECT id, name, email FROM auth.users WHERE email = %s AND is_active = true"
        user = execute_query(query, (request.email,), fetchone=True)

        # Si el usuario existe, crear token y enviar email
        if user:
            user_id, user_name, user_email = user

            # Obtener información de la request
            ip_address = req.client.host if req.client else None
            user_agent = req.headers.get("user-agent")

            # Crear token de reset
            reset_token = create_password_reset_token(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )

            # Enviar email
            email_sent = email_service.send_password_reset_email(
                to_email=user_email,
                user_name=user_name,
                reset_token=reset_token
            )

            if not email_sent:
                print(f"Failed to send reset email to {user_email}")
                # No lanzar error para no revelar si el email existe

        # SIEMPRE retornar éxito (incluso si el email no existe)
        # Esto previene que atacantes descubran qué emails están registrados
        return MessageResponse(
            message="Si el email existe, recibirás un link de recuperación en breve."
        )

    except Exception as e:
        print(f"Error in forgot_password: {str(e)}")
        # Retornar mensaje genérico incluso en caso de error
        return MessageResponse(
            message="Si el email existe, recibirás un link de recuperación en breve."
        )


@router.post("/verify-reset-token", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def verify_reset_token(request: VerifyResetTokenRequest):
    """
    Endpoint para verificar si un token de reset es válido.

    Útil para la UI, para mostrar el formulario de nueva contraseña
    solo si el token es válido.
    """
    user = get_user_by_reset_token(request.token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )

    return MessageResponse(
        message=f"Token válido para {user['email']}"
    )


@router.post("/reset-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def reset_password(request: ResetPasswordRequest):
    """
    Endpoint para establecer una nueva contraseña usando el token de reset.

    Flujo:
    1. Verifica que el token sea válido
    2. Hashea la nueva contraseña
    3. Actualiza la contraseña del usuario
    4. Invalida el token y todos los demás tokens del usuario
    """
    try:
        # Verificar token y obtener usuario
        user = get_user_by_reset_token(request.token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado"
            )

        # Hashear nueva contraseña
        hashed_password = hash_password(request.new_password)

        # Actualizar contraseña del usuario
        update_query = """
            UPDATE auth.users
            SET password_hash = %s,
                updated_at = NOW()
            WHERE id = %s
        """

        execute_query(update_query, (hashed_password, user['id']), fetchall=False, commit=True)

        # Marcar token como usado
        mark_token_as_used(request.token)

        # Invalidar todos los demás tokens de reset del usuario
        invalidate_user_reset_tokens(user['id'])

        return MessageResponse(
            message="Contraseña actualizada correctamente. Ya puedes iniciar sesión."
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in reset_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al restablecer la contraseña"
        )
