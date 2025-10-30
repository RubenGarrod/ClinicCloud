# ClinicCloud Scraper

**[🇬🇧 English](README_EN.md)** | **🇪🇸 Español**

---

Sistema inteligente de scraping y procesamiento de documentos médicos con generación automática de embeddings y resúmenes.

## Características

- **Scraping Multi-Fuente**: PubMed, Cochrane, NICE Guidelines
- **Procesamiento ML Embebido**: S-PubMedBert (embeddings) + BART (resúmenes)
- **Batch Processing Optimizado**: Procesa miles de documentos eficientemente
- **Modo Continuo**: Ejecución controlada por horario con pausas configurables
- **Categorización Automática**: Clasifica documentos por especialidad médica
- **Almacenamiento Vectorial**: Inserta embeddings en PostgreSQL con pgvector

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    SCRAPER CONTINUO                         │
│  (scraper_continuo.py - Loop con control horario)          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   SCRAPER MASIVO                            │
│  (scraper_masivo.py - Batch processing optimizado)         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼               ▼
   ┌────────┐   ┌──────────┐   ┌──────────────┐
   │ Scrapy │   │  Models  │   │  PostgreSQL  │
   │ Spider │   │ Singleton│   │  + pgvector  │
   └────────┘   └──────────┘   └──────────────┘
        │             │                │
        │      ┌──────┴────────┐       │
        │      ▼               ▼       │
        │  S-PubMedBert    BART-CNN    │
        │  (embeddings)   (resúmenes)  │
        │                              │
        └──────────────┬───────────────┘
                       ▼
              Documentos procesados
           (título, resumen, embedding,
            categoría, fuente, metadata)
```

## Tres Modos de Ejecución

### 1. Scraper Continuo (RECOMENDADO para producción)

**Archivo**: `scraper_continuo.py`

Ejecuta el scraper en loop continuo con:
- Control de horario (START_HOUR - STOP_HOUR)
- Pausas configurables entre ejecuciones
- Carga única de modelos ML (eficiente en memoria)
- Auto-apagado fuera de horario

```bash
# Con docker-compose (ya configurado)
docker-compose up -d scraper

# Ver logs en tiempo real
docker-compose logs -f scraper

# Detener
docker-compose down scraper
```

**Variables de entorno**:
```bash
SCRAPER_MAX_DOCS=1000          # Documentos por ejecución
SCRAPER_BATCH_SIZE=25          # Docs por batch
SCRAPER_START_HOUR=0           # Hora inicio (0-23)
SCRAPER_STOP_HOUR=23           # Hora fin (0-23)
SCRAPER_LOOP_DELAY=1800        # Segundos entre ejecuciones (30min)
```

**Uso típico**: Servidor de producción que corre 24/7 con horario limitado (ej: solo de noche).

---

### 2. Scraper Masivo (Para procesamiento intensivo)

**Archivo**: `scraper_masivo.py`

Ejecuta una sola vez con máximo rendimiento:
- Procesa miles de documentos en una ejecución
- Batch processing optimizado (100-1000 docs/batch)
- Multiprocessing para paralelización
- Se apaga al terminar o al llegar al horario límite

```bash
# Modo manual (dentro del contenedor)
docker-compose run scraper python scraper_masivo.py \
  --max-docs 10000 \
  --batch-size 100 \
  --start-hour 22 \
  --stop-hour 8

# Con argumentos por defecto (1000 docs)
docker-compose run scraper python scraper_masivo.py
```

**Argumentos**:
- `--max-docs`: Máximo de documentos a procesar (default: 1000)
- `--batch-size`: Documentos por batch (default: 25)
- `--start-hour`: Hora de inicio permitida (default: 0)
- `--stop-hour`: Hora de parada (default: 23)

**Uso típico**: Scraping nocturno programado con cron, procesamiento inicial de gran volumen.

---

### 3. Scraper Básico (Compatibilidad legacy)

**Archivo**: `main.py`

Versión original con Scrapy tradicional:
- Ejecuta spider de PubMed con términos de búsqueda
- Programado cada 24 horas con `schedule`
- Menos optimizado pero más simple

```bash
# Ejecutar manualmente
docker-compose run scraper python main.py
```

**Uso típico**: Desarrollo, pruebas, scraping simple sin ML pesado.

---

## Configuración

### Variables de Entorno Requeridas

```bash
# Base de datos (REQUERIDO)
POSTGRES_USER=cliniccloud
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_DB=cliniccloud
DB_HOST=db
DB_PORT=5432

# Scraper continuo (OPCIONAL - usa defaults si no se especifica)
SCRAPER_MAX_DOCS=1000
SCRAPER_BATCH_SIZE=25
SCRAPER_START_HOUR=0
SCRAPER_STOP_HOUR=23
SCRAPER_LOOP_DELAY=1800

# Logging (OPCIONAL)
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Configuración del docker-compose.yml

El scraper ya está configurado en el `docker-compose.yml` principal:

```yaml
scraper:
  build:
    context: ./scraper
    dockerfile: Dockerfile
  environment:
    POSTGRES_USER: ${POSTGRES_USER:-cliniccloud}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB:-cliniccloud}
    DB_HOST: db
    DB_PORT: 5432
    SCRAPER_MAX_DOCS: ${SCRAPER_MAX_DOCS:-1000}
    SCRAPER_BATCH_SIZE: ${SCRAPER_BATCH_SIZE:-25}
    SCRAPER_START_HOUR: ${SCRAPER_START_HOUR:-0}
    SCRAPER_STOP_HOUR: ${SCRAPER_STOP_HOUR:-23}
    SCRAPER_LOOP_DELAY: ${SCRAPER_LOOP_DELAY:-1800}
  depends_on:
    db:
      condition: service_healthy
  volumes:
    - ./scraper/models:/app/models:rw  # Cachea modelos ML
```

---

## Modelos ML Utilizados

### 1. S-PubMedBert-MS-MARCO (Embeddings)

- **Modelo**: `pritamdeka/S-PubMedBert-MS-MARCO`
- **Dimensiones**: 768
- **Uso**: Genera embeddings semánticos para búsqueda vectorial
- **Descarga**: ~420 MB (primera ejecución)
- **Ubicación**: `/app/models/` (persistido en volumen)

### 2. BART-Large-CNN (Resúmenes)

- **Modelo**: `facebook/bart-large-cnn`
- **Uso**: Genera resúmenes automáticos de abstracts largos
- **Descarga**: ~1.6 GB (primera ejecución)
- **Ubicación**: Cache de HuggingFace (`~/.cache/`)

**Nota**: Los modelos se descargan automáticamente en la primera ejecución y se cachean para ejecuciones posteriores.

---

## Pipeline de Procesamiento

1. **Scraping** (Scrapy)
   - Consulta APIs de fuentes médicas (PubMed, etc.)
   - Extrae: título, abstract, autores, DOI, fecha, fuente

2. **Categorización** (ML)
   - Clasifica documento por especialidad médica
   - Usa keywords MeSH + términos médicos
   - Asigna a categorías predefinidas en BD

3. **Generación de Embeddings** (S-PubMedBert)
   - Genera vector de 768 dimensiones
   - Batch processing (32 docs/batch)
   - Optimizado para búsqueda semántica

4. **Resumen Automático** (BART)
   - Genera resumen de 50-150 palabras
   - Solo si abstract es muy largo (>300 chars)
   - Batch processing (16 docs/batch)

5. **Almacenamiento** (PostgreSQL)
   - Inserta en tabla `documents.documento`
   - Almacena embedding en columna `embedding` (vector 768)
   - Vincula con categoría médica

---

## Monitoring y Logs

### Ver logs en tiempo real

```bash
# Scraper continuo
docker-compose logs -f scraper

# Filtrar por nivel
docker-compose logs scraper | grep ERROR
docker-compose logs scraper | grep "✅"  # Mensajes de éxito
```

### Métricas clave en logs

```
🚀 INICIANDO EJECUCIÓN DEL SCRAPER MASIVO
   Max documentos: 1000
   Batch size: 25
   Horario: 0:00 - 23:00

🔄 Cargando modelo S-PubMedBert-MS-MARCO...
✅ Modelo S-PubMedBert cargado (768 dims)

📊 Procesados 850 documentos en 15.3 minutos
   - Embeddings generados: 850
   - Resúmenes generados: 320
   - Insertados en BD: 850
   - Errores: 0

✅ Scraper completado exitosamente
⏳ Esperando 1800s (30.0 min) antes de la siguiente ejecución...
```

---

## Troubleshooting

### Error: "No se pudo conectar a la base de datos"

**Causa**: PostgreSQL no está listo o credenciales incorrectas

**Solución**:
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps db

# Verificar logs de PostgreSQL
docker-compose logs db

# Verificar variables de entorno
docker-compose config | grep POSTGRES
```

### Error: "Out of memory" durante carga de modelos

**Causa**: Servidor con poca RAM (<4GB)

**Solución**:
```bash
# Reducir batch size
SCRAPER_BATCH_SIZE=10  # En lugar de 25

# Usar solo embeddings (sin resúmenes)
# Editar pipelines.py y comentar generación de resúmenes
```

### Error: "Model download failed"

**Causa**: Sin conexión a internet o proxy bloqueando HuggingFace

**Solución**:
```bash
# Pre-descargar modelos manualmente
docker-compose run scraper python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
print('Modelo descargado exitosamente')
"
```

### Scraper se detiene inesperadamente

**Causa**: Señal SIGTERM o error no capturado

**Solución**:
```bash
# Ver logs completos
docker-compose logs scraper --tail 100

# Reiniciar con logs detallados
docker-compose up scraper  # Sin -d para ver output directo
```

---

## Optimización para Producción

### Scraping Nocturno (Recomendado)

Configurar horario de ejecución solo en horas de bajo tráfico:

```bash
# En .env
SCRAPER_START_HOUR=22  # 10 PM
SCRAPER_STOP_HOUR=8    # 8 AM
SCRAPER_LOOP_DELAY=3600  # 1 hora entre ejecuciones
```

### Procesamiento Masivo Semanal

Para volúmenes muy grandes, ejecutar manualmente una vez por semana:

```bash
# Viernes a las 10 PM, procesar 50,000 documentos
docker-compose run scraper python scraper_masivo.py \
  --max-docs 50000 \
  --batch-size 100 \
  --start-hour 22 \
  --stop-hour 8
```

### Cacheo de Modelos

Los modelos ML ocupan ~2 GB de RAM y tardan ~30s en cargar. Para evitar recargas:

1. **Volumen persistente**: Ya configurado en docker-compose
2. **Modo continuo**: Carga modelos UNA sola vez al inicio
3. **Singleton pattern**: Reutiliza instancias en memoria

---

## Desarrollo Local

### Ejecutar scraper sin Docker

```bash
cd scraper

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export POSTGRES_USER=cliniccloud
export POSTGRES_PASSWORD=password
export POSTGRES_DB=cliniccloud
export DB_HOST=localhost
export DB_PORT=5432

# Ejecutar scraper continuo
python scraper_continuo.py

# O scraper masivo
python scraper_masivo.py --max-docs 100
```

### Ejecutar tests

```bash
# Test de categorizador
python inferencia/test_categorizador.py

# Test de conexión a BD
python -c "
import psycopg2
import os
conn = psycopg2.connect(
    dbname=os.getenv('POSTGRES_DB', 'cliniccloud'),
    user=os.getenv('POSTGRES_USER', 'cliniccloud'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('DB_HOST', 'localhost')
)
print('✅ Conexión exitosa')
conn.close()
"
```

---

## FAQ

**Q: ¿Cuánto espacio en disco necesito?**
A: Modelos ML (~2 GB) + datos scrapeados (depende del volumen). Mínimo 10 GB recomendado.

**Q: ¿Cuánta RAM necesita el scraper?**
A: Mínimo 4 GB. Recomendado 8 GB para batch processing grande.

**Q: ¿Puedo scrapear otras fuentes además de PubMed?**
A: Sí, pero requiere implementar nuevos spiders en `clinic_scraper/spiders/`. PubMed es la única fuente implementada actualmente.

**Q: ¿Los embeddings son compatibles con el motor de búsqueda?**
A: El scraper usa S-PubMedBert (768 dims). El motor de búsqueda usa MiniLM (384 dims). **NO son compatibles**. Debes elegir uno y usarlo consistentemente.

**Q: ¿Cómo cambio el modelo de embeddings?**
A: Edita `inferencia/model_singletons.py` y cambia el nombre del modelo. Asegúrate de actualizar `EMBEDDING_DIMENSION` en todas partes.

**Q: ¿El scraper respeta robots.txt?**
A: PubMed permite scraping vía API, no requiere robots.txt. Si agregas otras fuentes web, habilita `ROBOTSTXT_OBEY=True` en settings.

---

## Contribuir

Para contribuir al scraper:

1. Fork el repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nuevo-spider`
3. Implementa el spider en `clinic_scraper/spiders/`
4. Asegúrate de que el pipeline procese correctamente los datos
5. Crea un PR con descripción detallada

**Áreas de mejora prioritarias:**
- Spiders para Cochrane Library y NICE Guidelines
- Deduplicación de documentos (por DOI/título)
- Rate limiting más sofisticado
- Retry logic para fallos de red
- Telemetría y métricas (Prometheus)

---

## Licencia

Parte de ClinicCloud - GNU GPL v3 License

Copyright (C) 2025 Rubén García Rodríguez
