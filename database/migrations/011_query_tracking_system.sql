-- =====================================================
-- Migration 011: Sistema de tracking de queries y cobertura
-- =====================================================
-- Este script crea las tablas necesarias para el sistema
-- híbrido de rotación inteligente de búsquedas del scraper

-- Tabla para tracking de queries ejecutadas
CREATE TABLE IF NOT EXISTS query_tracking (
    id SERIAL PRIMARY KEY,
    query_text VARCHAR(500) NOT NULL,
    categoria VARCHAR(100),
    fecha_ejecutada TIMESTAMP NOT NULL DEFAULT NOW(),
    pmids_encontrados INTEGER DEFAULT 0,
    pmids_nuevos INTEGER DEFAULT 0,
    pmids_insertados INTEGER DEFAULT 0,
    duracion_segundos INTEGER
);

CREATE INDEX IF NOT EXISTS idx_query_tracking_fecha ON query_tracking(fecha_ejecutada);
CREATE INDEX IF NOT EXISTS idx_query_tracking_categoria ON query_tracking(categoria);
CREATE INDEX IF NOT EXISTS idx_query_tracking_query_fecha ON query_tracking(query_text, fecha_ejecutada DESC);

-- Tabla para estadísticas de cobertura por categoría
CREATE TABLE IF NOT EXISTS categoria_coverage (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(100) NOT NULL UNIQUE,
    total_documentos INTEGER DEFAULT 0,
    ultima_actualizacion TIMESTAMP NOT NULL DEFAULT NOW(),
    prioridad INTEGER DEFAULT 5, -- 1=baja, 5=normal, 10=alta
    dias_desde_ultimo_scrape INTEGER DEFAULT 999
);

CREATE INDEX IF NOT EXISTS idx_categoria_coverage_prioridad ON categoria_coverage(prioridad);
CREATE INDEX IF NOT EXISTS idx_categoria_coverage_dias ON categoria_coverage(dias_desde_ultimo_scrape);

-- Función para actualizar cobertura de categorías
CREATE OR REPLACE FUNCTION update_categoria_coverage()
RETURNS void AS $$
BEGIN
    -- Insertar o actualizar cobertura por categoría
    INSERT INTO categoria_coverage (categoria, total_documentos, ultima_actualizacion)
    SELECT
        c.nombre as categoria,
        COUNT(d.id) as total_documentos,
        COALESCE(MAX(d.fecha_publicacion), NOW()) as ultima_actualizacion
    FROM categoria c
    LEFT JOIN documento d ON d.id_categoria = c.id
    GROUP BY c.nombre
    ON CONFLICT (categoria)
    DO UPDATE SET
        total_documentos = EXCLUDED.total_documentos,
        ultima_actualizacion = EXCLUDED.ultima_actualizacion,
        dias_desde_ultimo_scrape = CASE
            WHEN EXCLUDED.ultima_actualizacion IS NOT NULL
            THEN EXTRACT(DAY FROM (NOW() - EXCLUDED.ultima_actualizacion))::INTEGER
            ELSE 999
        END;
END;
$$ LANGUAGE plpgsql;

-- Vista para priorización de queries
CREATE OR REPLACE VIEW query_priority AS
SELECT
    cc.categoria,
    cc.total_documentos,
    cc.dias_desde_ultimo_scrape,
    cc.prioridad,
    -- Score de prioridad (más alto = más prioritario)
    (cc.prioridad * 10) +
    (LEAST(cc.dias_desde_ultimo_scrape, 30)) +
    (CASE WHEN cc.total_documentos < 50 THEN 20 ELSE 0 END) as priority_score,
    COALESCE(COUNT(qt.id), 0) as queries_ultimos_7_dias
FROM categoria_coverage cc
LEFT JOIN query_tracking qt ON
    qt.categoria = cc.categoria AND
    qt.fecha_ejecutada > NOW() - INTERVAL '7 days'
GROUP BY cc.categoria, cc.total_documentos, cc.dias_desde_ultimo_scrape, cc.prioridad
ORDER BY priority_score DESC;

-- Comentarios
COMMENT ON TABLE query_tracking IS 'Tracking de todas las queries ejecutadas por el scraper';
COMMENT ON TABLE categoria_coverage IS 'Estadísticas de cobertura por categoría médica';
COMMENT ON VIEW query_priority IS 'Vista para determinar prioridad de queries basada en cobertura';
