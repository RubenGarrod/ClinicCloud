-- Tabla para tracking de PMIDs procesados
-- Evita reprocesar documentos ya obtenidos de PubMed

CREATE TABLE IF NOT EXISTS pmid_procesado (
    id SERIAL PRIMARY KEY,
    pmid VARCHAR(20) NOT NULL UNIQUE,
    fecha_procesado TIMESTAMP NOT NULL DEFAULT NOW(),
    query_origen VARCHAR(500),
    insertado BOOLEAN DEFAULT FALSE,
    -- Índices para búsquedas rápidas
    CONSTRAINT pmid_unique UNIQUE(pmid)
);

-- Índice para búsquedas rápidas por PMID
CREATE INDEX IF NOT EXISTS idx_pmid_procesado_pmid ON pmid_procesado(pmid);

-- Índice para limpiezas periódicas (eliminar PMIDs antiguos)
CREATE INDEX IF NOT EXISTS idx_pmid_procesado_fecha ON pmid_procesado(fecha_procesado);

-- Comentarios
COMMENT ON TABLE pmid_procesado IS 'Registro de PMIDs ya procesados para evitar duplicados en scraping';
COMMENT ON COLUMN pmid_procesado.pmid IS 'PubMed ID único del artículo';
COMMENT ON COLUMN pmid_procesado.fecha_procesado IS 'Cuándo se procesó este PMID';
COMMENT ON COLUMN pmid_procesado.query_origen IS 'Query de búsqueda que encontró este PMID';
COMMENT ON COLUMN pmid_procesado.insertado IS 'Si el documento fue insertado o saltado por duplicado';
