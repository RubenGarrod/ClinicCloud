-- Migration 004: Tabla para tokens de recuperación de contraseña
-- Autor: Claude Code
-- Fecha: 2025-10-09
-- Descripción: Almacena tokens temporales para recuperación de contraseña

-- Crear tabla de tokens de reset de contraseña
CREATE TABLE IF NOT EXISTS auth.password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,

    -- Metadata del token
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,

    -- Información de seguridad
    ip_address VARCHAR(45) DEFAULT NULL,  -- Soporta IPv4 e IPv6
    user_agent TEXT DEFAULT NULL,

    -- Índices para búsquedas rápidas
    CONSTRAINT valid_expiration CHECK (expires_at > created_at)
);

-- Índice para búsquedas por token (muy frecuente)
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token
    ON auth.password_reset_tokens(token);

-- Índice para búsquedas por usuario
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id
    ON auth.password_reset_tokens(user_id);

-- Índice para limpiar tokens expirados
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at
    ON auth.password_reset_tokens(expires_at);

-- Comentarios para documentación
COMMENT ON TABLE auth.password_reset_tokens IS 'Tokens temporales para recuperación de contraseña';
COMMENT ON COLUMN auth.password_reset_tokens.token IS 'Token único generado con secrets.token_urlsafe()';
COMMENT ON COLUMN auth.password_reset_tokens.expires_at IS 'Fecha de expiración del token (típicamente 1 hora)';
COMMENT ON COLUMN auth.password_reset_tokens.used_at IS 'Marca de tiempo cuando se usó el token (NULL si no usado)';
COMMENT ON COLUMN auth.password_reset_tokens.ip_address IS 'IP desde donde se solicitó el reset';
COMMENT ON COLUMN auth.password_reset_tokens.user_agent IS 'User agent del navegador';

-- Función para limpiar tokens expirados (se puede ejecutar con cron)
CREATE OR REPLACE FUNCTION auth.cleanup_expired_password_reset_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM auth.password_reset_tokens
    WHERE expires_at < NOW() OR used_at IS NOT NULL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION auth.cleanup_expired_password_reset_tokens() IS
    'Elimina tokens expirados o ya usados. Retorna el número de tokens eliminados.';
