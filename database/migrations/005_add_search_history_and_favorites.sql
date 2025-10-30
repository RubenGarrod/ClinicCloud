-- =====================================================
-- MIGRACIÓN: HISTORIAL DE BÚSQUEDAS Y FAVORITOS
-- =====================================================
-- Fecha: 2025-01-10
-- Descripción: Crea tablas para historial de búsquedas y documentos favoritos

-- =====================================================
-- TABLA: HISTORIAL DE BÚSQUEDAS
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
-- TABLA: DOCUMENTOS FAVORITOS
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
-- VERIFICACIÓN DE MIGRACIÓN
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✓ Migración completada exitosamente';
    RAISE NOTICE 'Tablas creadas:';
    RAISE NOTICE '  - search_history (historial de búsquedas)';
    RAISE NOTICE '  - favorite_documents (documentos favoritos)';
END $$;
