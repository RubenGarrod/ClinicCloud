#!/bin/bash
# =============================================================================
# ClinicCloud - Script de Limpieza de Deployment Anterior
# =============================================================================
# Este script limpia el deployment antiguo de forma segura, haciendo backup
# de la base de datos antes de eliminar todo.
# =============================================================================

set -e  # Exit on error

echo "======================================================================"
echo "  ClinicCloud - Limpieza de Deployment Anterior"
echo "======================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# =============================================================================
# PASO 0: Confirmación
# =============================================================================
echo ""
print_warning "ADVERTENCIA: Este script va a:"
echo "  1. Hacer backup de la base de datos actual"
echo "  2. Detener y eliminar todos los contenedores Docker"
echo "  3. Eliminar todas las imágenes Docker de ClinicCloud"
echo "  4. Eliminar el directorio /root/ClinicCloud (después del backup)"
echo "  5. Limpiar volúmenes Docker (OPCIONAL - datos se perderán)"
echo ""
read -p "¿Estás seguro de continuar? (escribe 'SI' para confirmar): " confirm

if [ "$confirm" != "SI" ]; then
    print_error "Operación cancelada"
    exit 1
fi

# =============================================================================
# PASO 1: Crear Backup de Base de Datos
# =============================================================================
echo ""
echo "PASO 1: Creando backup de la base de datos..."

BACKUP_DIR="/root/cliniccloud-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Verificar si existe algún contenedor de DB corriendo
if docker ps -a | grep -q "db\|postgres"; then
    print_info "Encontrado contenedor de base de datos, creando backup..."

    # Intentar hacer backup con diferentes nombres de contenedor posibles
    DB_CONTAINER=$(docker ps -a --format "{{.Names}}" | grep -E "db|postgres|cliniccloud.*db" | head -1)

    if [ -n "$DB_CONTAINER" ]; then
        print_info "Contenedor de DB: $DB_CONTAINER"

        # Iniciar el contenedor si está parado
        docker start "$DB_CONTAINER" 2>/dev/null || true
        sleep 5

        # Hacer backup
        BACKUP_FILE="$BACKUP_DIR/database_backup.sql"
        docker exec "$DB_CONTAINER" pg_dumpall -U admin > "$BACKUP_FILE" 2>/dev/null || \
        docker exec "$DB_CONTAINER" pg_dumpall -U postgres > "$BACKUP_FILE" 2>/dev/null || \
        docker exec "$DB_CONTAINER" pg_dumpall -U cliniccloud > "$BACKUP_FILE" 2>/dev/null || \
        print_warning "No se pudo crear backup automático de la base de datos"

        if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
            print_success "Backup creado: $BACKUP_FILE"
            echo "Tamaño: $(du -h "$BACKUP_FILE" | cut -f1)"
        else
            print_warning "Backup de DB no creado o vacío"
        fi
    fi
else
    print_info "No se encontró contenedor de base de datos, saltando backup"
fi

# =============================================================================
# PASO 2: Backup de Archivos de Configuración
# =============================================================================
echo ""
echo "PASO 2: Haciendo backup de archivos de configuración..."

if [ -d "/root/ClinicCloud" ]; then
    print_info "Copiando archivos de configuración..."

    # Backup de .env si existe
    [ -f "/root/ClinicCloud/.env" ] && cp /root/ClinicCloud/.env "$BACKUP_DIR/.env.old"

    # Backup de docker-compose.yml si está modificado
    [ -f "/root/ClinicCloud/docker-compose.yml" ] && cp /root/ClinicCloud/docker-compose.yml "$BACKUP_DIR/docker-compose.yml.old"

    # Listar archivos respaldados
    ls -lh "$BACKUP_DIR"
    print_success "Backup de configuración completado"
else
    print_info "No se encontró directorio /root/ClinicCloud"
fi

print_success "Backups guardados en: $BACKUP_DIR"

# =============================================================================
# PASO 3: Detener y Eliminar Contenedores
# =============================================================================
echo ""
echo "PASO 3: Deteniendo y eliminando contenedores..."

# Intentar usar docker-compose si existe
if [ -f "/root/ClinicCloud/docker-compose.yml" ]; then
    print_info "Usando docker-compose para detener servicios..."
    cd /root/ClinicCloud
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down 2>/dev/null || true
fi

# Detener todos los contenedores
print_info "Deteniendo todos los contenedores..."
docker stop $(docker ps -aq) 2>/dev/null || print_info "No hay contenedores corriendo"

# Eliminar todos los contenedores
print_info "Eliminando todos los contenedores..."
docker rm -f $(docker ps -aq) 2>/dev/null || print_info "No hay contenedores para eliminar"

print_success "Contenedores eliminados"

# =============================================================================
# PASO 4: Eliminar Imágenes Docker de ClinicCloud
# =============================================================================
echo ""
echo "PASO 4: Eliminando imágenes Docker..."

print_info "Buscando imágenes de ClinicCloud..."
docker images | grep -i "cliniccloud\|desarrollocliniccloud"

print_info "Eliminando imágenes de ClinicCloud..."
docker images | grep -i "cliniccloud\|desarrollocliniccloud" | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || print_info "No se encontraron imágenes de ClinicCloud"

# Eliminar imágenes huérfanas
print_info "Eliminando imágenes sin tag (dangling)..."
docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || print_info "No hay imágenes dangling"

print_success "Imágenes de ClinicCloud eliminadas"

# =============================================================================
# PASO 5: Limpiar Volúmenes (OPCIONAL)
# =============================================================================
echo ""
echo "PASO 5: Limpieza de volúmenes Docker..."

print_warning "ADVERTENCIA: Eliminar volúmenes borrará TODOS los datos persistentes"
echo "Volúmenes actuales:"
docker volume ls

echo ""
read -p "¿Quieres eliminar TODOS los volúmenes? (escribe 'SI' para confirmar): " confirm_volumes

if [ "$confirm_volumes" == "SI" ]; then
    print_info "Eliminando volúmenes..."
    docker volume prune -f
    print_success "Volúmenes eliminados"
else
    print_info "Volúmenes mantenidos (datos preservados)"
fi

# =============================================================================
# PASO 6: Eliminar Directorio de la Aplicación
# =============================================================================
echo ""
echo "PASO 6: Eliminando directorio de la aplicación..."

if [ -d "/root/ClinicCloud" ]; then
    print_info "Eliminando /root/ClinicCloud..."
    rm -rf /root/ClinicCloud
    print_success "Directorio eliminado"
fi

if [ -d "/root/DesarrolloClinicCloud" ]; then
    print_info "Eliminando /root/DesarrolloClinicCloud..."
    rm -rf /root/DesarrolloClinicCloud
    print_success "Directorio eliminado"
fi

# =============================================================================
# PASO 7: Limpieza de Directorios de Datos Antiguos
# =============================================================================
echo ""
echo "PASO 7: Limpiando directorios de datos antiguos..."

# Mostrar directorios de datos
print_info "Directorios de datos encontrados:"
ls -lah /root/ | grep -i "clinic\|pgdata\|transformers" || print_info "No se encontraron directorios de datos"

echo ""
read -p "¿Quieres eliminar los directorios de datos antiguos? (escribe 'SI' para confirmar): " confirm_data

if [ "$confirm_data" == "SI" ]; then
    print_info "Eliminando directorios de datos..."
    rm -rf /root/cliniccloud-data 2>/dev/null || true
    rm -rf /root/pgdata 2>/dev/null || true
    rm -rf /root/transformers-cache 2>/dev/null || true
    print_success "Directorios de datos eliminados"
else
    print_info "Directorios de datos mantenidos"
fi

# =============================================================================
# PASO 8: Limpieza General de Docker
# =============================================================================
echo ""
echo "PASO 8: Limpieza general del sistema Docker..."

print_info "Ejecutando docker system prune..."
docker system prune -a -f --volumes 2>/dev/null || docker system prune -a -f

print_success "Sistema Docker limpiado"

# =============================================================================
# PASO 9: Verificación Final
# =============================================================================
echo ""
echo "PASO 9: Verificación final..."

echo ""
print_info "Contenedores restantes:"
docker ps -a

echo ""
print_info "Imágenes restantes:"
docker images

echo ""
print_info "Volúmenes restantes:"
docker volume ls

echo ""
print_info "Espacio en disco:"
df -h /

# =============================================================================
# LIMPIEZA COMPLETADA
# =============================================================================
echo ""
echo "======================================================================"
echo "  ✅ LIMPIEZA COMPLETADA EXITOSAMENTE"
echo "======================================================================"
echo ""
echo "Resumen:"
echo "  ✅ Backup de base de datos creado (si existía)"
echo "  ✅ Contenedores eliminados"
echo "  ✅ Imágenes de ClinicCloud eliminadas"
echo "  ✅ Directorios de aplicación eliminados"
echo "  ✅ Sistema Docker limpiado"
echo ""
echo "Backup guardado en:"
echo "  $BACKUP_DIR"
echo ""
echo "Archivos en el backup:"
ls -lh "$BACKUP_DIR"
echo ""
print_warning "IMPORTANTE: Guarda el backup en un lugar seguro antes de proceder"
echo ""
echo "Siguiente paso:"
echo "  Ejecutar el script de deployment: ./deploy.sh"
echo ""
echo "======================================================================"
