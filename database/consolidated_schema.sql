-- =====================================================
-- CLINIC CLOUD - SCHEMA COMPLETO DE BASE DE DATOS
-- =====================================================
-- Copyright (C) 2025 Rubén García Rodríguez
-- Licensed under GPL-3.0
--
-- Este archivo consolida todos los schemas y migraciones
-- en un único script para nuevas instalaciones.
--
-- Para instalaciones existentes, usar las migraciones
-- individuales en database/migrations/
-- =====================================================

-- =====================================================
-- EXTENSIONES REQUERIDAS
-- =====================================================

-- Extensión para búsqueda vectorial
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- SCHEMA: PUBLIC (Documentos Médicos)
-- =====================================================

-- Tabla de categorías médicas
CREATE TABLE IF NOT EXISTS categoria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE NOT NULL
);

COMMENT ON TABLE categoria IS 'Categorías médicas para clasificación de documentos';
COMMENT ON COLUMN categoria.nombre IS 'Nombre de la especialidad médica';

-- Tabla de documentos médicos
CREATE TABLE IF NOT EXISTS documento (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(500) NOT NULL,
    autor TEXT,  -- TEXT para soportar listas largas de autores
    fecha_publicacion DATE,
    contenido_vectorizado VECTOR(768),
    url_fuente TEXT NOT NULL,
    id_categoria INTEGER REFERENCES categoria(id),

    -- Nuevos campos para metadata enriquecida (Migración 006)
    mesh_terms TEXT[] DEFAULT '{}',
    journal VARCHAR(500),
    doi VARCHAR(100),
    publication_types TEXT[] DEFAULT '{}',
    language VARCHAR(10) DEFAULT 'eng',

    -- Constraints para evitar duplicados
    CONSTRAINT unique_url UNIQUE (url_fuente),
    CONSTRAINT check_titulo_not_empty CHECK (LENGTH(TRIM(titulo)) > 0)
);

COMMENT ON TABLE documento IS 'Documentos médicos y científicos indexados';
COMMENT ON COLUMN documento.autor IS 'Lista completa de autores del documento (sin límite de longitud)';
COMMENT ON COLUMN documento.contenido_vectorizado IS 'Embedding vectorial del documento para búsqueda semántica';
COMMENT ON COLUMN documento.url_fuente IS 'URL única del documento original';
COMMENT ON COLUMN documento.mesh_terms IS 'Medical Subject Headings (MeSH) asignados por NLM - categorización oficial';
COMMENT ON COLUMN documento.journal IS 'Nombre de la revista o journal donde fue publicado';
COMMENT ON COLUMN documento.doi IS 'Digital Object Identifier único del documento';
COMMENT ON COLUMN documento.publication_types IS 'Tipos de publicación (Clinical Trial, RCT, etc.)';
COMMENT ON COLUMN documento.language IS 'Código ISO 639-2 del idioma del documento';

-- Tabla de resúmenes generados automáticamente
CREATE TABLE IF NOT EXISTS resumen (
    id SERIAL PRIMARY KEY,
    id_documento INTEGER NOT NULL REFERENCES documento(id) ON DELETE CASCADE,
    texto_resumen TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraint: un documento solo puede tener un resumen
    CONSTRAINT unique_resumen_por_documento UNIQUE (id_documento)
);

COMMENT ON TABLE resumen IS 'Resúmenes generados automáticamente por BART para los documentos';
COMMENT ON COLUMN resumen.texto_resumen IS 'Texto del resumen generado (miniresumen de ~100-150 palabras)';

-- Índices para optimización de búsquedas
CREATE INDEX IF NOT EXISTS idx_documento_categoria ON documento(id_categoria);
CREATE INDEX IF NOT EXISTS idx_documento_fecha ON documento(fecha_publicacion DESC);
CREATE INDEX IF NOT EXISTS idx_documento_contenido_vectorizado
    ON documento USING ivfflat (contenido_vectorizado vector_cosine_ops);

-- Índices para nuevos campos (Migración 006)
CREATE INDEX IF NOT EXISTS idx_documento_mesh_terms ON documento USING GIN (mesh_terms);
CREATE INDEX IF NOT EXISTS idx_documento_publication_types ON documento USING GIN (publication_types);
CREATE INDEX IF NOT EXISTS idx_documento_journal ON documento (journal) WHERE journal IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_documento_doi ON documento (doi) WHERE doi IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_documento_language ON documento (language);

-- Índices para resumen (Migración 007)
CREATE INDEX IF NOT EXISTS idx_resumen_id_documento ON resumen(id_documento);

-- =====================================================
-- SCHEMA: AUTH (Autenticación y Usuarios)
-- =====================================================

-- Crear schema separado para autenticación
CREATE SCHEMA IF NOT EXISTS auth;

-- Tabla principal de usuarios
CREATE TABLE IF NOT EXISTS auth.users (
    -- Identificación
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    -- Información profesional
    title VARCHAR(50),                    -- Dr., Dra., Lic., Enf., etc.
    country VARCHAR(100),
    region VARCHAR(100),
    institution VARCHAR(255),             -- Hospital, Universidad, etc.
    specialty VARCHAR(255),               -- Especialidad médica

    -- Personalización
    avatar_url VARCHAR(500),
    avatar_icon VARCHAR(50) DEFAULT 'cat',
    avatar_color VARCHAR(50) DEFAULT 'blue',
    language VARCHAR(5) DEFAULT 'es',

    -- Estado y seguridad
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT check_language CHECK (language IN ('es', 'en'))
);

COMMENT ON TABLE auth.users IS 'Usuarios registrados del sistema';
COMMENT ON COLUMN auth.users.avatar_icon IS 'ID del icono de animal seleccionado para avatar';
COMMENT ON COLUMN auth.users.avatar_color IS 'ID del color de fondo del avatar';
COMMENT ON COLUMN auth.users.language IS 'Idioma preferido del usuario (es/en)';

-- Índices para usuarios
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON auth.users(is_active);

-- Tabla de preferencias de usuario
CREATE TABLE IF NOT EXISTS auth.user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Preferencias de búsqueda
    preferred_language VARCHAR(10) DEFAULT 'es' CHECK (preferred_language IN ('es', 'en', 'both')),
    results_per_page INTEGER DEFAULT 25 CHECK (results_per_page IN (10, 25, 50)),
    default_sort VARCHAR(20) DEFAULT 'relevance' CHECK (default_sort IN ('relevance', 'date', 'author')),

    -- Preferencias de visualización
    font_size VARCHAR(10) DEFAULT 'normal' CHECK (font_size IN ('small', 'normal', 'large')),
    theme VARCHAR(10) DEFAULT 'system' CHECK (theme IN ('light', 'dark', 'system')),

    -- Configuración de privacidad
    save_search_history BOOLEAN DEFAULT TRUE,
    history_retention VARCHAR(20) DEFAULT '6months' CHECK (history_retention IN ('1month', '3months', '6months', 'forever')),
    anonymous_stats BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE auth.user_preferences IS 'Preferencias personalizadas de cada usuario';

-- Índice para preferencias
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON auth.user_preferences(user_id);

-- Tabla de tokens de recuperación de contraseña
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

    -- Constraint
    CONSTRAINT valid_expiration CHECK (expires_at > created_at)
);

COMMENT ON TABLE auth.password_reset_tokens IS 'Tokens temporales para recuperación de contraseña';

-- Índices para tokens
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON auth.password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON auth.password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON auth.password_reset_tokens(expires_at);

-- =====================================================
-- SCHEMA: PUBLIC (Historial y Favoritos)
-- =====================================================

-- Tabla de historial de búsquedas
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,

    -- Relación con usuario (NULL para búsquedas anónimas)
    user_id INTEGER REFERENCES auth.users(id) ON DELETE SET NULL,

    -- Query de búsqueda
    query TEXT NOT NULL,

    -- Resultados obtenidos
    results_count INTEGER DEFAULT 0,

    -- Filtros aplicados en la búsqueda
    categories TEXT[],  -- Array de categorías
    date_from DATE,
    date_to DATE,

    -- Para tracking de sesiones anónimas
    session_id VARCHAR(100),

    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT check_query_not_empty CHECK (LENGTH(TRIM(query)) > 0)
);

COMMENT ON TABLE search_history IS 'Historial de búsquedas realizadas por usuarios';

-- Índices para historial
CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_search_history_session_id ON search_history(session_id);

-- Tabla de documentos favoritos
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,

    -- Relación con usuario
    user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Información del documento guardado
    document_id INTEGER NOT NULL REFERENCES documento(id) ON DELETE CASCADE,
    document_title VARCHAR(500) NOT NULL,
    document_url TEXT NOT NULL,
    document_summary TEXT,
    authors TEXT[],
    publication_date DATE,
    category VARCHAR(255),

    -- Notas personales y tags
    notes TEXT,
    tags TEXT[],

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraint: un usuario no puede guardar el mismo documento dos veces
    CONSTRAINT unique_user_document UNIQUE (user_id, document_id)
);

COMMENT ON TABLE favorites IS 'Documentos guardados por usuarios con notas y tags';
COMMENT ON COLUMN favorites.notes IS 'Notas personales del usuario sobre el documento';
COMMENT ON COLUMN favorites.tags IS 'Etiquetas personalizadas para organizar favoritos';

-- Índices para favoritos
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_document_id ON favorites(document_id);
CREATE INDEX IF NOT EXISTS idx_favorites_created_at ON favorites(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_favorites_tags ON favorites USING GIN(tags);

-- =====================================================
-- FUNCIONES Y TRIGGERS
-- =====================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para auth.users
DROP TRIGGER IF EXISTS update_users_updated_at ON auth.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para auth.user_preferences
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON auth.user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON auth.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para favorites
DROP TRIGGER IF EXISTS update_favorites_updated_at ON favorites;
CREATE TRIGGER update_favorites_updated_at
    BEFORE UPDATE ON favorites
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- FUNCIÓN DE LIMPIEZA DE TOKENS EXPIRADOS
-- =====================================================

CREATE OR REPLACE FUNCTION auth.cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM auth.password_reset_tokens
    WHERE expires_at < CURRENT_TIMESTAMP
    OR used_at IS NOT NULL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION auth.cleanup_expired_tokens IS 'Elimina tokens de reset de contraseña expirados o ya usados';

-- =====================================================
-- DATOS INICIALES (OPCIONAL)
-- =====================================================

-- Insertar categorías médicas básicas
INSERT INTO categoria (nombre) VALUES
    ('Cardiología'),
    ('Neurología'),
    ('Oncología'),
    ('Pediatría'),
    ('Dermatología'),
    ('Psiquiatría'),
    ('Obstetricia y Ginecología'),
    ('Traumatología'),
    ('Oftalmología'),
    ('Otorrinolaringología'),
    ('Endocrinología'),
    ('Urología'),
    ('Gastroenterología'),
    ('Genética Médica'),
    ('Geriatría'),
    ('Infectología'),
    ('Inmunología'),
    ('Nefrología'),
    ('Neumología'),
    ('Reumatología'),
    ('Medicina General'),
    ('Medicina Interna'),
    ('Radiología'),
    ('Anestesiología'),
    ('Hematología')
ON CONFLICT (nombre) DO NOTHING;

-- =====================================================
-- VERIFICACIÓN FINAL
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ClinicCloud Database Schema Initialized';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Extensions: vector';
    RAISE NOTICE 'Schemas: public, auth';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - categoria (medical categories)';
    RAISE NOTICE '  - documento (medical documents)';
    RAISE NOTICE '  - auth.users (users)';
    RAISE NOTICE '  - auth.user_preferences (user preferences)';
    RAISE NOTICE '  - auth.password_reset_tokens (password reset)';
    RAISE NOTICE '  - search_history (search history)';
    RAISE NOTICE '  - favorites (saved documents)';
    RAISE NOTICE '========================================';
END $$;
