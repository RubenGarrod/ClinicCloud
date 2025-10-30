FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de manera más robusta
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # Instalar explícitamente los paquetes
    pip install --no-cache-dir fastapi==0.101.0 uvicorn==0.23.2 pydantic==2.1.1 pydantic-settings==2.0.3 psycopg2-binary==2.9.7 python-dotenv==1.0.0 numpy==1.25.2

# Copiar el código del motor de búsqueda
COPY . .

# Establecer variables de entorno
ENV PYTHONPATH=/app
ENV MODULE_NAME="main"
ENV VARIABLE_NAME="app"
ENV PORT=8001

# Exponer el puerto
EXPOSE 8001

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]