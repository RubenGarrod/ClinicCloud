-- =====================================================
-- ⚠️  DEPRECATED - NO USAR ESTE ARCHIVO
-- =====================================================
-- Este archivo está obsoleto y se mantiene solo por compatibilidad.
-- Para nuevas instalaciones, usar: consolidated_schema.sql
-- =====================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de categorías - Ya tiene restricción UNIQUE en 'nombre'
CREATE TABLE categoria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE NOT NULL
);

-- Tabla de documentos - Agregamos restricciones para unicidad
CREATE TABLE documento (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(500) NOT NULL,
    autor VARCHAR(255),
    fecha_publicacion DATE,
    contenido_vectorizado VECTOR(768), 
    url_fuente TEXT NOT NULL,
    id_categoria INTEGER REFERENCES categoria(id),
    -- Consideramos que un documento es único si tiene la misma URL
    -- o si tiene el mismo título y autor (si está disponible)
    CONSTRAINT unique_url UNIQUE (url_fuente),
    CONSTRAINT unique_titulo_autor UNIQUE (titulo, COALESCE(autor, 'unknown'))
);

-- Tabla de resúmenes - Hacemos id_documento único para evitar múltiples resúmenes
CREATE TABLE resumen (
    id SERIAL PRIMARY KEY,
    id_documento INTEGER REFERENCES documento(id) ON DELETE CASCADE,
    texto_resumen TEXT NOT NULL,
    -- Aseguramos que cada documento solo puede tener un único resumen
    CONSTRAINT unique_documento_resumen UNIQUE (id_documento)
);

-- Creamos un índice para búsquedas vectoriales eficientes
CREATE INDEX ON documento USING ivfflat (contenido_vectorizado vector_cosine_ops) 
WITH (lists = 100);

-- Creamos también un índice en campos frecuentemente utilizados en búsquedas
CREATE INDEX idx_documento_titulo ON documento (titulo);
CREATE INDEX idx_documento_categoria ON documento (id_categoria);
CREATE INDEX idx_documento_fecha ON documento (fecha_publicacion);

-- Función para verificar y prevenir la inserción de documentos similares
CREATE OR REPLACE FUNCTION check_duplicate_document() RETURNS TRIGGER AS $$
BEGIN
    -- Si se está insertando un documento con título muy similar a uno existente
    -- y el mismo autor, podría ser un duplicado con pequeñas diferencias en el título
    IF EXISTS (
        SELECT 1 FROM documento 
        WHERE 
            autor = NEW.autor 
            AND (
                -- Títulos idénticos pero no detectados por restricción UNIQUE debido a espacios o puntuación
                REGEXP_REPLACE(LOWER(titulo), '[^a-z0-9]', '', 'g') = 
                REGEXP_REPLACE(LOWER(NEW.titulo), '[^a-z0-9]', '', 'g')
                -- O títulos muy similares (esto requiere extensión pg_trgm para ser efectivo)
                -- OR similarity(titulo, NEW.titulo) > 0.8
            )
            AND id != NEW.id
    ) THEN
        RAISE EXCEPTION 'Documento posiblemente duplicado detectado. Título similar ya existe con el mismo autor.';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Activar el trigger para nuevas inserciones y actualizaciones
CREATE TRIGGER prevent_duplicate_documents
BEFORE INSERT OR UPDATE ON documento
FOR EACH ROW EXECUTE FUNCTION check_duplicate_document();

-- =====================================================
-- SCHEMA DE AUTENTICACIÓN
-- =====================================================

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

-- Insertar usuario administrador por defecto (solo para desarrollo)
INSERT INTO auth.users (email, password_hash, name, is_active, email_verified)
VALUES (
    'admin@cliniccloud.com',
    -- Password: 'admin123' hasheado con bcrypt
    '$2b$12$LQv3c1yqBwEHxV1fGOLrxOehHyk.jZ8f8B3qjRy1QJbNQJX9LpZ3e',
    'Administrador Sistema',
    true,
    true
) ON CONFLICT (email) DO NOTHING;