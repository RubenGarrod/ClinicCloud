# -*- coding: utf-8 -*-
"""
Session Manager - Token Validation with Database
=================================================

Gestiona sesiones activas y validación de tokens JWT en base de datos.

Funcionalidades:
- Registro de nuevos tokens al login
- Validación de tokens activos
- Revocación de tokens (logout)
- Limpieza de sesiones expiradas
- Límite de sesiones simultáneas
- Detección de actividad sospechosa

Uso:
    from app.core.session_manager import SessionManager

    # Al login
    await SessionManager.create_session(user_id, token, request)

    # Al validar token
    is_valid = await SessionManager.validate_token(token)

    # Al logout
    await SessionManager.revoke_token(token)
"""

import hashlib
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import Request

from app.db.pool import fetch_one, fetch_all, execute

logger = logging.getLogger(__name__)


class SessionManager:
    """Gestión de sesiones activas con tokens JWT en base de datos."""

    @staticmethod
    def _hash_token(token: str) -> str:
        """
        Hashea el token JWT con SHA-256 para almacenamiento seguro.

        No almacenamos el token completo en BD por seguridad.
        Si la BD se compromete, los tokens no son legibles.
        """
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def _parse_user_agent(user_agent: str) -> Dict[str, Any]:
        """
        Parsea User-Agent para extraer info del dispositivo.

        Retorna un diccionario con device, os, browser.
        Esto es una implementación simple - para producción
        considerar usar una librería como user-agents.
        """
        ua = user_agent.lower()

        # Detectar dispositivo
        if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
            device = 'mobile'
        elif 'tablet' in ua or 'ipad' in ua:
            device = 'tablet'
        else:
            device = 'desktop'

        # Detectar OS
        if 'windows' in ua:
            os_name = 'Windows'
        elif 'mac os' in ua or 'macos' in ua:
            os_name = 'macOS'
        elif 'linux' in ua:
            os_name = 'Linux'
        elif 'android' in ua:
            os_name = 'Android'
        elif 'ios' in ua or 'iphone' in ua or 'ipad' in ua:
            os_name = 'iOS'
        else:
            os_name = 'Unknown'

        # Detectar browser
        if 'chrome' in ua and 'edg' not in ua:
            browser = 'Chrome'
        elif 'firefox' in ua:
            browser = 'Firefox'
        elif 'safari' in ua and 'chrome' not in ua:
            browser = 'Safari'
        elif 'edg' in ua:
            browser = 'Edge'
        else:
            browser = 'Other'

        return {
            'device': device,
            'os': os_name,
            'browser': browser
        }

    @staticmethod
    async def create_session(
        user_id: int,
        token: str,
        request: Request,
        expires_at: datetime,
        token_type: str = 'access'
    ) -> bool:
        """
        Crea una nueva sesión en la base de datos.

        Args:
            user_id: ID del usuario (integer)
            token: Token JWT completo
            request: FastAPI Request object
            expires_at: Fecha de expiración del token
            token_type: 'access' o 'refresh'

        Returns:
            True si se creó exitosamente
        """
        try:
            token_hash = SessionManager._hash_token(token)

            # Obtener IP del cliente
            client_ip = request.client.host if request.client else None
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()

            # Obtener User-Agent
            user_agent = request.headers.get("User-Agent", "")
            device_info = SessionManager._parse_user_agent(user_agent)

            # Insertar en BD
            query = """
                INSERT INTO auth.active_sessions (
                    user_id,
                    token_hash,
                    token_type,
                    expires_at,
                    ip_address,
                    user_agent,
                    device_info
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """

            result = await fetch_one(
                query,
                user_id,
                token_hash,
                token_type,
                expires_at,
                client_ip,
                user_agent[:500] if user_agent else None,  # Limitar longitud
                json.dumps(device_info) if device_info else None  # Convertir dict a JSON
            )

            if result:
                logger.info(f"Session created for user {user_id} from {client_ip}")

                # Aplicar límite de sesiones (máximo 5 por usuario)
                await SessionManager._enforce_session_limit(user_id, max_sessions=5)

                return True

            return False

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return False

    @staticmethod
    async def validate_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Valida si un token está activo en la base de datos.

        Args:
            token: Token JWT completo

        Returns:
            Información de la sesión si es válida, None si no
        """
        try:
            token_hash = SessionManager._hash_token(token)

            query = """
                SELECT
                    id,
                    user_id,
                    created_at,
                    expires_at,
                    ip_address,
                    device_info
                FROM auth.active_sessions
                WHERE
                    token_hash = $1
                    AND is_active = TRUE
                    AND expires_at > NOW()
                LIMIT 1
            """

            session = await fetch_one(query, token_hash)

            if session:
                # Actualizar last_used_at
                await execute(
                    "UPDATE auth.active_sessions SET last_used_at = NOW() WHERE id = $1",
                    session['id']
                )

                return dict(session)

            return None

        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None

    @staticmethod
    async def revoke_token(token: str, reason: str = 'logout') -> bool:
        """
        Revoca un token específico (logout).

        Args:
            token: Token JWT completo
            reason: Razón de revocación

        Returns:
            True si se revocó exitosamente
        """
        try:
            token_hash = SessionManager._hash_token(token)

            query = """
                UPDATE auth.active_sessions
                SET
                    is_active = FALSE,
                    revoked_at = NOW(),
                    revoked_reason = $2
                WHERE
                    token_hash = $1
                    AND is_active = TRUE
            """

            result = await execute(query, token_hash, reason)

            # El result es el status string como "UPDATE 1"
            success = "UPDATE 1" in str(result)

            if success:
                logger.info(f"Token revoked: {reason}")

            return success

        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

    @staticmethod
    async def revoke_all_user_sessions(user_id: int, reason: str = 'security') -> int:
        """
        Revoca todas las sesiones de un usuario.

        Útil cuando:
        - El usuario cambia su contraseña
        - Se detecta actividad sospechosa
        - El usuario solicita cerrar todas las sesiones

        Args:
            user_id: ID del usuario (integer)
            reason: Razón de revocación

        Returns:
            Número de sesiones revocadas
        """
        try:
            query = """
                UPDATE auth.active_sessions
                SET
                    is_active = FALSE,
                    revoked_at = NOW(),
                    revoked_reason = $2
                WHERE
                    user_id = $1
                    AND is_active = TRUE
            """

            result = await execute(query, user_id, reason)

            # Extraer número de filas afectadas del status string
            count = int(result.split()[-1]) if result and len(result.split()) > 1 else 0

            logger.info(f"Revoked {count} sessions for user {user_id}: {reason}")

            return count

        except Exception as e:
            logger.error(f"Error revoking user sessions: {e}")
            return 0

    @staticmethod
    async def get_active_sessions(user_id: int) -> list:
        """
        Obtiene todas las sesiones activas de un usuario.

        Args:
            user_id: ID del usuario (integer)

        Returns:
            Lista de sesiones activas
        """
        try:
            query = """
                SELECT
                    id,
                    created_at,
                    last_used_at,
                    expires_at,
                    ip_address,
                    user_agent,
                    device_info
                FROM auth.active_sessions
                WHERE
                    user_id = $1
                    AND is_active = TRUE
                    AND expires_at > NOW()
                ORDER BY last_used_at DESC NULLS LAST
            """

            sessions = await fetch_all(query, user_id)

            return [dict(s) for s in sessions] if sessions else []

        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []

    @staticmethod
    async def cleanup_expired_sessions() -> int:
        """
        Limpia sesiones expiradas.

        Esta función debe ejecutarse periódicamente (ej: cada hora).

        Returns:
            Número de sesiones limpiadas
        """
        try:
            query = """
                UPDATE auth.active_sessions
                SET
                    is_active = FALSE,
                    revoked_at = NOW(),
                    revoked_reason = 'expired'
                WHERE
                    is_active = TRUE
                    AND expires_at < NOW()
            """

            result = await execute(query)

            count = int(result.split()[-1]) if result and len(result.split()) > 1 else 0

            if count > 0:
                logger.info(f"Cleaned up {count} expired sessions")

            # Opcional: Eliminar sesiones muy antiguas (más de 30 días)
            delete_query = """
                DELETE FROM auth.active_sessions
                WHERE
                    is_active = FALSE
                    AND revoked_at < NOW() - INTERVAL '30 days'
            """

            await execute(delete_query)

            return count

        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            return 0

    @staticmethod
    async def _enforce_session_limit(user_id: int, max_sessions: int = 5) -> int:
        """
        Limita el número de sesiones simultáneas por usuario.

        Revoca las sesiones más antiguas si se excede el límite.

        Args:
            user_id: ID del usuario (integer)
            max_sessions: Número máximo de sesiones permitidas

        Returns:
            Número de sesiones revocadas
        """
        try:
            # Contar sesiones activas
            count_query = """
                SELECT COUNT(*)
                FROM auth.active_sessions
                WHERE
                    user_id = $1
                    AND is_active = TRUE
                    AND token_type = 'access'
            """

            result = await fetch_one(count_query, user_id)
            current_count = result['count'] if result else 0

            if current_count <= max_sessions:
                return 0

            # Revocar sesiones antiguas
            revoke_query = """
                WITH sessions_to_revoke AS (
                    SELECT id
                    FROM auth.active_sessions
                    WHERE
                        user_id = $1
                        AND is_active = TRUE
                        AND token_type = 'access'
                    ORDER BY last_used_at ASC NULLS FIRST, created_at ASC
                    OFFSET $2
                )
                UPDATE auth.active_sessions
                SET
                    is_active = FALSE,
                    revoked_at = NOW(),
                    revoked_reason = 'session_limit_exceeded'
                WHERE id IN (SELECT id FROM sessions_to_revoke)
            """

            result = await execute(revoke_query, user_id, max_sessions)

            count = int(result.split()[-1]) if result and len(result.split()) > 1 else 0

            if count > 0:
                logger.info(f"Revoked {count} old sessions for user {user_id} (limit: {max_sessions})")

            return count

        except Exception as e:
            logger.error(f"Error enforcing session limit: {e}")
            return 0
