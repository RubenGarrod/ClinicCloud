-- Habilita la extensión pgvector (si no está ya activa)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de categorías
CREATE TABLE categoria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE NOT NULL
);

-- Tabla de documentos
CREATE TABLE documento (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(500) NOT NULL,
    autor VARCHAR(255),
    fecha_publicacion DATE,
    contenido_vectorizado VECTOR(768), -- 768 dimensiones como el embedding de BART
    url_fuente TEXT NOT NULL,
    id_categoria INTEGER REFERENCES categoria(id)
);

-- Tabla de resúmenes
CREATE TABLE resumen (
    id SERIAL PRIMARY KEY,
    id_documento INTEGER REFERENCES documento(id) ON DELETE CASCADE,
    texto_resumen TEXT NOT NULL
);
