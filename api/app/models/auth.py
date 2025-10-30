"""
MÓDULO DE AUTENTICACIÓN Y SEGURIDAD
==================================

Este archivo contiene todas las utilidades de autenticación:
- Hashing de contraseñas con bcrypt
- Generación y validación de tokens JWT
- Utilidades de seguridad

Comentarios en español para facilitar mantenimiento.
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import jwt
import bcrypt
from pydantic import BaseModel


# =====================================================
# CONFIGURACIÓN DE SEGURIDAD
# =====================================================

# Secreto para firmar JWT - OBLIGATORIO desde variable de entorno
JWT_SECRET_KEY = os.getenv("JWT_SECRET")

if not JWT_SECRET_KEY:
    raise ValueError(
        "⚠️ ERROR CRÍTICO: JWT_SECRET no está configurado.\n"
        "Por seguridad, NO se permite usar un valor por defecto.\n\n"
        "Solución:\n"
        "1. Genera un secret seguro:\n"
        "   python3 -c \"import secrets; print(secrets.token_urlsafe(64))\"\n\n"
        "2. Añádelo a tu archivo .env:\n"
        "   JWT_SECRET=el_secret_que_generaste\n\n"
        "3. Reinicia la aplicación.\n"
    )

# Validar que no sea el valor de ejemplo
if "CAMBIAR_ESTO" in JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    raise ValueError(
        "⚠️ ERROR CRÍTICO: JWT_SECRET parece ser un valor de ejemplo o muy corto.\n"
        "Debe ser un secret aleatorio de al menos 32 caracteres.\n\n"
        "Genera uno nuevo:\n"
        "python3 -c \"import secrets; print(secrets.token_urlsafe(64))\"\n"
    )

# Algoritmo para JWT (recomendado HS256 para aplicaciones simples)
JWT_ALGORITHM = "HS256"

# Tiempo de expiración del token en horas
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# Rounds de bcrypt para hashing (más alto = más seguro pero más lento)
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))


# =====================================================
# UTILIDADES PARA CONTRASEÑAS
# =====================================================

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña para almacenar en BD
        
    Example:
        >>> hashed = hash_password("mi_password_123")
        >>> print(hashed)  # $2b$12$...
    """
    # Convertir string a bytes
    password_bytes = password.encode('utf-8')
    
    # Generar salt y hashear
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retornar como string
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        password: Contraseña en texto plano
        hashed_password: Hash almacenado en la BD
        
    Returns:
        bool: True si la contraseña es correcta
        
    Example:
        >>> is_valid = verify_password("mi_password_123", stored_hash)
        >>> print(is_valid)  # True o False
    """
    try:
        # Convertir a bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verificar con bcrypt
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # Si hay cualquier error, la contraseña es inválida
        return False


def generate_random_password(length: int = 12) -> str:
    """
    Genera una contraseña aleatoria segura.
    Útil para passwords temporales o reseteo.
    
    Args:
        length: Longitud de la contraseña (mínimo 8)
        
    Returns:
        str: Contraseña aleatoria
    """
    if length < 8:
        length = 8
    
    # Caracteres permitidos
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    
    # Generar contraseña aleatoria
    password = ''.join(secrets.choice(chars) for _ in range(length))
    
    # Asegurar que tenga al menos una letra y un número
    if not any(c.isalpha() for c in password):
        password = password[:-1] + secrets.choice("abcdefghijklmnopqrstuvwxyz")
    if not any(c.isdigit() for c in password):
        password = password[:-1] + secrets.choice("0123456789")
    
    return password


# =====================================================
# UTILIDADES PARA JWT TOKENS
# =====================================================

def create_access_token(user_id: str, user_email: str) -> dict:
    """
    Crea un token JWT para un usuario.
    
    Args:
        user_id: ID único del usuario
        user_email: Email del usuario
        
    Returns:
        dict: Token y metadatos
        
    Example:
        >>> token_data = create_access_token("uuid-123", "user@email.com")
        >>> print(token_data["access_token"])
    """
    # Calcular tiempo de expiración
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=JWT_EXPIRE_HOURS)
    
    # Payload del token (mantener mínimo por tamaño)
    payload = {
        "sub": user_id,          # Subject (estándar JWT)
        "email": user_email,     # Email para referencia
        "iat": int(now.timestamp()),      # Issued at (cuándo se creó)
        "exp": int(expires_at.timestamp()), # Expiration time
        "type": "access"         # Tipo de token
    }
    
    # Generar token JWT
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_HOURS * 3600,  # En segundos
        "expires_at": expires_at.isoformat()
    }


def verify_token(token: str) -> Optional[dict]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        dict | None: Payload del token si es válido, None si no
        
    Example:
        >>> payload = verify_token("eyJ...")
        >>> if payload:
        ...     user_id = payload["sub"]
    """
    try:
        # Decodificar y verificar token
        payload = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM]
        )
        
        # Verificar que sea un token de acceso
        if payload.get("type") != "access":
            return None
            
        # Verificar que tenga los campos requeridos
        if not payload.get("sub") or not payload.get("email"):
            return None
            
        return payload
        
    except jwt.ExpiredSignatureError:
        # Token expirado
        return None
    except jwt.InvalidTokenError:
        # Token inválido (malformado, firma incorrecta, etc.)
        return None
    except Exception:
        # Cualquier otro error
        return None


def extract_token_from_header(authorization_header: str) -> Optional[str]:
    """
    Extrae el token del header Authorization.
    
    Args:
        authorization_header: Header "Bearer <token>"
        
    Returns:
        str | None: Token limpio o None si formato incorrecto
        
    Example:
        >>> token = extract_token_from_header("Bearer eyJ...")
        >>> print(token)  # "eyJ..."
    """
    if not authorization_header:
        return None
    
    # Formato esperado: "Bearer <token>"
    parts = authorization_header.split(" ")
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


def create_token_hash(token: str) -> str:
    """
    Crea un hash del token para almacenar en BD.
    Útil para invalidar tokens sin almacenar el token completo.
    
    Args:
        token: Token JWT completo
        
    Returns:
        str: Hash SHA256 del token
    """
    return hashlib.sha256(token.encode()).hexdigest()


# =====================================================
# UTILIDADES DE VALIDACIÓN
# =====================================================

def is_token_expired(token_payload: dict) -> bool:
    """
    Verifica si un token ha expirado.
    
    Args:
        token_payload: Payload decodificado del token
        
    Returns:
        bool: True si el token ha expirado
    """
    exp_timestamp = token_payload.get("exp")
    if not exp_timestamp:
        return True  # Sin expiración = considerarlo expirado
    
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    
    return now >= exp_datetime


def get_token_remaining_time(token_payload: dict) -> Optional[timedelta]:
    """
    Calcula el tiempo restante antes de que expire un token.
    
    Args:
        token_payload: Payload decodificado del token
        
    Returns:
        timedelta | None: Tiempo restante o None si ya expiró
    """
    exp_timestamp = token_payload.get("exp")
    if not exp_timestamp:
        return None
    
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    
    if now >= exp_datetime:
        return None  # Ya expiró
    
    return exp_datetime - now


# =====================================================
# UTILIDADES PARA RATE LIMITING
# =====================================================

def generate_rate_limit_key(ip: str, identifier: str = "") -> str:
    """
    Genera una clave para rate limiting.
    Combina IP y opcionalmente otro identificador.
    
    Args:
        ip: Dirección IP
        identifier: Identificador adicional (email, user_id, etc.)
        
    Returns:
        str: Clave única para rate limiting
    """
    if identifier:
        return f"rate_limit:{ip}:{identifier}"
    return f"rate_limit:{ip}"


# =====================================================
# MODELOS PARA RESPUESTAS DE ERROR
# =====================================================

class AuthError(BaseModel):
    """Modelo para errores de autenticación"""
    error: str
    message: str
    details: Optional[dict] = None


class TokenError(AuthError):
    """Error específico de tokens"""
    error: str = "token_error"


class CredentialsError(AuthError):
    """Error de credenciales inválidas"""
    error: str = "invalid_credentials"


class RateLimitError(AuthError):
    """Error de demasiados intentos"""
    error: str = "rate_limit_exceeded"


# =====================================================
# CONSTANTES DE ERRORES
# =====================================================

# Mensajes de error en español
AUTH_ERRORS = {
    "INVALID_CREDENTIALS": "Email o contraseña incorrectos",
    "USER_NOT_FOUND": "Usuario no encontrado",
    "USER_INACTIVE": "Cuenta desactivada",
    "EMAIL_NOT_VERIFIED": "Email no verificado",
    "TOKEN_EXPIRED": "Token expirado",
    "TOKEN_INVALID": "Token inválido",
    "TOKEN_MISSING": "Token de autorización requerido",
    "INSUFFICIENT_PERMISSIONS": "Permisos insuficientes",
    "RATE_LIMIT_EXCEEDED": "Demasiados intentos, intenta más tarde",
    "PASSWORD_TOO_WEAK": "Contraseña muy débil",
    "EMAIL_ALREADY_EXISTS": "Este email ya está registrado",
    "REGISTRATION_DISABLED": "Registro de usuarios deshabilitado",
    "OAUTH_ERROR": "Error en autenticación con proveedor externo"
}


# =====================================================
# FUNCIONES DE UTILIDAD ADICIONALES
# =====================================================

def mask_email(email: str) -> str:
    """
    Enmascara un email para logs (privacidad).
    
    Args:
        email: Email completo
        
    Returns:
        str: Email enmascarado
        
    Example:
        >>> masked = mask_email("usuario@email.com")
        >>> print(masked)  # "u****o@e****.com"
    """
    if not email or "@" not in email:
        return "***"
    
    local, domain = email.split("@", 1)
    
    # Enmascarar parte local
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    
    # Enmascarar dominio
    if "." in domain:
        domain_parts = domain.split(".")
        domain_name = domain_parts[0]
        domain_ext = ".".join(domain_parts[1:])
        
        if len(domain_name) <= 2:
            masked_domain = "*" * len(domain_name) + "." + domain_ext
        else:
            masked_domain = domain_name[0] + "*" * (len(domain_name) - 2) + domain_name[-1] + "." + domain_ext
    else:
        masked_domain = "*" * len(domain)
    
    return f"{masked_local}@{masked_domain}"


def get_client_ip(request_headers: dict) -> str:
    """
    Extrae la IP del cliente considerando proxies.
    
    Args:
        request_headers: Headers de la request
        
    Returns:
        str: IP del cliente
    """
    # Verificar headers de proxy en orden de prioridad
    ip_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Client-IP',
        'CF-Connecting-IP'  # Cloudflare
    ]
    
    for header in ip_headers:
        ip = request_headers.get(header)
        if ip:
            # X-Forwarded-For puede tener múltiples IPs separadas por coma
            return ip.split(',')[0].strip()
    
    # Fallback a IP directa (puede ser del proxy)
    return request_headers.get('host', 'unknown')