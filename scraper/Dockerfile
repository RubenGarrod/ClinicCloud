FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias de sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Configuración por defecto del scraper continuo
ENV SCRAPER_MAX_DOCS=1000
ENV SCRAPER_BATCH_SIZE=25
ENV SCRAPER_START_HOUR=0
ENV SCRAPER_STOP_HOUR=23
ENV SCRAPER_LOOP_DELAY=1800

# Comando por defecto: scraper continuo optimizado
# Para usar el scraper básico: docker-compose run scraper python main.py
# Para scraper masivo: docker-compose run scraper python scraper_masivo.py --max-docs 10000
CMD ["python", "scraper_continuo.py"]