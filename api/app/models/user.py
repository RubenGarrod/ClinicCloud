"""
MODELOS DE USUARIO PARA EL SISTEMA DE AUTENTICACIÓN
===================================================

Este archivo define los modelos Pydantic para manejo de usuarios.
Los modelos se usan para validación de datos y serialización JSON.

Comentarios en español para facilitar mantenimiento y comprensión.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


# =====================================================
# MODELOS PARA REQUESTS (Lo que recibe la API)
# =====================================================

class UserRegisterRequest(BaseModel):
    """
    Modelo para registro de nuevos usuarios.
    Define qué datos son obligatorios al registrarse.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Email único para login")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña en texto plano")
    institution: Optional[str] = Field(None, max_length=255, description="Institución médica")
    specialty: Optional[str] = Field(None, max_length=255, description="Especialidad médica")
    language: Optional[str] = Field('es', description="Idioma preferido (es/en)")

    @validator('name')
    def validate_name(cls, v):
        """Valida que el nombre contenga solo letras, espacios y algunos caracteres especiales"""
        if not re.match(r'^[a-zA-ZáéíóúñÑ\s\-\.]+$', v.strip()):
            raise ValueError('El nombre solo puede contener letras, espacios, guiones y puntos')
        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        """Valida que la contraseña tenga al menos una letra y un número"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

    @validator('language')
    def validate_language(cls, v):
        """Valida que el idioma sea uno de los soportados"""
        if v and v not in ['es', 'en']:
            raise ValueError('El idioma debe ser "es" o "en"')
        return v


class UserLoginRequest(BaseModel):
    """
    Modelo para login de usuarios existentes.
    Solo requiere email y contraseña.
    """
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")


class UserUpdateRequest(BaseModel):
    """
    Modelo para actualización de datos de usuario.
    Todos los campos son opcionales.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nuevo nombre")
    title: Optional[str] = Field(None, max_length=50, description="Título profesional (Dr., Dra., etc.)")
    country: Optional[str] = Field(None, max_length=100, description="País")
    region: Optional[str] = Field(None, max_length=100, description="Región/Estado")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL del avatar")
    avatar_icon: Optional[str] = Field(None, max_length=50, description="ID del icono de avatar")
    avatar_color: Optional[str] = Field(None, max_length=50, description="ID del color de avatar")
    institution: Optional[str] = Field(None, max_length=255, description="Institución médica")
    specialty: Optional[str] = Field(None, max_length=255, description="Especialidad médica")
    language: Optional[str] = Field(None, description="Idioma preferido (es/en)")

    @validator('name')
    def validate_name(cls, v):
        """Valida el nombre si se proporciona"""
        if v is not None:
            if not re.match(r'^[a-zA-ZáéíóúñÑ\s\-\.]+$', v.strip()):
                raise ValueError('El nombre solo puede contener letras, espacios, guiones y puntos')
            return v.strip()
        return v

    @validator('language')
    def validate_language(cls, v):
        """Valida que el idioma sea uno de los soportados"""
        if v and v not in ['es', 'en']:
            raise ValueError('El idioma debe ser "es" o "en"')
        return v


class ChangePasswordRequest(BaseModel):
    """
    Modelo para cambio de contraseña.
    Requiere contraseña actual para validar identidad.
    """
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=6, max_length=100, description="Nueva contraseña")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Valida que la nueva contraseña tenga formato correcto"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


# =====================================================
# MODELOS PARA RESPONSES (Lo que devuelve la API)
# =====================================================

class UserResponse(BaseModel):
    """
    Modelo público de usuario.
    NO incluye información sensible como password_hash.
    Este es el formato que ve el frontend.
    """
    id: str = Field(..., description="ID único del usuario")
    name: str = Field(..., description="Nombre completo")
    email: str = Field(..., description="Email del usuario")
    title: Optional[str] = Field(None, description="Título profesional")
    country: Optional[str] = Field(None, description="País")
    region: Optional[str] = Field(None, description="Región/Estado")
    avatar_url: Optional[str] = Field(None, description="URL del avatar")
    avatar_icon: Optional[str] = Field(None, description="ID del icono de avatar")
    avatar_color: Optional[str] = Field(None, description="ID del color de avatar")
    institution: Optional[str] = Field(None, description="Institución médica")
    specialty: Optional[str] = Field(None, description="Especialidad médica")
    language: Optional[str] = Field(None, description="Idioma preferido")
    is_active: bool = Field(..., description="Si el usuario está activo")
    email_verified: bool = Field(..., description="Si el email está verificado")
    created_at: datetime = Field(..., description="Fecha de registro")
    updated_at: datetime = Field(..., description="Última actualización")
    last_login: Optional[datetime] = Field(None, description="Último inicio de sesión")

    class Config:
        """Configuración para permitir conversión desde ORM"""
        from_attributes = True  # Permite crear desde objetos SQLAlchemy
        json_encoders = {
            # Convierte datetime a ISO string para JSON
            datetime: lambda v: v.isoformat() if v else None
        }


class LoginResponse(BaseModel):
    """
    Respuesta del login exitoso.
    Contiene el token JWT y datos básicos del usuario.
    """
    access_token: str = Field(..., description="Token JWT para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: UserResponse = Field(..., description="Datos del usuario logueado")


class MessageResponse(BaseModel):
    """
    Respuesta genérica con un mensaje.
    Útil para confirmaciones, errores, etc.
    """
    message: str = Field(..., description="Mensaje informativo")
    success: bool = Field(default=True, description="Si la operación fue exitosa")


# =====================================================
# MODELOS INTERNOS (Solo para uso en el backend)
# =====================================================

class UserInDB(BaseModel):
    """
    Modelo completo del usuario como está en la base de datos.
    Incluye campos sensibles que NO deben exponerse en la API.
    """
    id: str
    name: str
    email: str
    password_hash: str  # Campo sensible - solo para uso interno
    title: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_icon: Optional[str] = None
    avatar_color: Optional[str] = None
    institution: Optional[str] = None
    specialty: Optional[str] = None
    language: Optional[str] = None
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """
    Datos que se almacenan dentro del token JWT.
    Mantener mínimo para reducir tamaño del token.
    """
    user_id: str = Field(..., description="ID del usuario")
    email: str = Field(..., description="Email del usuario")
    exp: datetime = Field(..., description="Fecha de expiración")
    
    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }


# =====================================================
# MODELOS PARA OAUTH (Google, Facebook, etc.)
# =====================================================

class OAuthUserInfo(BaseModel):
    """
    Información del usuario obtenida de proveedores OAuth.
    Se normaliza independientemente del proveedor.
    """
    provider: str = Field(..., description="Proveedor OAuth (google, facebook, etc.)")
    provider_user_id: str = Field(..., description="ID del usuario en el proveedor")
    email: str = Field(..., description="Email del proveedor")
    name: str = Field(..., description="Nombre del proveedor")
    avatar_url: Optional[str] = Field(None, description="Avatar del proveedor")
    email_verified: bool = Field(default=False, description="Si el email está verificado en el proveedor")


class OAuthLoginRequest(BaseModel):
    """
    Request para login con OAuth.
    Contiene el token recibido del proveedor.
    """
    provider: str = Field(..., description="Nombre del proveedor")
    access_token: str = Field(..., description="Token de acceso del proveedor")


# =====================================================
# MODELOS PARA SESIONES
# =====================================================

class SessionInfo(BaseModel):
    """
    Información de una sesión activa.
    Para mostrar al usuario sus sesiones activas.
    """
    id: str = Field(..., description="ID de la sesión")
    created_at: datetime = Field(..., description="Cuándo se creó la sesión")
    expires_at: datetime = Field(..., description="Cuándo expira")
    user_agent: Optional[str] = Field(None, description="Navegador/dispositivo")
    ip_address: Optional[str] = Field(None, description="Dirección IP")
    is_current: bool = Field(..., description="Si es la sesión actual")
    
    class Config:
        from_attributes = True


# =====================================================
# VALIDADORES ADICIONALES
# =====================================================

def validate_email_format(email: str) -> bool:
    """
    Validador adicional de email más estricto.
    Se puede usar en validaciones personalizadas.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validador de fortaleza de contraseña.
    Retorna (es_válida, mensaje_error)
    """
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    if len(password) > 100:
        return False, "La contraseña no puede tener más de 100 caracteres"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "La contraseña debe contener al menos una letra"
    
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    
    # Opcional: validaciones adicionales
    if len(password) >= 8 and re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return True, "Contraseña fuerte"
    
    return True, "Contraseña válida"