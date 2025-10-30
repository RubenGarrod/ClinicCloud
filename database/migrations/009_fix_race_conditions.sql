-- ==============================================================================
-- MIGRACIÓN 009: FIX RACE CONDITIONS
-- ==============================================================================
-- Fecha: 2025-10-23
-- Descripción: Añade UNIQUE constraints para prevenir race conditions
-- ==============================================================================

BEGIN;

-- Paso 1: Limpiar duplicados existentes en favoritos
DELETE FROM favorites a USING favorites b
WHERE a.id < b.id
AND a.user_id = b.user_id
AND a.document_id = b.document_id;

-- Paso 2: Añadir constraint UNIQUE a favoritos (solo si no existe)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'unique_user_document'
    ) THEN
        ALTER TABLE favorites
        ADD CONSTRAINT unique_user_document UNIQUE (user_id, document_id);
    END IF;
END $$;

-- Paso 3: Crear índice único en historial de búsqueda (prevenir duplicados exactos)
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_search_history
ON search_history (user_id, query, created_at);

COMMIT;

-- Verificación
SELECT 'Migración 009 aplicada correctamente' AS status;
