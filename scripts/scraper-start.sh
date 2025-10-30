#!/bin/bash
# =============================================================================
# SCRAPER START - Iniciar scraper continuo
# =============================================================================
# Este script inicia el scraper en modo continuo.
# Usar con cron para programar inicio automático.
#
# Ejemplo cron (iniciar a las 22:00 todos los días):
#   0 22 * * * /root/ClinicCloud/scripts/scraper-start.sh >> /var/log/cliniccloud-scraper.log 2>&1
# =============================================================================

set -e

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "================================================================================"
echo "🚀 INICIANDO SCRAPER CONTINUO - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"

# Verificar que docker-compose existe
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose no está instalado"
    exit 1
fi

# Verificar que el servicio db está corriendo
if ! docker-compose ps db | grep -q "Up"; then
    echo "⚠️  La base de datos no está corriendo. Iniciando servicios principales..."
    docker-compose up -d db api motor_busqueda frontend
    echo "⏳ Esperando 10s para que la base de datos esté lista..."
    sleep 10
fi

# Iniciar scraper con profile
echo "📦 Iniciando scraper en modo continuo..."
docker-compose --profile scraper up -d scraper

# Verificar que se inició correctamente
if docker-compose ps scraper | grep -q "Up"; then
    echo "✅ Scraper iniciado correctamente"
    echo "📊 Ver logs en tiempo real con: docker-compose logs -f scraper"
    echo "🛑 Detener con: docker-compose down scraper"
else
    echo "❌ Error: El scraper no se pudo iniciar"
    exit 1
fi

echo "================================================================================"
echo "✅ Scraper continuo en ejecución"
echo "================================================================================"
