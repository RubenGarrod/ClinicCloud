-- =====================================================
-- Migración 007: Fix autor field + Add resumen table
-- =====================================================
-- Copyright (C) 2025 Rubén García Rodríguez
-- Licensed under GPL-3.0
--
-- Fix: Cambiar autor de VARCHAR(255) a TEXT para soportar listas largas
-- Add: Tabla resumen para almacenar los resúmenes generados por BART
-- =====================================================

BEGIN;

-- 1. Cambiar el tipo de datos de autor a TEXT
ALTER TABLE documento
    ALTER COLUMN autor TYPE TEXT;

COMMENT ON COLUMN documento.autor IS 'Lista completa de autores del documento (sin límite de longitud)';

-- 2. Crear tabla de resúmenes
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

-- Índices para resumen
CREATE INDEX IF NOT EXISTS idx_resumen_id_documento ON resumen(id_documento);

COMMIT;

-- Verificación
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migración 007 aplicada correctamente';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Cambios:';
    RAISE NOTICE '  - Campo autor cambiado a TEXT';
    RAISE NOTICE '  - Tabla resumen creada';
    RAISE NOTICE '========================================';
END $$;
