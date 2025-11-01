-- =====================================================
-- MIGRACIÓN: PREFERENCIAS DE USUARIO, HISTORIAL Y FAVORITOS
-- =====================================================
-- Fecha: 2025-01-07
-- Descripción: Extiende el sistema de usuarios con preferencias de UI,
--              historial de búsquedas, favoritos y prepara para RAG conversacional

-- =====================================================
-- PASO 1: EXTENDER TABLA DE USUARIOS CON PREFERENCIAS
-- =====================================================

-- Añadir columnas de preferencias a la tabla existente auth.users
ALTER TABLE auth.users
ADD COLUMN IF NOT EXISTS institution VARCHAR(255),
ADD COLUMN IF NOT EXISTS specialty VARCHAR(255),
ADD COLUMN IF NOT EXISTS avatar_icon VARCHAR(50) DEFAULT 'cat',
ADD COLUMN IF NOT EXISTS avatar_color VARCHAR(50) DEFAULT 'blue',
ADD COLUMN IF NOT EXISTS language VARCHAR(5) DEFAULT 'es',
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- Comentarios para documentación
COMMENT ON COLUMN auth.users.institution IS 'Institución médica del usuario (hospital, universidad, etc.)';
COMMENT ON COLUMN auth.users.specialty IS 'Especialidad médica del usuario';
COMMENT ON COLUMN auth.users.avatar_icon IS 'ID del icono de animal seleccionado para avatar';
COMMENT ON COLUMN auth.users.avatar_color IS 'ID del color de fondo del avatar';
COMMENT ON COLUMN auth.users.language IS 'Idioma preferido del usuario (es/en)';
COMMENT ON COLUMN auth.users.last_login IS 'Última vez que el usuario inició sesión';

-- =====================================================
-- PASO 2: HISTORIAL DE BÚSQUEDAS
-- =====================================================

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

    -- Metadata
    searched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para queries rápidas
CREATE INDEX IF NOT EXISTS idx_search_history_user_date
    ON search_history(user_id, searched_at DESC);

CREATE INDEX IF NOT EXISTS idx_search_history_date
    ON search_history(searched_at DESC);

CREATE INDEX IF NOT EXISTS idx_search_history_session
    ON search_history(session_id, searched_at DESC);

-- Índice full-text para buscar en queries anteriores
CREATE INDEX IF NOT EXISTS idx_search_history_query
    ON search_history USING gin(to_tsvector('spanish', query));

-- Comentarios
COMMENT ON TABLE search_history IS 'Historial de búsquedas de usuarios registrados y anónimos';
COMMENT ON COLUMN search_history.user_id IS 'Usuario que realizó la búsqueda (NULL si anónimo)';
COMMENT ON COLUMN search_history.session_id IS 'ID de sesión para trackear búsquedas anónimas';
COMMENT ON COLUMN search_history.categories IS 'Array de categorías filtradas';

-- =====================================================
-- PASO 3: DOCUMENTOS FAVORITOS
-- =====================================================

CREATE TABLE IF NOT EXISTS favorite_documents (
    id SERIAL PRIMARY KEY,

    -- Usuario propietario del favorito
    user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Información del documento
    document_id VARCHAR(255) NOT NULL,  -- ID del documento en tu sistema
    document_title TEXT NOT NULL,
    document_url TEXT,
    authors TEXT[],  -- Array de autores
    category VARCHAR(100),
    publication_date DATE,

    -- Notas personales del usuario
    notes TEXT,

    -- Tags personales del usuario
    tags TEXT[],

    -- Metadata
    favorited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Un usuario no puede marcar el mismo documento dos veces
    CONSTRAINT unique_user_document UNIQUE(user_id, document_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_favorites_user
    ON favorite_documents(user_id, favorited_at DESC);

CREATE INDEX IF NOT EXISTS idx_favorites_category
    ON favorite_documents(category);

CREATE INDEX IF NOT EXISTS idx_favorites_tags
    ON favorite_documents USING gin(tags);

-- Comentarios
COMMENT ON TABLE favorite_documents IS 'Documentos marcados como favoritos por los usuarios';
COMMENT ON COLUMN favorite_documents.document_id IS 'ID del documento en el sistema de búsqueda';
COMMENT ON COLUMN favorite_documents.notes IS 'Notas personales del usuario sobre el documento';
COMMENT ON COLUMN favorite_documents.tags IS 'Etiquetas personales para organizar favoritos';

-- =====================================================
-- PASO 4: TABLAS PARA CONVERSACIONES RAG (FUTURO)
-- =====================================================
-- Se crean vacías para tener la estructura lista

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,

    -- Usuario propietario
    user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Título de la conversación (auto-generado o editado por usuario)
    title VARCHAR(500) NOT NULL,

    -- Documento principal de la conversación (opcional)
    primary_document_id VARCHAR(255),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Estado
    is_archived BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,

    -- Conversación a la que pertenece
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Rol del mensaje
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),

    -- Contenido del mensaje
    content TEXT NOT NULL,

    -- Metadata del mensaje
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Fuentes RAG usadas (para trazabilidad)
    sources JSONB,

    -- Fuentes externas (web, PubMed, etc.)
    external_sources JSONB,

    -- Analytics
    tokens_used INTEGER,
    model_used VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS conversation_documents (
    id SERIAL PRIMARY KEY,

    -- Conversación
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Documento asociado
    document_id VARCHAR(255) NOT NULL,

    -- Metadata
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_primary BOOLEAN DEFAULT FALSE,

    -- Un documento no se puede añadir múltiples veces a la misma conversación
    CONSTRAINT unique_conversation_document UNIQUE(conversation_id, document_id)
);

-- Índices para conversaciones
CREATE INDEX IF NOT EXISTS idx_conversations_user
    ON conversations(user_id, last_message_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_document
    ON conversations(primary_document_id);

CREATE INDEX IF NOT EXISTS idx_messages_conversation
    ON conversation_messages(conversation_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_conv_docs_conversation
    ON conversation_documents(conversation_id);

-- Comentarios
COMMENT ON TABLE conversations IS 'Conversaciones RAG con documentos (para implementación futura)';
COMMENT ON TABLE conversation_messages IS 'Mensajes de conversaciones RAG';
COMMENT ON TABLE conversation_documents IS 'Documentos asociados a cada conversación';

-- =====================================================
-- PASO 5: ANALYTICS DE INTERACCIONES (OPCIONAL)
-- =====================================================

CREATE TABLE IF NOT EXISTS document_interactions (
    id SERIAL PRIMARY KEY,

    -- Usuario (puede ser NULL si no queremos guardar user_id)
    user_id INTEGER REFERENCES auth.users(id) ON DELETE SET NULL,

    -- Documento
    document_id VARCHAR(255) NOT NULL,

    -- Tipo de interacción
    interaction_type VARCHAR(50) NOT NULL CHECK (
        interaction_type IN ('view', 'favorite', 'unfavorite', 'start_conversation', 'share', 'download')
    ),

    -- Contexto (opcional)
    search_query TEXT,

    -- Metadata
    interacted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_interactions_document
    ON document_interactions(document_id, interacted_at DESC);

CREATE INDEX IF NOT EXISTS idx_interactions_user
    ON document_interactions(user_id, interacted_at DESC);

CREATE INDEX IF NOT EXISTS idx_interactions_type
    ON document_interactions(interaction_type, interacted_at DESC);

-- Comentarios
COMMENT ON TABLE document_interactions IS 'Registro de interacciones con documentos para analytics';

-- =====================================================
-- PASO 6: TRIGGER PARA UPDATED_AT EN CONVERSACIONES
-- =====================================================

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION auth.update_updated_at_column();

-- =====================================================
-- PASO 7: DATOS DE EJEMPLO (SOLO DESARROLLO)
-- =====================================================

-- Actualizar usuario admin con preferencias de ejemplo
UPDATE auth.users
SET
    avatar_icon = 'cat',
    avatar_color = 'blue',
    language = 'es',
    institution = 'Clinic Cloud Development',
    specialty = 'Administración'
WHERE email = 'admin@cliniccloud.com';

-- =====================================================
-- VERIFICACIÓN DE MIGRACIÓN
-- =====================================================

-- Verificar que las columnas se añadieron correctamente
DO $$
DECLARE
    column_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns
    WHERE table_schema = 'auth'
    AND table_name = 'users'
    AND column_name IN ('avatar_icon', 'avatar_color', 'language', 'institution', 'specialty');

    IF column_count = 5 THEN
        RAISE NOTICE '✓ Columnas de preferencias añadidas correctamente a auth.users';
    ELSE
        RAISE WARNING '⚠ Solo se añadieron % de 5 columnas esperadas', column_count;
    END IF;
END $$;

-- Listar todas las tablas creadas
DO $$
BEGIN
    RAISE NOTICE '✓ Migración completada exitosamente';
    RAISE NOTICE 'Tablas creadas/actualizadas:';
    RAISE NOTICE '  - auth.users (extendida con preferencias)';
    RAISE NOTICE '  - search_history (historial de búsquedas)';
    RAISE NOTICE '  - favorite_documents (documentos favoritos)';
    RAISE NOTICE '  - conversations (preparada para RAG futuro)';
    RAISE NOTICE '  - conversation_messages (preparada para RAG futuro)';
    RAISE NOTICE '  - conversation_documents (preparada para RAG futuro)';
    RAISE NOTICE '  - document_interactions (analytics opcional)';
END $$;
