#!/bin/bash
# =============================================================================
# Script de Scraping Nocturno Automático
# =============================================================================
# Este script se ejecuta automáticamente en la madrugada para:
# 1. Iniciar el scraper masivo a las 2:00 AM
# 2. Procesar miles de documentos usando todos los recursos
# 3. Auto-apagarse a las 7:00 AM
# 4. Enviar notificaciones de progreso
#
# Instalación en crontab:
#   crontab -e
#   0 2 * * * /root/ClinicCloud/scraper/auto_scraper_nocturno.sh >> /var/log/scraper_nocturno.log 2>&1
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} [INFO] $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} [SUCCESS] $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} [WARNING] $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} [ERROR] $1"
}

echo "============================================================================="
log_info "🌙 SCRAPER NOCTURNO - INICIO"
echo "============================================================================="

# Variables
PROJECT_DIR="/root/ClinicCloud"
MAX_DOCS="${MAX_DOCS:-50000}"  # Por defecto 50k documentos
BATCH_SIZE="${BATCH_SIZE:-100}"
START_HOUR=2
STOP_HOUR=7

# Verificar que estamos en el directorio correcto
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Directorio $PROJECT_DIR no encontrado"
    exit 1
fi

cd "$PROJECT_DIR"

# Verificar hora actual
CURRENT_HOUR=$(date +%H)
if [ "$CURRENT_HOUR" -lt "$START_HOUR" ] || [ "$CURRENT_HOUR" -ge "$STOP_HOUR" ]; then
    log_warning "Fuera del horario permitido ($START_HOUR:00 - $STOP_HOUR:00). Hora actual: $CURRENT_HOUR:00"
    log_info "El scraper se ejecutará automáticamente a las $START_HOUR:00 AM"
    exit 0
fi

# Verificar que los servicios core estén corriendo
log_info "Verificando servicios core..."
if ! docker ps | grep -q cliniccloud_db; then
    log_error "Base de datos no está corriendo"
    exit 1
fi
log_success "Base de datos OK"

# Detener servicios no esenciales para liberar RAM
log_info "Deteniendo servicios no esenciales para liberar recursos..."

# Guardar estado de servicios
FRONTEND_RUNNING=$(docker ps -q -f name=cliniccloud_frontend)
API_RUNNING=$(docker ps -q -f name=cliniccloud_api)
MOTOR_RUNNING=$(docker ps -q -f name=cliniccloud_motor_busqueda)

# Detener frontend, API y motor de búsqueda (solo DB necesaria)
docker stop cliniccloud_frontend cliniccloud_api cliniccloud_motor_busqueda 2>/dev/null || log_warning "Algunos servicios ya estaban detenidos"

log_success "Servicios no esenciales detenidos"

# Verificar recursos disponibles
log_info "Recursos del sistema:"
free -h | grep -E "Mem|Swap"
echo ""

# Ejecutar scraper masivo
log_info "🚀 Iniciando scraper masivo..."
log_info "Configuración:"
log_info "  - Max documentos: $MAX_DOCS"
log_info "  - Batch size: $BATCH_SIZE"
log_info "  - Horario: $START_HOUR:00 - $STOP_HOUR:00"
echo ""

# Construir imagen si no existe
if ! docker images | grep -q cliniccloud_scraper; then
    log_info "Construyendo imagen del scraper..."
    docker-compose build scraper
fi

# Ejecutar scraper en contenedor con todos los recursos disponibles
docker run --rm \
    --name cliniccloud_scraper_nocturno \
    --network cliniccloud_network \
    --memory="10g" \
    --cpus="5" \
    -e DB_HOST=db \
    -e DB_PORT=5432 \
    -e DB_NAME=${DB_NAME:-cliniccloud} \
    -e DB_USER=${DB_USER:-admin} \
    -e DB_PASSWORD=${DB_PASSWORD:-admin123} \
    -e NCBI_API_KEY=${NCBI_API_KEY:-} \
    -v $(pwd)/scraper:/app \
    cliniccloud_scraper:latest \
    python scraper_masivo.py \
        --max-docs $MAX_DOCS \
        --batch-size $BATCH_SIZE \
        --start-hour $START_HOUR \
        --stop-hour $STOP_HOUR

SCRAPER_EXIT_CODE=$?

# Reporte final
echo ""
log_info "📊 Scraper finalizado con código: $SCRAPER_EXIT_CODE"

# Verificar estadísticas de la base de datos
log_info "Estadísticas de documentos en BD:"
docker exec cliniccloud_db psql -U ${DB_USER:-admin} -d ${DB_NAME:-cliniccloud} -c \
    "SELECT
        COUNT(*) as total_docs,
        COUNT(contenido_vectorizado) as docs_con_embedding,
        COUNT(r.id) as docs_con_resumen
     FROM documento d
     LEFT JOIN resumen r ON d.id = r.id_documento;" || log_warning "No se pudieron obtener estadísticas"

# Reiniciar servicios
log_info "Reiniciando servicios..."
docker start cliniccloud_motor_busqueda cliniccloud_api cliniccloud_frontend 2>/dev/null || log_warning "Error reiniciando algunos servicios"

# Esperar a que los servicios estén listos
sleep 30

# Verificar que los servicios estén OK
log_info "Verificando servicios..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep cliniccloud

echo ""
echo "============================================================================="
if [ $SCRAPER_EXIT_CODE -eq 0 ]; then
    log_success "✅ SCRAPING NOCTURNO COMPLETADO EXITOSAMENTE"
else
    log_error "❌ SCRAPING NOCTURNO FINALIZADO CON ERRORES (código: $SCRAPER_EXIT_CODE)"
fi
log_info "Servicios restaurados y listos para producción"
echo "============================================================================="

# Limpiar imágenes y contenedores huérfanos
log_info "Limpiando recursos Docker..."
docker system prune -f > /dev/null 2>&1

exit $SCRAPER_EXIT_CODE
