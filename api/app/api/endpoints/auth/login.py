"""
ENDPOINTS DE AUTENTICACIÓN - LOGIN Y REGISTRO
============================================

Este archivo contiene los endpoints para:
- Login de usuarios existentes
- Registro de nuevos usuarios
- Logout (invalidación de tokens)
- Verificación de tokens

Comentarios en español para facilitar mantenimiento.
"""

# import asyncpg
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Annotated

# Importar modelos y utilidades
from app.models.user import (
    UserLoginRequest,
    UserRegisterRequest,
    UserUpdateRequest,
    ChangePasswordRequest,
    LoginResponse,
    UserResponse,
    MessageResponse,
    UserInDB
)
from app.models.preferences import (
    UserPreferences,
    UserPreferencesUpdate
)
from app.models.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    create_token_hash,
    mask_email,
    get_client_ip,
    AUTH_ERRORS,
    JWT_EXPIRE_HOURS
)
from app.db.database import get_db_cursor, execute_query
from app.api.endpoints.auth.dependencies import get_current_user
from app.core.rate_limiter import get_rate_limiter
from app.core.session_manager import SessionManager
from app.core.validation import validate_email, validate_password_strength, validate_username

# Configurar router para este módulo
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Configurar esquema de seguridad Bearer Token
security = HTTPBearer(auto_error=False)


# =====================================================
# FUNCIONES AUXILIARES PARA BASE DE DATOS
# =====================================================

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Busca un usuario por email en la base de datos.

    Args:
        email: Email del usuario a buscar

    Returns:
        UserInDB | None: Usuario si existe, None si no
    """
    query = """
        SELECT id, name, email, password_hash, title, country, region, avatar_url, avatar_icon, avatar_color,
               institution, specialty, language,
               is_active, email_verified, created_at, updated_at, last_login
        FROM auth.users
        WHERE email = %s
    """

    row = execute_query(query, (email.lower(),), fetchone=True)

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


def create_user_in_db(user_data: UserRegisterRequest) -> UserInDB:
    """
    Crea un nuevo usuario en la base de datos.
    
    Args:
        user_data: Datos del usuario a crear
        
    Returns:
        UserInDB: Usuario creado
        
    Raises:
        Exception: Si hay error al crear el usuario
    """
    # Hashear la contraseña
    password_hash = hash_password(user_data.password)
    
    query = """
        INSERT INTO auth.users (name, email, password_hash, is_active, email_verified)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, name, email, password_hash, avatar_url, 
                  is_active, email_verified, created_at, updated_at
    """
    
    row = execute_query(
        query,
        (user_data.name.strip(),
         user_data.email.lower(),
         password_hash,
         True,  # is_active
         False),  # email_verified
        fetchone=True,
        commit=True
    )
    
    return UserInDB(
        id=str(row[0]),  # UUID se convierte a string
        name=row[1],
        email=row[2],
        password_hash=row[3],
        avatar_url=row[4],
        is_active=row[5],
        email_verified=row[6],
        created_at=row[7],
        updated_at=row[8]
    )




# =====================================================
# ENDPOINTS DE AUTENTICACIÓN
# =====================================================

@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    user_data: UserRegisterRequest,
    _rate_limit: Annotated[None, Depends(get_rate_limiter("auth_register"))] = None
):
    """
    Registra un nuevo usuario en el sistema.
    
    Este endpoint:
    1. Valida que el email no esté en uso
    2. Hashea la contraseña de forma segura
    3. Crea el usuario en la base de datos
    4. Genera un token JWT automáticamente
    5. Registra la sesión
    
    Returns:
        LoginResponse: Token de acceso y datos del usuario
        
    Raises:
        HTTPException 400: Si el email ya está registrado
        HTTPException 500: Si hay error interno
    """
    try:
        # Validar email
        email_valid, email_error = validate_email(user_data.email)
        if not email_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email inválido: {email_error}"
            )

        # Validar nombre de usuario
        name_valid, name_error = validate_username(user_data.name)
        if not name_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nombre inválido: {name_error}"
            )

        # Validar fortaleza de contraseña
        password_valid, password_errors = validate_password_strength(user_data.password)
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contraseña débil: {', '.join(password_errors)}"
            )

        # Verificar si el email ya existe
        existing_user = get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AUTH_ERRORS["EMAIL_ALREADY_EXISTS"]
            )
        
        # Crear el usuario
        new_user = create_user_in_db(user_data)
        
        # Generar token JWT
        token_data = create_access_token(new_user.id, new_user.email)

        # Crear sesión en la base de datos
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        await SessionManager.create_session(
            user_id=new_user.id,
            token=token_data["access_token"],
            request=request,
            expires_at=expires_at,
            token_type='access'
        )

        # Convertir a response público (sin password_hash)
        user_response = UserResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            title=getattr(new_user, 'title', None),
            country=getattr(new_user, 'country', None),
            region=getattr(new_user, 'region', None),
            avatar_url=new_user.avatar_url,
            avatar_icon=getattr(new_user, 'avatar_icon', None),
            avatar_color=getattr(new_user, 'avatar_color', None),
            institution=getattr(new_user, 'institution', None),
            specialty=getattr(new_user, 'specialty', None),
            language=getattr(new_user, 'language', 'es'),
            is_active=new_user.is_active,
            email_verified=new_user.email_verified,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
            last_login=getattr(new_user, 'last_login', None)
        )
        
        return LoginResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=user_response
        )
        
    except HTTPException:
        # Re-lanzar HTTPExceptions sin modificar
        raise
    except Exception as e:
        # Log del error interno (sin exponer detalles al usuario)
        print(f"Error en registro de usuario {mask_email(user_data.email)}: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: Request,
    credentials: UserLoginRequest,
    _rate_limit: Annotated[None, Depends(get_rate_limiter("auth_login"))] = None
):
    """
    Inicia sesión de un usuario existente.
    
    Este endpoint:
    1. Busca al usuario por email
    2. Verifica la contraseña
    3. Valida que la cuenta esté activa
    4. Genera un token JWT
    5. Registra la sesión
    
    Returns:
        LoginResponse: Token de acceso y datos del usuario
        
    Raises:
        HTTPException 401: Si las credenciales son incorrectas
        HTTPException 403: Si la cuenta está desactivada
        HTTPException 500: Si hay error interno
    """
    try:
        # Validar formato de email
        email_valid, email_error = validate_email(credentials.email)
        if not email_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email inválido: {email_error}"
            )

        # Buscar usuario por email
        user = get_user_by_email(credentials.email)

        # Verificar si el usuario existe
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["INVALID_CREDENTIALS"]
            )
        
        # Verificar contraseña
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["INVALID_CREDENTIALS"]
            )
        
        # Verificar que la cuenta esté activa
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AUTH_ERRORS["USER_INACTIVE"]
            )
        
        # Generar token JWT
        token_data = create_access_token(user.id, user.email)

        # Crear sesión en la base de datos
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        await SessionManager.create_session(
            user_id=user.id,
            token=token_data["access_token"],
            request=request,
            expires_at=expires_at,
            token_type='access'
        )

        # Actualizar last_login del usuario
        update_login_query = "UPDATE auth.users SET last_login = NOW() WHERE id = %s"
        execute_query(update_login_query, (int(user.id),), commit=True)

        # Convertir a response público
        user_response = UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            title=user.title,
            country=user.country,
            region=user.region,
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
        
        return LoginResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=user_response
        )
        
    except HTTPException:
        # Re-lanzar HTTPExceptions sin modificar
        raise
    except Exception as e:
        # Log del error interno
        print(f"Error en login de usuario {mask_email(credentials.email)}: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Cierra la sesión del usuario actual.
    
    Este endpoint:
    1. Verifica que el token sea válido
    2. Invalida la sesión en la base de datos
    3. El token seguirá siendo válido hasta su expiración natural
       (para invalidación completa se necesitaría una blacklist de tokens)
    
    Returns:
        MessageResponse: Confirmación del logout
        
    Raises:
        HTTPException 401: Si el token es inválido
    """
    try:
        # Verificar que se proporcione token
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["TOKEN_MISSING"]
            )
        
        # Verificar y decodificar token
        token_payload = verify_token(credentials.credentials)
        if not token_payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["TOKEN_INVALID"]
            )

        # Revocar la sesión en la base de datos
        revoked = await SessionManager.revoke_token(
            token=credentials.credentials,
            reason='logout'
        )

        if not revoked:
            # El token era válido pero no había sesión activa
            # Esto puede pasar si la sesión ya fue revocada o expiró
            pass

        return MessageResponse(
            message="Sesión cerrada correctamente",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en logout: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/verify", response_model=UserResponse)
async def verify_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Verifica el token actual y retorna los datos del usuario.
    
    Útil para:
    - Verificar si el usuario sigue logueado
    - Obtener datos actualizados del usuario
    - Validar tokens en el frontend
    
    Returns:
        UserResponse: Datos del usuario actual
        
    Raises:
        HTTPException 401: Si el token es inválido o expirado
    """
    try:
        # Verificar que se proporcione token
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["TOKEN_MISSING"]
            )
        
        # Verificar y decodificar token
        token_payload = verify_token(credentials.credentials)
        if not token_payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["TOKEN_INVALID"]
            )
        
        # Buscar usuario actual en la BD
        user = get_user_by_email(token_payload["email"])
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["USER_NOT_FOUND"]
            )
        
        # Retornar datos públicos del usuario
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            title=user.title,
            country=user.country,
            region=user.region,
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
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en verificación de usuario: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Actualiza el perfil del usuario actual.

    Permite actualizar:
    - Nombre
    - Avatar (icon y color)
    - Información profesional (institución, especialidad)
    - Preferencia de idioma

    NO permite cambiar el email (usar endpoint específico si se implementa).

    Returns:
        UserResponse: Datos actualizados del usuario

    Raises:
        HTTPException 401: Si el token es inválido
        HTTPException 500: Si hay error interno
    """
    try:
        # Construir query dinámicamente según campos proporcionados
        update_fields = []
        params = []

        if profile_data.name is not None:
            update_fields.append("name = %s")
            params.append(profile_data.name)

        if profile_data.title is not None:
            update_fields.append("title = %s")
            params.append(profile_data.title)

        if profile_data.country is not None:
            update_fields.append("country = %s")
            params.append(profile_data.country)

        if profile_data.region is not None:
            update_fields.append("region = %s")
            params.append(profile_data.region)

        if profile_data.avatar_icon is not None:
            update_fields.append("avatar_icon = %s")
            params.append(profile_data.avatar_icon)

        if profile_data.avatar_color is not None:
            update_fields.append("avatar_color = %s")
            params.append(profile_data.avatar_color)

        if profile_data.avatar_url is not None:
            update_fields.append("avatar_url = %s")
            params.append(profile_data.avatar_url)

        if profile_data.institution is not None:
            update_fields.append("institution = %s")
            params.append(profile_data.institution)

        if profile_data.specialty is not None:
            update_fields.append("specialty = %s")
            params.append(profile_data.specialty)

        if profile_data.language is not None:
            update_fields.append("language = %s")
            params.append(profile_data.language)

        # Si no hay campos para actualizar, retornar usuario actual
        if not update_fields:
            return current_user

        # Agregar updated_at automáticamente
        update_fields.append("updated_at = NOW()")

        # Agregar user_id al final de los parámetros (convertir a int)
        user_id = int(current_user.id) if isinstance(current_user.id, str) else current_user.id
        params.append(user_id)

        # Ejecutar update
        query = f"""
            UPDATE auth.users
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, name, email, title, country, region, avatar_url, avatar_icon, avatar_color,
                      institution, specialty, language, is_active, email_verified,
                      created_at, updated_at, last_login
        """

        row = execute_query(query, tuple(params), fetchone=True, commit=True)

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Retornar usuario actualizado
        return UserResponse(
            id=str(row[0]),
            name=row[1],
            email=row[2],
            title=row[3],
            country=row[4],
            region=row[5],
            avatar_url=row[6],
            avatar_icon=row[7],
            avatar_color=row[8],
            institution=row[9],
            specialty=row[10],
            language=row[11],
            is_active=row[12],
            email_verified=row[13],
            created_at=row[14],
            updated_at=row[15],
            last_login=row[16]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Cambia la contraseña del usuario actual.

    Requiere la contraseña actual para verificar identidad.
    La nueva contraseña debe cumplir con los requisitos de seguridad.

    Returns:
        MessageResponse: Confirmación del cambio

    Raises:
        HTTPException 401: Si la contraseña actual es incorrecta
        HTTPException 400: Si la nueva contraseña no es válida
        HTTPException 500: Si hay error interno
    """
    try:
        # Obtener usuario completo de la BD (con password_hash)
        user = get_user_by_email(current_user.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Verificar contraseña actual
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="La contraseña actual es incorrecta"
            )

        # Verificar que la nueva contraseña sea diferente
        if verify_password(password_data.new_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual"
            )

        # Hashear nueva contraseña
        new_password_hash = hash_password(password_data.new_password)

        # Actualizar contraseña en la BD
        query = """
            UPDATE auth.users
            SET password_hash = %s, updated_at = NOW()
            WHERE id = %s
        """

        # Convertir user_id a int
        user_id = int(current_user.id) if isinstance(current_user.id, str) else current_user.id

        # Ejecutar el UPDATE directamente con cursor
        from app.db.database import get_db_cursor
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (new_password_hash, user_id))

        # Por seguridad, revocar todas las sesiones del usuario
        # El usuario tendrá que hacer login nuevamente
        await SessionManager.revoke_all_user_sessions(
            user_id=current_user.id,
            reason='password_change'
        )

        return MessageResponse(
            message="Contraseña actualizada correctamente. Por seguridad, debes iniciar sesión nuevamente.",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al cambiar contraseña: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# ============================================
# ENDPOINTS DE PREFERENCIAS DE USUARIO
# ============================================

@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Obtener las preferencias del usuario actual.
    Si el usuario no tiene preferencias guardadas, retorna valores por defecto.
    """
    try:
        user_id = int(current_user.id) if isinstance(current_user.id, str) else current_user.id
        print(f"[GET /preferences] Obteniendo preferencias para user_id={user_id}")  # Debug

        # Intentar obtener las preferencias existentes
        query = """
            SELECT preferred_language, results_per_page, default_sort, font_size, theme,
                   save_search_history, history_retention, anonymous_stats
            FROM auth.user_preferences
            WHERE user_id = %s
        """

        row = execute_query(query, (user_id,), fetchone=True)
        print(f"[GET /preferences] Row desde DB: {row}")  # Debug

        if row:
            preferences = UserPreferences(
                preferredLanguage=row[0],
                resultsPerPage=row[1],
                defaultSort=row[2],
                fontSize=row[3],
                theme=row[4],
                saveSearchHistory=row[5],
                historyRetention=row[6],
                anonymousStats=row[7]
            )
            print(f"[GET /preferences] Retornando: {preferences.dict()}")  # Debug
            return preferences
        else:
            # Retornar preferencias por defecto
            print(f"[GET /preferences] No encontradas, retornando defaults")  # Debug
            return UserPreferences()

    except Exception as e:
        print(f"Error al obtener preferencias: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener preferencias"
        )


@router.patch("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Actualizar las preferencias del usuario.
    Si no existen preferencias, las crea automáticamente.
    """
    try:
        user_id = int(current_user.id) if isinstance(current_user.id, str) else current_user.id
        print(f"[PATCH /preferences] user_id={user_id}, datos={preferences.dict(exclude_none=True)}")  # Debug

        # Verificar si el usuario ya tiene preferencias
        check_query = "SELECT id FROM auth.user_preferences WHERE user_id = %s"
        existing = execute_query(check_query, (user_id,), fetchone=True)
        print(f"[PATCH /preferences] Preferencias existentes: {existing}")  # Debug

        if existing:
            # UPDATE: construir query dinámica solo con campos proporcionados
            update_fields = []
            params = []

            if preferences.preferredLanguage is not None:
                update_fields.append("preferred_language = %s")
                params.append(preferences.preferredLanguage)

            if preferences.resultsPerPage is not None:
                update_fields.append("results_per_page = %s")
                params.append(preferences.resultsPerPage)

            if preferences.defaultSort is not None:
                update_fields.append("default_sort = %s")
                params.append(preferences.defaultSort)

            if preferences.fontSize is not None:
                update_fields.append("font_size = %s")
                params.append(preferences.fontSize)

            if preferences.theme is not None:
                update_fields.append("theme = %s")
                params.append(preferences.theme)

            if preferences.saveSearchHistory is not None:
                update_fields.append("save_search_history = %s")
                params.append(preferences.saveSearchHistory)

            if preferences.historyRetention is not None:
                update_fields.append("history_retention = %s")
                params.append(preferences.historyRetention)

            if preferences.anonymousStats is not None:
                update_fields.append("anonymous_stats = %s")
                params.append(preferences.anonymousStats)

            if not update_fields:
                # Si no hay cambios, retornar preferencias actuales
                query = """
                    SELECT preferred_language, results_per_page, default_sort, font_size, theme,
                           save_search_history, history_retention, anonymous_stats
                    FROM auth.user_preferences
                    WHERE user_id = %s
                """
                row = execute_query(query, (user_id,), fetchone=True)
                return UserPreferences(
                    preferredLanguage=row[0],
                    resultsPerPage=row[1],
                    defaultSort=row[2],
                    fontSize=row[3],
                    theme=row[4],
                    saveSearchHistory=row[5],
                    historyRetention=row[6],
                    anonymousStats=row[7]
                )

            # Agregar updated_at
            update_fields.append("updated_at = NOW()")
            params.append(user_id)

            query = f"""
                UPDATE auth.user_preferences
                SET {', '.join(update_fields)}
                WHERE user_id = %s
                RETURNING preferred_language, results_per_page, default_sort, font_size, theme,
                          save_search_history, history_retention, anonymous_stats
            """

            row = execute_query(query, tuple(params), fetchone=True, commit=True)

        else:
            # INSERT: crear nuevas preferencias con valores proporcionados o por defecto
            defaults = UserPreferences()

            query = """
                INSERT INTO auth.user_preferences (
                    user_id, preferred_language, results_per_page, default_sort, font_size, theme,
                    save_search_history, history_retention, anonymous_stats
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING preferred_language, results_per_page, default_sort, font_size, theme,
                          save_search_history, history_retention, anonymous_stats
            """

            params = (
                user_id,
                preferences.preferredLanguage if preferences.preferredLanguage is not None else defaults.preferredLanguage,
                preferences.resultsPerPage if preferences.resultsPerPage is not None else defaults.resultsPerPage,
                preferences.defaultSort if preferences.defaultSort is not None else defaults.defaultSort,
                preferences.fontSize if preferences.fontSize is not None else defaults.fontSize,
                preferences.theme if preferences.theme is not None else defaults.theme,
                preferences.saveSearchHistory if preferences.saveSearchHistory is not None else defaults.saveSearchHistory,
                preferences.historyRetention if preferences.historyRetention is not None else defaults.historyRetention,
                preferences.anonymousStats if preferences.anonymousStats is not None else defaults.anonymousStats,
            )

            row = execute_query(query, params, fetchone=True, commit=True)

        return UserPreferences(
            preferredLanguage=row[0],
            resultsPerPage=row[1],
            defaultSort=row[2],
            fontSize=row[3],
            theme=row[4],
            saveSearchHistory=row[5],
            historyRetention=row[6],
            anonymousStats=row[7]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar preferencias: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar preferencias"
        )


@router.delete("/delete-account", response_model=MessageResponse)
async def delete_account(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Elimina permanentemente la cuenta del usuario actual y todos sus datos asociados.

    Este endpoint:
    1. Elimina todas las preferencias del usuario
    2. Elimina todo el historial de búsquedas
    3. Elimina todos los favoritos
    4. Elimina la cuenta del usuario

    Esta acción es IRREVERSIBLE.

    Returns:
        MessageResponse: Confirmación de la eliminación

    Raises:
        HTTPException 401: Si el token es inválido
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si hay error interno
    """
    try:
        user_id = int(current_user.id) if isinstance(current_user.id, str) else current_user.id

        # Usar una transacción para asegurar que todo se elimine correctamente
        from app.db.database import get_db_cursor

        with get_db_cursor(commit=True) as cursor:
            # 1. Eliminar preferencias (si existen)
            cursor.execute(
                "DELETE FROM auth.user_preferences WHERE user_id = %s",
                (user_id,)
            )

            # 2. Eliminar historial de búsquedas (si existe)
            cursor.execute(
                "DELETE FROM search_history WHERE user_id = %s",
                (user_id,)
            )

            # 3. Eliminar favoritos (si existen)
            cursor.execute(
                "DELETE FROM favorites WHERE user_id = %s",
                (user_id,)
            )

            # 4. Eliminar el usuario
            cursor.execute(
                "DELETE FROM auth.users WHERE id = %s RETURNING id",
                (user_id,)
            )

            deleted_user = cursor.fetchone()

            if not deleted_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

        print(f"Cuenta eliminada exitosamente: user_id={user_id}, email={mask_email(current_user.email)}")

        return MessageResponse(
            message="Cuenta eliminada permanentemente. Todos tus datos han sido borrados.",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al eliminar cuenta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la cuenta"
        )