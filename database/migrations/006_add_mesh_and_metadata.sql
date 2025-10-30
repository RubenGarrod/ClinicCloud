-- =====================================================
-- MIGRACIÓN 006: Añadir MeSH Terms y Metadata Adicional
-- =====================================================
-- Copyright (C) 2025 Rubén García Rodríguez
-- Licensed under GPL-3.0
--
-- Esta migración añade soporte para:
-- - MeSH Terms (Medical Subject Headings) de NLM
-- - Información de revista/journal
-- - DOI (Digital Object Identifier)
-- - Tipos de publicación
-- - Idioma del documento
--
-- Fecha: 2025-01-16
-- =====================================================

-- Añadir nuevas columnas a la tabla documento
ALTER TABLE documento
ADD COLUMN IF NOT EXISTS mesh_terms TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS journal VARCHAR(500),
ADD COLUMN IF NOT EXISTS doi VARCHAR(100),
ADD COLUMN IF NOT EXISTS publication_types TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'eng';

-- Comentarios explicativos
COMMENT ON COLUMN documento.mesh_terms IS 'Medical Subject Headings (MeSH) asignados por NLM - categorización oficial';
COMMENT ON COLUMN documento.journal IS 'Nombre de la revista o journal donde fue publicado';
COMMENT ON COLUMN documento.doi IS 'Digital Object Identifier único del documento';
COMMENT ON COLUMN documento.publication_types IS 'Tipos de publicación (Clinical Trial, RCT, etc.)';
COMMENT ON COLUMN documento.language IS 'Código ISO 639-2 del idioma del documento';

-- Índices para optimizar búsquedas
-- GIN (Generalized Inverted Index) es ideal para arrays de texto
CREATE INDEX IF NOT EXISTS idx_documento_mesh_terms
ON documento USING GIN (mesh_terms);

CREATE INDEX IF NOT EXISTS idx_documento_publication_types
ON documento USING GIN (publication_types);

-- Índice para búsquedas por journal
CREATE INDEX IF NOT EXISTS idx_documento_journal
ON documento (journal) WHERE journal IS NOT NULL;

-- Índice para búsquedas por DOI (único)
CREATE INDEX IF NOT EXISTS idx_documento_doi
ON documento (doi) WHERE doi IS NOT NULL;

-- Índice para filtrar por idioma
CREATE INDEX IF NOT EXISTS idx_documento_language
ON documento (language);

-- Verificar que la migración se aplicó correctamente
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'documento'
        AND column_name = 'mesh_terms'
    ) THEN
        RAISE NOTICE 'Migración 006 aplicada correctamente: Nuevas columnas y índices creados';
    ELSE
        RAISE EXCEPTION 'Error en migración 006: Columnas no creadas';
    END IF;
END $$;
