# -*- coding: utf-8 -*-
"""
Input Validation for Backend
=============================

Validaciones de seguridad para inputs del usuario en el backend.

Capa adicional de defensa (defense in depth):
- Frontend sanitiza para UX
- Backend valida para seguridad

NUNCA confíes en el frontend. Siempre valida en backend.
"""

import re
from typing import Optional, List, Tuple
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Valida email usando email-validator library.

    Args:
        email: Email a validar

    Returns:
        (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required"

    try:
        # Usar librería robusta de validación
        validated = validate_email_lib(email, check_deliverability=False)
        email_normalized = validated.normalized

        # Validaciones adicionales
        if len(email_normalized) > 254:
            return False, "Email too long (max 254 characters)"

        return True, None

    except EmailNotValidError as e:
        return False, str(e)


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Valida fortaleza de contraseña.

    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    - Máximo 128 caracteres

    Args:
        password: Contraseña a validar

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    if not password or not isinstance(password, str):
        return False, ["Password is required"]

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if len(password) > 128:
        errors.append("Password must not exceed 128 characters")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/]', password):
        errors.append("Password must contain at least one special character")

    # Prevenir contraseñas comunes (opcional pero recomendado)
    common_passwords = [
        "password", "12345678", "qwerty", "admin123", "letmein",
        "welcome", "monkey", "dragon", "master", "sunshine"
    ]

    if password.lower() in common_passwords:
        errors.append("Password is too common, please choose a stronger password")

    return len(errors) == 0, errors


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Valida nombre de usuario.

    Requisitos:
    - 3-50 caracteres
    - Solo alfanumérico, guiones y guiones bajos
    - No puede empezar/terminar con guión
    - No puede contener espacios

    Args:
        username: Nombre de usuario a validar

    Returns:
        (is_valid, error_message)
    """
    if not username or not isinstance(username, str):
        return False, "Username is required"

    # Limpiar espacios
    username = username.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 50:
        return False, "Username must not exceed 50 characters"

    # Solo permitir alfanumérico, guiones y guiones bajos
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9_-]{1,48}[a-zA-Z0-9])?$', username):
        return False, "Username can only contain letters, numbers, hyphens and underscores"

    return True, None


def sanitize_text_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitiza texto removiendo caracteres peligrosos.

    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima

    Returns:
        Texto sanitizado
    """
    if not text or not isinstance(text, str):
        return ""

    # Remover caracteres de control (excepto newline, tab, carriage return)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    # Remover null bytes
    text = text.replace('\x00', '')

    # Limitar longitud
    text = text[:max_length]

    # Trim
    return text.strip()


def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Valida query de búsqueda.

    Args:
        query: Query a validar

    Returns:
        (is_valid, error_message)
    """
    if not query or not isinstance(query, str):
        return False, "Search query is required"

    # Sanitizar
    query = sanitize_text_input(query, max_length=500)

    if len(query) < 2:
        return False, "Search query must be at least 2 characters long"

    if len(query) > 500:
        return False, "Search query must not exceed 500 characters"

    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Valida URL para prevenir javascript:, data:, etc.

    Args:
        url: URL a validar

    Returns:
        (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL is required"

    # Prevenir schemes peligrosos
    dangerous_schemes = re.compile(r'^(javascript|data|vbscript|file|about):', re.IGNORECASE)
    if dangerous_schemes.match(url):
        return False, "URL scheme not allowed"

    # Validar que sea http o https
    if not re.match(r'^https?://', url, re.IGNORECASE):
        return False, "URL must start with http:// or https://"

    # Limitar longitud
    if len(url) > 2048:
        return False, "URL too long (max 2048 characters)"

    return True, None


def validate_integer_range(
    value: int,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    field_name: str = "Value"
) -> Tuple[bool, Optional[str]]:
    """
    Valida que un entero esté en un rango.

    Args:
        value: Valor a validar
        min_value: Valor mínimo (opcional)
        max_value: Valor máximo (opcional)
        field_name: Nombre del campo para mensajes de error

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(value, int):
        return False, f"{field_name} must be an integer"

    if min_value is not None and value < min_value:
        return False, f"{field_name} must be at least {min_value}"

    if max_value is not None and value > max_value:
        return False, f"{field_name} must not exceed {max_value}"

    return True, None


def validate_enum_value(value: str, allowed_values: List[str], field_name: str = "Value") -> Tuple[bool, Optional[str]]:
    """
    Valida que un valor esté en una lista permitida.

    Args:
        value: Valor a validar
        allowed_values: Lista de valores permitidos
        field_name: Nombre del campo para mensajes de error

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"

    if value not in allowed_values:
        return False, f"{field_name} must be one of: {', '.join(allowed_values)}"

    return True, None


# Constantes para validaciones comunes
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 2000
MAX_COMMENT_LENGTH = 5000
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50
