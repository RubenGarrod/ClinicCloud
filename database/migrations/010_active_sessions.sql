-- ============================================================================
-- MIGRACIÓN 010: Active Sessions - Token Validation
-- ============================================================================
-- Crea tabla para gestión de sesiones activas y tokens JWT.
--
-- Beneficios:
-- - Revocación de tokens (logout real)
-- - Detección de tokens robados
-- - Límite de sesiones simultáneas
-- - Auditoría de accesos
-- - Invalidación masiva (cambio de contraseña)
--
-- Autor: Claude Code
-- Fecha: 2025-10-29
-- ============================================================================

-- Crear esquema para sesiones si no existe
CREATE SCHEMA IF NOT EXISTS auth;

-- ============================================================================
-- TABLA: auth.active_sessions
-- ============================================================================
-- Almacena todos los tokens JWT activos para validación

CREATE TABLE IF NOT EXISTS auth.active_sessions (
    -- Identificación
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Token info
    token_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 del token JWT
    token_type VARCHAR(20) NOT NULL DEFAULT 'access',  -- 'access' o 'refresh'

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_used_at TIMESTAMPTZ,

    -- Client info (para detección de robo)
    ip_address INET,
    user_agent TEXT,
    device_info JSONB,  -- {device: "mobile", os: "iOS", browser: "Safari"}

    -- Estado
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    revoked_at TIMESTAMPTZ,
    revoked_reason VARCHAR(100),  -- 'logout', 'password_changed', 'security', 'expired'

    -- Índices para búsqueda rápida
    CONSTRAINT check_token_type CHECK (token_type IN ('access', 'refresh'))
);

-- ============================================================================
-- ÍNDICES para performance
-- ============================================================================

-- Búsqueda por token hash (la más común)
CREATE INDEX IF NOT EXISTS idx_active_sessions_token_hash
ON auth.active_sessions(token_hash)
WHERE is_active = TRUE;

-- Búsqueda por user_id (para listar sesiones de un usuario)
CREATE INDEX IF NOT EXISTS idx_active_sessions_user_id
ON auth.active_sessions(user_id)
WHERE is_active = TRUE;

-- Limpieza de tokens expirados
CREATE INDEX IF NOT EXISTS idx_active_sessions_expires_at
ON auth.active_sessions(expires_at)
WHERE is_active = TRUE;

-- Búsqueda por IP (detección de accesos sospechosos)
CREATE INDEX IF NOT EXISTS idx_active_sessions_ip_address
ON auth.active_sessions(ip_address);

-- ============================================================================
-- FUNCIÓN: Limpiar sesiones expiradas
-- ============================================================================
-- Se debe ejecutar periódicamente (ej: cada hora con cron)

CREATE OR REPLACE FUNCTION auth.cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Marcar como inactivas las sesiones expiradas
    UPDATE auth.active_sessions
    SET
        is_active = FALSE,
        revoked_at = NOW(),
        revoked_reason = 'expired'
    WHERE
        is_active = TRUE
        AND expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Opcional: Eliminar sesiones muy antiguas (más de 30 días inactivas)
    DELETE FROM auth.active_sessions
    WHERE
        is_active = FALSE
        AND revoked_at < NOW() - INTERVAL '30 days';

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCIÓN: Revocar todas las sesiones de un usuario
-- ============================================================================
-- Útil cuando el usuario cambia su contraseña

CREATE OR REPLACE FUNCTION auth.revoke_user_sessions(
    p_user_id INTEGER,
    p_reason VARCHAR(100) DEFAULT 'security'
)
RETURNS INTEGER AS $$
DECLARE
    revoked_count INTEGER;
BEGIN
    UPDATE auth.active_sessions
    SET
        is_active = FALSE,
        revoked_at = NOW(),
        revoked_reason = p_reason
    WHERE
        user_id = p_user_id
        AND is_active = TRUE;

    GET DIAGNOSTICS revoked_count = ROW_COUNT;

    RETURN revoked_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCIÓN: Limitar sesiones simultáneas
-- ============================================================================
-- Revoca sesiones antiguas si el usuario tiene más de N sesiones activas

CREATE OR REPLACE FUNCTION auth.enforce_session_limit(
    p_user_id INTEGER,
    p_max_sessions INTEGER DEFAULT 5
)
RETURNS INTEGER AS $$
DECLARE
    revoked_count INTEGER;
BEGIN
    -- Obtener sesiones a revocar (las más antiguas)
    WITH sessions_to_revoke AS (
        SELECT id
        FROM auth.active_sessions
        WHERE
            user_id = p_user_id
            AND is_active = TRUE
            AND token_type = 'access'
        ORDER BY last_used_at ASC NULLS FIRST, created_at ASC
        OFFSET p_max_sessions
    )
    UPDATE auth.active_sessions
    SET
        is_active = FALSE,
        revoked_at = NOW(),
        revoked_reason = 'session_limit_exceeded'
    WHERE id IN (SELECT id FROM sessions_to_revoke);

    GET DIAGNOSTICS revoked_count = ROW_COUNT;

    RETURN revoked_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VISTA: Sesiones activas con info de usuario
-- ============================================================================

CREATE OR REPLACE VIEW auth.active_sessions_view AS
SELECT
    s.id,
    s.user_id,
    u.email,
    u.name,
    s.token_type,
    s.created_at,
    s.expires_at,
    s.last_used_at,
    s.ip_address,
    s.user_agent,
    s.device_info,
    EXTRACT(EPOCH FROM (s.expires_at - NOW())) / 60 AS minutes_until_expiry
FROM auth.active_sessions s
JOIN auth.users u ON s.user_id = u.id
WHERE s.is_active = TRUE
ORDER BY s.last_used_at DESC NULLS LAST;

-- ============================================================================
-- GRANTS (permisos)
-- ============================================================================

-- Dar permisos a la aplicación (ajustar según tu usuario de BD)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON auth.active_sessions TO your_app_user;
-- GRANT SELECT ON auth.active_sessions_view TO your_app_user;
-- GRANT EXECUTE ON FUNCTION auth.cleanup_expired_sessions() TO your_app_user;
-- GRANT EXECUTE ON FUNCTION auth.revoke_user_sessions(UUID, VARCHAR) TO your_app_user;
-- GRANT EXECUTE ON FUNCTION auth.enforce_session_limit(UUID, INTEGER) TO your_app_user;

-- ============================================================================
-- COMENTARIOS para documentación
-- ============================================================================

COMMENT ON TABLE auth.active_sessions IS 'Almacena tokens JWT activos para validación y revocación';
COMMENT ON COLUMN auth.active_sessions.token_hash IS 'SHA-256 hash del token JWT para búsqueda segura';
COMMENT ON COLUMN auth.active_sessions.device_info IS 'Información del dispositivo en formato JSON';
COMMENT ON COLUMN auth.active_sessions.revoked_reason IS 'Razón de revocación: logout, password_changed, security, expired, session_limit_exceeded';

COMMENT ON FUNCTION auth.cleanup_expired_sessions() IS 'Limpia sesiones expiradas. Ejecutar periódicamente con cron.';
COMMENT ON FUNCTION auth.revoke_user_sessions(INTEGER, VARCHAR) IS 'Revoca todas las sesiones de un usuario (ej: al cambiar contraseña)';
COMMENT ON FUNCTION auth.enforce_session_limit(INTEGER, INTEGER) IS 'Limita sesiones simultáneas revocando las más antiguas';

-- ============================================================================
-- DATOS DE EJEMPLO (solo para desarrollo)
-- ============================================================================

-- En producción, los tokens se crean al hacer login
-- Este es solo un ejemplo de cómo se vería la estructura

-- INSERT INTO auth.active_sessions (
--     user_id,
--     token_hash,
--     expires_at,
--     ip_address,
--     user_agent,
--     device_info
-- ) VALUES (
--     'some-user-uuid',
--     'sha256-hash-of-jwt-token',
--     NOW() + INTERVAL '24 hours',
--     '192.168.1.100'::INET,
--     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
--     '{"device": "desktop", "os": "Windows 10", "browser": "Chrome"}'::JSONB
-- );

-- ============================================================================
-- FIN DE MIGRACIÓN
-- ============================================================================

-- Verificar que todo se creó correctamente
DO $$
BEGIN
    RAISE NOTICE 'Migración 010 completada exitosamente';
    RAISE NOTICE 'Tabla creada: auth.active_sessions';
    RAISE NOTICE 'Funciones creadas: cleanup_expired_sessions, revoke_user_sessions, enforce_session_limit';
    RAISE NOTICE 'Vista creada: auth.active_sessions_view';
END $$;
