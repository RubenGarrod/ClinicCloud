# Sistema Híbrido de Queries para Scraper

## Descripción General

El sistema híbrido implementado en el scraper de ClinicCloud combina múltiples estrategias para maximizar la diversidad y cobertura de documentos médicos scraped desde PubMed.

## Componentes del Sistema

### 1. Base de Datos de Tracking

#### Tabla `query_tracking`
Registra todas las queries ejecutadas con métricas detalladas:
- `query_text`: Texto de la query ejecutada
- `categoria`: Categoría médica asociada
- `fecha_ejecutada`: Timestamp de ejecución
- `pmids_encontrados`: PMIDs totales retornados por PubMed
- `pmids_nuevos`: PMIDs no procesados previamente
- `pmids_insertados`: PMIDs insertados exitosamente en BD
- `duracion_segundos`: Tiempo de ejecución

#### Tabla `categoria_coverage`
Mantiene estadísticas de cobertura por categoría:
- `categoria`: Nombre de la categoría médica
- `total_documentos`: Número total de documentos en esta categoría
- `ultima_actualizacion`: Fecha del documento más reciente
- `prioridad`: Prioridad manual (1-10, default: 5)
- `dias_desde_ultimo_scrape`: Días desde último scraping

#### Vista `query_priority`
Calcula prioridades automáticamente usando:
```sql
priority_score = (prioridad * 10) + MIN(dias_desde_ultimo_scrape, 30) + (bonus si < 50 docs)
```

### 2. Pool de Queries (`query_templates.py`)

Contiene queries organizadas por categoría médica con tres niveles:

- **General**: Términos amplios (ej: "oncology", "cardiology")
- **Specific**: Consultas específicas (ej: "breast cancer treatment", "myocardial infarction")
- **MeSH Terms**: Términos controlados de NLM (ej: "Neoplasms[MeSH]")

Incluye 22 categorías médicas principales con ~400+ queries específicas.

### 3. Algoritmo de Rotación Inteligente

#### Paso 1: Obtener Prioridades
```python
priorities = db.get_category_priorities()
```
- Consulta la vista `query_priority`
- Ordena categorías por `priority_score` (mayor = más prioritario)
- Favorece categorías con:
  - Menos documentos actuales
  - Más días desde último scrape
  - Mayor prioridad manual

#### Paso 2: Filtrar Queries Recientes
```python
recently_scraped = db.get_recently_scraped_queries(days=3)
```
- Obtiene queries ejecutadas en últimos 3 días
- Evita repetición inmediata de búsquedas

#### Paso 3: Generar Pool Dinámico
Para cada categoría prioritaria:
1. Buscar queries disponibles en `MEDICAL_QUERIES`
2. Mezclar specific, mesh_terms y general
3. Filtrar queries ejecutadas recientemente
4. Randomizar orden
5. Seleccionar N queries según `priority_score / 10`

#### Paso 4: Agregar Trending Topics
- 10% del total de queries
- Temas de actualidad médica
- Ejemplos: "long COVID", "mRNA vaccines", "AI medicine"

#### Paso 5: Randomización Final
```python
random.shuffle(queries_with_category)
```
- Evita sesgo de orden de ejecución
- Asegura que categorías del final también se procesen

### 4. Tracking en Ejecución

Durante el scraping, cada query se registra:

```python
db.track_query_execution(
    query_text=query_text,
    categoria=categoria,
    pmids_encontrados=len(pmids),
    pmids_nuevos=len(pmids_nuevos),
    pmids_insertados=insertados,
    duracion=query_duration
)
```

Esta data alimenta el sistema de priorización en la siguiente ejecución.

## Ventajas del Sistema Híbrido

### 1. **Diversidad Máxima**
- Rotación entre categorías basada en cobertura real
- Queries específicas evitan repetición de contenido genérico
- Randomización elimina sesgos de orden

### 2. **Balance Automático**
- Categorías con pocos docs reciben mayor prioridad
- Se adapta automáticamente a cambios en PubMed
- No requiere configuración manual

### 3. **Eficiencia**
- No repite queries de últimos 3 días
- Prioriza categorías que generan contenido nuevo
- Evita saturación de categorías populares

### 4. **Trazabilidad**
- Cada query se registra con métricas
- Fácil análisis de rendimiento
- Debug simplificado

### 5. **Adaptabilidad**
- Fácil agregar nuevas categorías
- Prioridades manuales ajustables
- Trending topics actualizables

## Configuración

### Variables de Entorno

```bash
# Días hacia atrás para búsqueda en PubMed
SCRAPER_DAYS_BACK=30

# Documentos por ejecución
SCRAPER_MAX_DOCS=1000

# Tamaño de batch
SCRAPER_BATCH_SIZE=25
```

### Ajustar Prioridades Manualmente

```sql
-- Aumentar prioridad de oncología
UPDATE categoria_coverage
SET prioridad = 10
WHERE categoria = 'Oncology';

-- Disminuir prioridad de medicina general
UPDATE categoria_coverage
SET prioridad = 2
WHERE categoria = 'General Medicine';
```

### Agregar Nuevas Queries

Editar `scraper/query_templates.py`:

```python
MEDICAL_QUERIES = {
    "Nueva Categoria": {
        "general": ["término general"],
        "specific": [
            "query específica 1",
            "query específica 2"
        ],
        "mesh_terms": [
            "Término MeSH[MeSH]"
        ]
    }
}
```

### Actualizar Trending Topics

```python
TRENDING_TOPICS = [
    "nuevo tema relevante",
    "otro tema de actualidad"
]
```

## Monitoreo y Análisis

### Ver Categorías Prioritarias

```sql
SELECT * FROM query_priority LIMIT 10;
```

### Análisis de Queries por Categoría (últimos 7 días)

```sql
SELECT
    categoria,
    COUNT(*) as total_queries,
    SUM(pmids_encontrados) as total_pmids,
    SUM(pmids_nuevos) as pmids_nuevos,
    SUM(pmids_insertados) as pmids_insertados
FROM query_tracking
WHERE fecha_ejecutada > NOW() - INTERVAL '7 days'
GROUP BY categoria
ORDER BY pmids_insertados DESC;
```

### Queries Más Productivas

```sql
SELECT
    query_text,
    categoria,
    pmids_insertados,
    fecha_ejecutada
FROM query_tracking
WHERE fecha_ejecutada > NOW() - INTERVAL '30 days'
ORDER BY pmids_insertados DESC
LIMIT 20;
```

### Cobertura por Categoría

```sql
SELECT
    c.nombre as categoria,
    COUNT(d.id) as total_documentos,
    MAX(d.fecha_publicacion) as documento_mas_reciente
FROM categoria c
LEFT JOIN documento d ON d.id_categoria = c.id
GROUP BY c.nombre
ORDER BY total_documentos DESC;
```

## Troubleshooting

### Problema: Una categoría no se scrape nunca

**Solución**: Verificar que exista en `categoria_coverage`:

```sql
INSERT INTO categoria_coverage (categoria, prioridad)
VALUES ('Nombre Categoría', 10)
ON CONFLICT (categoria) DO UPDATE SET prioridad = 10;
```

### Problema: Muchas queries repetidas

**Solución**: Aumentar días de filtro en código:

```python
recently_scraped = db.get_recently_scraped_queries(days=7)  # Era 3
```

### Problema: Poca variedad en queries

**Solución**: Agregar más queries específicas en `query_templates.py`

### Problema: Error "MEDICAL_QUERIES not found"

**Solución**: Verificar que `query_templates.py` esté en el mismo directorio que `scraper_masivo.py`

## Roadmap Futuro

- [ ] Machine Learning para predicción de queries productivas
- [ ] Análisis semántico para evitar queries similares
- [ ] A/B testing de estrategias de priorización
- [ ] Dashboard web para monitoreo en tiempo real
- [ ] Auto-ajuste de prioridades basado en engagement de usuarios
- [ ] Integración con otras fuentes (bioRxiv, medRxiv, etc.)

## Referencias

- [PubMed E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25499/)
- [MeSH Browser](https://meshb.nlm.nih.gov/)
- [PubMed Search Tips](https://pubmed.ncbi.nlm.nih.gov/help/)

---

**Última actualización**: 2025-01-06
**Autor**: Sistema de scraping ClinicCloud
