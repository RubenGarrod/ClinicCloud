#!/bin/bash
# =============================================================================
# ClinicCloud - Deploy Limpio desde Cero
# =============================================================================
# Este script automatiza el deploy completo limpiando instalaciones previas
# y construyendo todo desde cero con las correcciones aplicadas
# =============================================================================

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "============================================================================="
echo "🚀 CLINICCLOUD - DEPLOY LIMPIO DESDE CERO"
echo "============================================================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml no encontrado. Ejecutar desde el directorio raíz del proyecto."
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    log_error "Archivo .env no encontrado"
    log_info "Copiando desde .env.example..."
    cp .env.example .env
    log_warning "IMPORTANTE: Edita el archivo .env con tus valores reales antes de continuar"
    log_info "Luego ejecuta: sed -i 's/\r$//' .env  # Para convertir a LF"
    exit 1
fi

# Paso 1: Backup de base de datos (si existe)
log_info "Paso 1/8: Verificando si existe base de datos para backup..."
if docker ps -a | grep -q cliniccloud_db; then
    if docker ps | grep -q cliniccloud_db; then
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        log_info "Base de datos encontrada. Creando backup: $BACKUP_FILE"
        docker exec cliniccloud_db pg_dump -U admin cliniccloud > "$BACKUP_FILE" 2>/dev/null || {
            log_warning "No se pudo crear backup (puede que la BD esté vacía o corrupta)"
        }
        log_success "Backup creado: $BACKUP_FILE"
    else
        log_info "Base de datos existe pero no está corriendo, saltando backup"
    fi
else
    log_info "No hay base de datos existente, saltando backup"
fi
echo ""

# Paso 2: Detener y eliminar contenedores
log_info "Paso 2/8: Deteniendo contenedores existentes..."
docker-compose down -v 2>/dev/null || log_warning "No había contenedores corriendo"
log_success "Contenedores detenidos"
echo ""

# Paso 3: Limpiar sistema Docker
log_info "Paso 3/8: Limpiando sistema Docker (imágenes, volúmenes, cache)..."
log_warning "Esto puede tomar varios minutos..."
docker system prune -af --volumes
log_success "Sistema Docker limpio"
echo ""

# Paso 4: Verificar variables de entorno
log_info "Paso 4/8: Verificando variables de entorno..."
source .env
if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" == "CAMBIAR_ESTO_contraseña_muy_segura_12345" ]; then
    log_error "DB_PASSWORD no está configurada o tiene el valor por defecto"
    log_info "Edita .env y cambia DB_PASSWORD antes de continuar"
    exit 1
fi
log_success "Variables de entorno verificadas"
echo ""

# Paso 5: Crear directorios para volúmenes persistentes
log_info "Paso 5/8: Creando directorios para volúmenes persistentes..."
mkdir -p /root/cliniccloud-data/pgdata
mkdir -p /root/cliniccloud-data/transformers-cache
chmod 777 /root/cliniccloud-data/pgdata
chmod 777 /root/cliniccloud-data/transformers-cache
log_success "Directorios creados"
echo ""

# Paso 6: Construir imágenes sin cache
log_info "Paso 6/8: Construyendo imágenes Docker sin cache..."
log_warning "Esto puede tomar 10-15 minutos..."
docker-compose build --no-cache
log_success "Imágenes construidas"
echo ""

# Paso 7: Iniciar servicios
log_info "Paso 7/8: Iniciando servicios..."
docker-compose up -d
log_success "Servicios iniciados"
echo ""

# Paso 8: Verificar estado
log_info "Paso 8/8: Esperando a que los servicios estén listos..."
sleep 30

log_info "Estado de contenedores:"
docker-compose ps

echo ""
log_info "Verificando conexiones..."

# Verificar base de datos
DB_READY=false
for i in {1..10}; do
    if docker exec cliniccloud_db pg_isready -U admin -d cliniccloud > /dev/null 2>&1; then
        DB_READY=true
        break
    fi
    log_info "Esperando a que PostgreSQL esté listo... ($i/10)"
    sleep 3
done

if [ "$DB_READY" = true ]; then
    log_success "✅ PostgreSQL: LISTO"

    # Verificar tablas
    TABLES=$(docker exec cliniccloud_db psql -U admin -d cliniccloud -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
    log_info "   - Tablas creadas: $TABLES"

    # Verificar documentos
    DOCS=$(docker exec cliniccloud_db psql -U admin -d cliniccloud -t -c "SELECT COUNT(*) FROM documento;" 2>/dev/null | xargs)
    log_info "   - Documentos: $DOCS"
else
    log_error "❌ PostgreSQL: NO RESPONDE"
fi

# Verificar API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    log_success "✅ API: LISTO (http://localhost:8000)"
else
    log_warning "⚠️  API: No responde aún (puede necesitar más tiempo)"
fi

# Verificar Motor de Búsqueda
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    log_success "✅ Motor de Búsqueda: LISTO (http://localhost:8001)"
else
    log_warning "⚠️  Motor de Búsqueda: No responde aún (puede necesitar más tiempo)"
fi

# Verificar Frontend
if curl -s http://localhost/ > /dev/null 2>&1; then
    log_success "✅ Frontend: LISTO (http://localhost)"
else
    log_warning "⚠️  Frontend: No responde aún (puede necesitar más tiempo)"
fi

echo ""
echo "============================================================================="
log_success "🎉 DEPLOY COMPLETADO"
echo "============================================================================="
echo ""
log_info "URLs de acceso:"
echo "  - Frontend:        http://localhost"
echo "  - API:             http://localhost:8000"
echo "  - API Docs:        http://localhost:8000/docs"
echo "  - Motor Búsqueda:  http://localhost:8001"
echo "  - Adminer:         http://localhost:8080"
echo ""
log_info "Próximos pasos:"
echo "  1. Verificar logs:     docker-compose logs -f"
echo "  2. Ver solo errores:   docker-compose logs | grep -i error"
echo "  3. Estado servicios:   docker-compose ps"
echo "  4. Ejecutar scraper:   docker-compose run --rm scraper python main.py --max-docs 1000"
echo ""
log_warning "Si algún servicio no responde, espera 2-3 minutos más y verifica los logs"
echo ""
