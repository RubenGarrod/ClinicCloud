# ClinicCloud Scraper

**[🇬🇧 English](README_EN.md)** | **[🇪🇸 Español](README.md)**

---

Intelligent scraping and medical document processing system with automatic embeddings and summary generation.

## Features

- **Multi-Source Scraping**: PubMed, Cochrane, NICE Guidelines
- **Embedded ML Processing**: S-PubMedBert (embeddings) + BART (summaries)
- **Optimized Batch Processing**: Efficiently processes thousands of documents
- **Continuous Mode**: Schedule-controlled execution with configurable pauses
- **Automatic Categorization**: Classifies documents by medical specialty
- **Vector Storage**: Inserts embeddings into PostgreSQL with pgvector

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTINUOUS SCRAPER                       │
│  (scraper_continuo.py - Loop with schedule control)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   MASSIVE SCRAPER                           │
│  (scraper_masivo.py - Optimized batch processing)          │
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
        │  (embeddings)   (summaries)  │
        │                              │
        └──────────────┬───────────────┘
                       ▼
              Processed documents
           (title, abstract, embedding,
            category, source, metadata)
```

## Three Execution Modes

### 1. Continuous Scraper (RECOMMENDED for production)

**File**: `scraper_continuo.py`

Runs the scraper in continuous loop with:
- Schedule control (START_HOUR - STOP_HOUR)
- Configurable pauses between executions
- One-time ML model loading (memory efficient)
- Auto-shutdown outside schedule

```bash
# With docker-compose (already configured)
docker-compose up -d scraper

# View logs in real-time
docker-compose logs -f scraper

# Stop
docker-compose down scraper
```

**Environment variables**:
```bash
SCRAPER_MAX_DOCS=1000          # Documents per execution
SCRAPER_BATCH_SIZE=25          # Docs per batch
SCRAPER_START_HOUR=0           # Start hour (0-23)
SCRAPER_STOP_HOUR=23           # Stop hour (0-23)
SCRAPER_LOOP_DELAY=1800        # Seconds between executions (30min)
```

**Typical use**: Production server running 24/7 with limited schedule (e.g., night-time only).

---

### 2. Massive Scraper (For intensive processing)

**File**: `scraper_masivo.py`

Executes once with maximum performance:
- Processes thousands of documents in one execution
- Optimized batch processing (100-1000 docs/batch)
- Multiprocessing for parallelization
- Shuts down upon completion or reaching schedule limit

```bash
# Manual mode (inside container)
docker-compose run scraper python scraper_masivo.py \
  --max-docs 10000 \
  --batch-size 100 \
  --start-hour 22 \
  --stop-hour 8

# With default arguments (1000 docs)
docker-compose run scraper python scraper_masivo.py
```

**Arguments**:
- `--max-docs`: Maximum documents to process (default: 1000)
- `--batch-size`: Documents per batch (default: 25)
- `--start-hour`: Allowed start hour (default: 0)
- `--stop-hour`: Stop hour (default: 23)

**Typical use**: Scheduled nightly scraping with cron, initial large volume processing.

---

### 3. Basic Scraper (Legacy compatibility)

**File**: `main.py`

Original version with traditional Scrapy:
- Executes PubMed spider with search terms
- Scheduled every 24 hours with `schedule`
- Less optimized but simpler

```bash
# Run manually
docker-compose run scraper python main.py
```

**Typical use**: Development, testing, simple scraping without heavy ML.

---

## Configuration

### Required Environment Variables

```bash
# Database (REQUIRED)
POSTGRES_USER=cliniccloud
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=cliniccloud
DB_HOST=db
DB_PORT=5432

# Continuous scraper (OPTIONAL - uses defaults if not specified)
SCRAPER_MAX_DOCS=1000
SCRAPER_BATCH_SIZE=25
SCRAPER_START_HOUR=0
SCRAPER_STOP_HOUR=23
SCRAPER_LOOP_DELAY=1800

# Logging (OPTIONAL)
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### docker-compose.yml Configuration

The scraper is already configured in the main `docker-compose.yml`:

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
    - ./scraper/models:/app/models:rw  # Caches ML models
```

---

## ML Models Used

### 1. S-PubMedBert-MS-MARCO (Embeddings)

- **Model**: `pritamdeka/S-PubMedBert-MS-MARCO`
- **Dimensions**: 768
- **Use**: Generates semantic embeddings for vector search
- **Download**: ~420 MB (first execution)
- **Location**: `/app/models/` (persisted in volume)

### 2. BART-Large-CNN (Summaries)

- **Model**: `facebook/bart-large-cnn`
- **Use**: Generates automatic summaries of long abstracts
- **Download**: ~1.6 GB (first execution)
- **Location**: HuggingFace cache (`~/.cache/`)

**Note**: Models are automatically downloaded on first execution and cached for subsequent runs.

---

## Processing Pipeline

1. **Scraping** (Scrapy)
   - Queries medical source APIs (PubMed, etc.)
   - Extracts: title, abstract, authors, DOI, date, source

2. **Categorization** (ML)
   - Classifies document by medical specialty
   - Uses MeSH keywords + medical terms
   - Assigns to predefined categories in DB

3. **Embedding Generation** (S-PubMedBert)
   - Generates 768-dimensional vector
   - Batch processing (32 docs/batch)
   - Optimized for semantic search

4. **Automatic Summary** (BART)
   - Generates 50-150 word summary
   - Only if abstract is very long (>300 chars)
   - Batch processing (16 docs/batch)

5. **Storage** (PostgreSQL)
   - Inserts into `documents.documento` table
   - Stores embedding in `embedding` column (vector 768)
   - Links with medical category

---

## Monitoring and Logs

### View logs in real-time

```bash
# Continuous scraper
docker-compose logs -f scraper

# Filter by level
docker-compose logs scraper | grep ERROR
docker-compose logs scraper | grep "✅"  # Success messages
```

### Key metrics in logs

```
🚀 STARTING MASSIVE SCRAPER EXECUTION
   Max documents: 1000
   Batch size: 25
   Schedule: 0:00 - 23:00

🔄 Loading S-PubMedBert-MS-MARCO model...
✅ S-PubMedBert model loaded (768 dims)

📊 Processed 850 documents in 15.3 minutes
   - Embeddings generated: 850
   - Summaries generated: 320
   - Inserted in DB: 850
   - Errors: 0

✅ Scraper completed successfully
⏳ Waiting 1800s (30.0 min) before next execution...
```

---

## Troubleshooting

### Error: "Could not connect to database"

**Cause**: PostgreSQL is not ready or incorrect credentials

**Solution**:
```bash
# Verify PostgreSQL is running
docker-compose ps db

# Check PostgreSQL logs
docker-compose logs db

# Verify environment variables
docker-compose config | grep POSTGRES
```

### Error: "Out of memory" during model loading

**Cause**: Server with low RAM (<4GB)

**Solution**:
```bash
# Reduce batch size
SCRAPER_BATCH_SIZE=10  # Instead of 25

# Use only embeddings (without summaries)
# Edit pipelines.py and comment out summary generation
```

### Error: "Model download failed"

**Cause**: No internet connection or proxy blocking HuggingFace

**Solution**:
```bash
# Pre-download models manually
docker-compose run scraper python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
print('Model downloaded successfully')
"
```

### Scraper stops unexpectedly

**Cause**: SIGTERM signal or uncaught error

**Solution**:
```bash
# View complete logs
docker-compose logs scraper --tail 100

# Restart with detailed logs
docker-compose up scraper  # Without -d to see direct output
```

---

## Production Optimization

### Nightly Scraping (Recommended)

Configure execution schedule only during low-traffic hours:

```bash
# In .env
SCRAPER_START_HOUR=22  # 10 PM
SCRAPER_STOP_HOUR=8    # 8 AM
SCRAPER_LOOP_DELAY=3600  # 1 hour between executions
```

### Weekly Massive Processing

For very large volumes, run manually once per week:

```bash
# Friday at 10 PM, process 50,000 documents
docker-compose run scraper python scraper_masivo.py \
  --max-docs 50000 \
  --batch-size 100 \
  --start-hour 22 \
  --stop-hour 8
```

### Model Caching

ML models occupy ~2 GB of RAM and take ~30s to load. To avoid reloads:

1. **Persistent volume**: Already configured in docker-compose
2. **Continuous mode**: Loads models ONCE at startup
3. **Singleton pattern**: Reuses in-memory instances

---

## Local Development

### Run scraper without Docker

```bash
cd scraper

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
export POSTGRES_USER=cliniccloud
export POSTGRES_PASSWORD=password
export POSTGRES_DB=cliniccloud
export DB_HOST=localhost
export DB_PORT=5432

# Run continuous scraper
python scraper_continuo.py

# Or massive scraper
python scraper_masivo.py --max-docs 100
```

### Run tests

```bash
# Test categorizer
python inferencia/test_categorizador.py

# Test DB connection
python -c "
import psycopg2
import os
conn = psycopg2.connect(
    dbname=os.getenv('POSTGRES_DB', 'cliniccloud'),
    user=os.getenv('POSTGRES_USER', 'cliniccloud'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('DB_HOST', 'localhost')
)
print('✅ Connection successful')
conn.close()
"
```

---

## FAQ

**Q: How much disk space do I need?**
A: ML models (~2 GB) + scraped data (depends on volume). Minimum 10 GB recommended.

**Q: How much RAM does the scraper need?**
A: Minimum 4 GB. Recommended 8 GB for large batch processing.

**Q: Can I scrape other sources besides PubMed?**
A: Yes, but requires implementing new spiders in `clinic_scraper/spiders/`. PubMed is the only currently implemented source.

**Q: Are the embeddings compatible with the search engine?**
A: The scraper uses S-PubMedBert (768 dims). The search engine uses MiniLM (384 dims). **They are NOT compatible**. You must choose one and use it consistently.

**Q: How do I change the embeddings model?**
A: Edit `inferencia/model_singletons.py` and change the model name. Make sure to update `EMBEDDING_DIMENSION` everywhere.

**Q: Does the scraper respect robots.txt?**
A: PubMed allows scraping via API, doesn't require robots.txt. If you add other web sources, enable `ROBOTSTXT_OBEY=True` in settings.

---

## Contributing

To contribute to the scraper:

1. Fork the repository
2. Create a branch for your feature: `git checkout -b feature/new-spider`
3. Implement the spider in `clinic_scraper/spiders/`
4. Ensure the pipeline correctly processes the data
5. Create a PR with detailed description

**Priority improvement areas:**
- Spiders for Cochrane Library and NICE Guidelines
- Document deduplication (by DOI/title)
- More sophisticated rate limiting
- Retry logic for network failures
- Telemetry and metrics (Prometheus)

---

## License

Part of ClinicCloud - GNU GPL v3 License

Copyright (C) 2025 Rubén García Rodríguez
