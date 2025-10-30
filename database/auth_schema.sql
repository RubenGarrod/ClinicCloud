-- =====================================================
-- SCHEMA DE AUTENTICACIÓN PARA CLINIC CLOUD
-- =====================================================
-- Este archivo crea las tablas necesarias para el sistema 
-- de autenticación de usuarios de forma modular y reutilizable

-- Crear schema separado para autenticación (mantiene organización)
CREATE SCHEMA IF NOT EXISTS auth;

-- =====================================================
-- TABLA DE USUARIOS
-- =====================================================
-- Almacena la información básica de los usuarios del sistema
CREATE TABLE IF NOT EXISTS auth.users (
    -- ID único del usuario (UUID para mejor seguridad que auto-increment)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Email único para login (índice para búsquedas rápidas)
    email VARCHAR(255) UNIQUE NOT NULL,
    
    -- Contraseña hasheada con bcrypt (NUNCA almacenar en texto plano)
    password_hash VARCHAR(255) NOT NULL,
    
    -- Nombre completo del usuario
    name VARCHAR(255) NOT NULL,
    
    -- Avatar del usuario (URL o path opcional)
    avatar_url VARCHAR(500),
    
    -- Estado del usuario (permite desactivar sin eliminar)
    is_active BOOLEAN DEFAULT true,
    
    -- Email verificado (para sistemas que requieren verificación)
    email_verified BOOLEAN DEFAULT false,
    
    -- Timestamps automáticos para auditoría
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLA DE SESIONES/TOKENS
-- =====================================================
-- Gestiona las sesiones activas y tokens JWT para mayor seguridad
CREATE TABLE IF NOT EXISTS auth.user_sessions (
    -- ID único de la sesión
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Referencia al usuario propietario de la sesión
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Hash del token JWT (para poder invalidar sesiones)
    token_hash VARCHAR(255) NOT NULL,
    
    -- Fecha de expiración del token
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Información adicional de la sesión
    user_agent TEXT, -- Navegador/dispositivo
    ip_address INET, -- IP desde donde se logueó
    
    -- Estado de la sesión
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamp de creación
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLA DE PROVEEDORES OAUTH (Google, Facebook, etc.)
-- =====================================================
-- Para login social - permite múltiples proveedores por usuario
CREATE TABLE IF NOT EXISTS auth.oauth_accounts (
    -- ID único de la cuenta OAuth
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Usuario asociado
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Proveedor (google, facebook, github, etc.)
    provider VARCHAR(50) NOT NULL,
    
    -- ID del usuario en el proveedor externo
    provider_user_id VARCHAR(255) NOT NULL,
    
    -- Email del proveedor (puede diferir del email principal)
    provider_email VARCHAR(255),
    
    -- Datos adicionales del proveedor (JSON)
    provider_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Un usuario no puede tener múltiples cuentas del mismo proveedor
    UNIQUE(provider, provider_user_id)
);

-- =====================================================
-- TABLA DE INTENTOS DE LOGIN (Seguridad)
-- =====================================================
-- Rastrea intentos fallidos para prevenir ataques de fuerza bruta
CREATE TABLE IF NOT EXISTS auth.login_attempts (
    -- ID único del intento
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Email que intentó hacer login (puede no existir en users)
    email VARCHAR(255) NOT NULL,
    
    -- IP desde donde se intentó
    ip_address INET NOT NULL,
    
    -- Si el intento fue exitoso
    success BOOLEAN NOT NULL,
    
    -- Razón del fallo (password_incorrect, user_not_found, account_locked, etc.)
    failure_reason VARCHAR(100),
    
    -- User agent del navegador
    user_agent TEXT,
    
    -- Timestamp del intento
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ÍNDICES PARA OPTIMIZAR CONSULTAS
-- =====================================================

-- Índice para búsquedas rápidas de email
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);

-- Índice para búsquedas de usuarios activos
CREATE INDEX IF NOT EXISTS idx_users_active ON auth.users(is_active);

-- Índice para búsquedas de sesiones por usuario
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON auth.user_sessions(user_id);

-- Índice para limpieza de sesiones expiradas
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON auth.user_sessions(expires_at);

-- Índice para OAuth lookups
CREATE INDEX IF NOT EXISTS idx_oauth_provider_user ON auth.oauth_accounts(provider, provider_user_id);

-- Índice para análisis de intentos de login por IP
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON auth.login_attempts(ip_address, attempted_at);

-- Índice para análisis de intentos por email
CREATE INDEX IF NOT EXISTS idx_login_attempts_email ON auth.login_attempts(email, attempted_at);

-- =====================================================
-- FUNCIÓN PARA ACTUALIZAR TIMESTAMP AUTOMÁTICAMENTE
-- =====================================================

-- Función que actualiza el campo updated_at automáticamente
CREATE OR REPLACE FUNCTION auth.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualiza el campo updated_at con la fecha/hora actual
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para usuarios - actualiza updated_at en cada UPDATE
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON auth.users 
    FOR EACH ROW 
    EXECUTE FUNCTION auth.update_updated_at_column();

-- Trigger para oauth_accounts
CREATE TRIGGER update_oauth_accounts_updated_at 
    BEFORE UPDATE ON auth.oauth_accounts 
    FOR EACH ROW 
    EXECUTE FUNCTION auth.update_updated_at_column();

-- =====================================================
-- DATOS INICIALES (OPCIONAL)
-- =====================================================

-- Insertar usuario administrador por defecto (solo para desarrollo)
-- IMPORTANTE: Cambiar credenciales en producción
INSERT INTO auth.users (email, password_hash, name, is_active, email_verified)
VALUES (
    'admin@cliniccloud.com',
    -- Password: 'admin123' hasheado con bcrypt
    '$2b$12$LQv3c1yqBwEHxV1fGOLrxOehHyk.jZ8f8B3qjRy1QJbNQJX9LpZ3e',
    'Administrador Sistema',
    true,
    true
) ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- COMENTARIOS EN TABLAS PARA DOCUMENTACIÓN
-- =====================================================

COMMENT ON SCHEMA auth IS 'Schema de autenticación y gestión de usuarios';
COMMENT ON TABLE auth.users IS 'Usuarios registrados en el sistema';
COMMENT ON TABLE auth.user_sessions IS 'Sesiones activas y tokens JWT';
COMMENT ON TABLE auth.oauth_accounts IS 'Cuentas de proveedores OAuth (Google, etc.)';
COMMENT ON TABLE auth.login_attempts IS 'Registro de intentos de login para seguridad';

COMMENT ON COLUMN auth.users.id IS 'Identificador único UUID del usuario';
COMMENT ON COLUMN auth.users.email IS 'Email único para autenticación';
COMMENT ON COLUMN auth.users.password_hash IS 'Contraseña hasheada con bcrypt';
COMMENT ON COLUMN auth.users.is_active IS 'Si el usuario está activo en el sistema';
COMMENT ON COLUMN auth.users.email_verified IS 'Si el email ha sido verificado';

-- =====================================================
-- PERMISOS Y SEGURIDAD
-- =====================================================

-- Revocar acceso público al schema auth
REVOKE ALL ON SCHEMA auth FROM public;

-- Solo el usuario de la aplicación debería tener acceso
-- (se configurará según el usuario de PostgreSQL que uses)
-- GRANT USAGE ON SCHEMA auth TO cliniccloud_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA auth TO cliniccloud_app_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA auth TO cliniccloud_app_user;