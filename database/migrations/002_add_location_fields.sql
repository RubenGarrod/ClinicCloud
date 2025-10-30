-- =====================================================
-- Migración: Añadir campos de localización y título
-- Fecha: 2025-01-08
-- Descripción: Añade title, country y region a auth.users
-- =====================================================

-- Añadir columnas nuevas
ALTER TABLE auth.users
ADD COLUMN IF NOT EXISTS title VARCHAR(50),
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS region VARCHAR(100);

-- Comentarios para documentación
COMMENT ON COLUMN auth.users.title IS 'Título profesional (Dr., Dra., Lic., Enf., etc.)';
COMMENT ON COLUMN auth.users.country IS 'País del usuario';
COMMENT ON COLUMN auth.users.region IS 'Región/Estado del usuario';

-- Verificación
DO $$
BEGIN
    RAISE NOTICE '✓ Migración 002 completada exitosamente';
    RAISE NOTICE 'Columnas añadidas:';
    RAISE NOTICE '  - title (título profesional)';
    RAISE NOTICE '  - country (país)';
    RAISE NOTICE '  - region (región/estado)';
END $$;
