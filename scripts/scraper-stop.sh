#!/bin/bash
# =============================================================================
# SCRAPER STOP - Detener scraper continuo
# =============================================================================
# Este script detiene el scraper continuo de forma segura.
# Usar con cron para programar parada automática.
#
# Ejemplo cron (detener a las 8:00 todos los días):
#   0 8 * * * /root/ClinicCloud/scripts/scraper-stop.sh >> /var/log/cliniccloud-scraper.log 2>&1
# =============================================================================

set -e

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "================================================================================"
echo "🛑 DETENIENDO SCRAPER CONTINUO - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"

# Verificar que docker-compose existe
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose no está instalado"
    exit 1
fi

# Verificar si el scraper está corriendo
if docker-compose ps scraper | grep -q "Up"; then
    echo "📊 Obteniendo estadísticas finales..."
    docker-compose exec -T db psql -U admin -d cliniccloud -c "SELECT COUNT(*) as total_documentos FROM documento;" || true

    echo "🛑 Deteniendo scraper..."
    docker-compose down scraper

    echo "✅ Scraper detenido correctamente"
else
    echo "ℹ️  El scraper ya estaba detenido"
fi

echo "================================================================================"
echo "✅ Scraper continuo detenido"
echo "================================================================================"
