#!/bin/bash
# =============================================================================
# ClinicCloud - Script de Deployment Automatizado para Contabo
# =============================================================================
# Servidor: 31.220.73.136
# Usuario: root
# =============================================================================

set -e  # Exit on error

echo "======================================================================"
echo "  ClinicCloud - Deployment en Servidor Contabo"
echo "======================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# =============================================================================
# PASO 0: Detectar Deployment Anterior
# =============================================================================
echo "PASO 0: Verificando deployment anterior..."

OLD_DEPLOYMENT_DETECTED=false

# Verificar contenedores existentes
if docker ps -a | grep -q "cliniccloud\|desarrollocliniccloud"; then
    print_warning "Se detectaron contenedores de deployment anterior"
    OLD_DEPLOYMENT_DETECTED=true
fi

# Verificar imágenes existentes
if docker images | grep -q "cliniccloud\|desarrollocliniccloud"; then
    print_warning "Se detectaron imágenes Docker de deployment anterior"
    OLD_DEPLOYMENT_DETECTED=true
fi

# Verificar directorio existente
if [ -d "/root/ClinicCloud" ] || [ -d "/root/DesarrolloClinicCloud" ]; then
    print_warning "Se detectaron directorios de deployment anterior"
    OLD_DEPLOYMENT_DETECTED=true
fi

if [ "$OLD_DEPLOYMENT_DETECTED" = true ]; then
    echo ""
    print_warning "=========================================================="
    print_warning "  SE DETECTÓ UN DEPLOYMENT ANTERIOR"
    print_warning "=========================================================="
    echo ""
    echo "Es altamente recomendado limpiar el deployment anterior antes de continuar."
    echo ""
    echo "Opciones:"
    echo "  1. Ejecutar script de limpieza (RECOMENDADO)"
    echo "  2. Continuar sin limpiar (puede causar conflictos)"
    echo "  3. Cancelar deployment"
    echo ""
    read -p "Selecciona una opción (1/2/3): " cleanup_option

    case $cleanup_option in
        1)
            if [ -f "./cleanup-old-deployment.sh" ]; then
                print_info "Ejecutando script de limpieza..."
                chmod +x ./cleanup-old-deployment.sh
                ./cleanup-old-deployment.sh
                echo ""
                print_success "Limpieza completada. Continuando con deployment..."
                echo ""
            else
                print_error "Script de limpieza no encontrado: cleanup-old-deployment.sh"
                echo "Por favor descarga y ejecuta primero cleanup-old-deployment.sh"
                exit 1
            fi
            ;;
        2)
            print_warning "Continuando sin limpiar. Pueden ocurrir conflictos..."
            ;;
        3)
            print_info "Deployment cancelado"
            exit 0
            ;;
        *)
            print_error "Opción inválida"
            exit 1
            ;;
    esac
else
    print_success "No se detectó deployment anterior"
fi

# =============================================================================
# PASO 1: Verificar Pre-requisitos
# =============================================================================
echo ""
echo "PASO 1: Verificando pre-requisitos..."

# Verificar si estamos como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script debe ejecutarse como root"
    exit 1
fi
print_success "Usuario root verificado"

# Verificar conexión a internet
if ping -c 1 google.com &> /dev/null; then
    print_success "Conexión a internet OK"
else
    print_error "No hay conexión a internet"
    exit 1
fi

# =============================================================================
# PASO 2: Instalar Docker y Docker Compose
# =============================================================================
echo ""
echo "PASO 2: Instalando Docker y Docker Compose..."

if ! command -v docker &> /dev/null; then
    print_info "Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    print_success "Docker instalado"
else
    print_success "Docker ya está instalado ($(docker --version))"
fi

if ! command -v docker-compose &> /dev/null; then
    print_info "Instalando Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose instalado"
else
    print_success "Docker Compose ya está instalado ($(docker-compose --version))"
fi

# =============================================================================
# PASO 3: Configurar Firewall
# =============================================================================
echo ""
echo "PASO 3: Configurando firewall..."

if command -v ufw &> /dev/null; then
    print_info "Configurando UFW..."
    ufw allow 22/tcp   # SSH
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    ufw allow 8000/tcp # API
    ufw allow 8001/tcp # Search Engine
    echo "y" | ufw enable || true
    print_success "Firewall configurado"
else
    print_info "UFW no disponible, saltando configuración de firewall"
fi

# =============================================================================
# PASO 4: Crear Directorios de Datos
# =============================================================================
echo ""
echo "PASO 4: Creando directorios de datos..."

mkdir -p /root/cliniccloud-data/pgdata
mkdir -p /root/cliniccloud-data/transformers-cache
mkdir -p /root/cliniccloud-data/backups

chmod 777 /root/cliniccloud-data/pgdata
chmod 777 /root/cliniccloud-data/transformers-cache
chmod 755 /root/cliniccloud-data/backups

print_success "Directorios creados y configurados"

# =============================================================================
# PASO 5: Clonar Repositorio
# =============================================================================
echo ""
echo "PASO 5: Clonando repositorio desde GitHub..."

cd /root

if [ -d "ClinicCloud" ]; then
    print_info "Directorio ClinicCloud ya existe, actualizando..."
    cd ClinicCloud
    git pull origin main || git pull origin master
else
    print_info "Clonando repositorio..."
    git clone https://github.com/RubenGarrod/ClinicCloud.git
    cd ClinicCloud
fi

print_success "Repositorio clonado/actualizado"

# =============================================================================
# PASO 6: Configurar Variables de Entorno
# =============================================================================
echo ""
echo "PASO 6: Configurando variables de entorno..."

if [ ! -f .env ]; then
    print_info "Creando archivo .env..."
    cp .env.example .env

    # Generar credenciales seguras
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -hex 64)

    # Reemplazar en .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env

    print_success "Archivo .env creado con credenciales seguras"

    # Guardar credenciales en archivo seguro
    cat > /root/cliniccloud-credentials.txt <<EOF
====================================================================
ClinicCloud - Credenciales de Producción
====================================================================
Generadas el: $(date)

POSTGRES_PASSWORD=$POSTGRES_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
JWT_SECRET_KEY=$JWT_SECRET

IMPORTANTE: Guarda este archivo en un lugar seguro y elimínalo del servidor
====================================================================
EOF
    chmod 600 /root/cliniccloud-credentials.txt

    print_success "Credenciales guardadas en /root/cliniccloud-credentials.txt"
else
    print_success "Archivo .env ya existe"
fi

# =============================================================================
# PASO 7: Iniciar Base de Datos
# =============================================================================
echo ""
echo "PASO 7: Inicializando base de datos..."

print_info "Iniciando contenedor de PostgreSQL..."
docker-compose up -d db

print_info "Esperando a que PostgreSQL esté listo (30 segundos)..."
sleep 30

# Verificar que PostgreSQL está corriendo
if docker-compose ps | grep -q "db.*Up"; then
    print_success "PostgreSQL está corriendo"
else
    print_error "PostgreSQL no pudo iniciar"
    docker-compose logs db
    exit 1
fi

# =============================================================================
# PASO 8: Aplicar Schema y Migraciones
# =============================================================================
echo ""
echo "PASO 8: Aplicando schema y migraciones..."

print_info "Aplicando schema consolidado..."
docker-compose exec -T db psql -U admin -d cliniccloud < database/consolidated_schema.sql

print_info "Aplicando migraciones..."
for migration in database/migrations/*.sql; do
    migration_name=$(basename "$migration")
    echo "  Aplicando: $migration_name"
    docker-compose exec -T db psql -U admin -d cliniccloud < "$migration"
done

print_success "Schema y migraciones aplicadas"

# Verificar tablas
echo ""
print_info "Verificando tablas creadas..."
docker-compose exec db psql -U admin -d cliniccloud -c "\dt" | head -20

# =============================================================================
# PASO 9: Build y Start de Todos los Servicios
# =============================================================================
echo ""
echo "PASO 9: Building y iniciando todos los servicios..."

print_info "Building servicios (esto puede tomar varios minutos)..."
docker-compose build --parallel

print_info "Iniciando servicios en modo producción..."
docker-compose up -d

print_success "Todos los servicios iniciados"

# =============================================================================
# PASO 10: Verificar Servicios
# =============================================================================
echo ""
echo "PASO 10: Verificando servicios..."

sleep 10

print_info "Estado de contenedores:"
docker-compose ps

echo ""
print_info "Verificando health check de API..."
sleep 5

if curl -f http://localhost:8000/api/health &> /dev/null; then
    print_success "API está respondiendo correctamente"
else
    print_error "API no responde al health check"
    echo "Logs de API:"
    docker-compose logs --tail=50 api
fi

# =============================================================================
# PASO 11: Configurar Backups Automáticos
# =============================================================================
echo ""
echo "PASO 11: Configurando backups automáticos..."

# Añadir cron job para backup diario a las 3 AM
CRON_JOB="0 3 * * * /root/ClinicCloud/scripts/backup-db.sh"
(crontab -l 2>/dev/null | grep -v backup-db.sh; echo "$CRON_JOB") | crontab -

print_success "Backup automático configurado (diariamente a las 3 AM)"

# =============================================================================
# DEPLOYMENT COMPLETADO
# =============================================================================
echo ""
echo "======================================================================"
echo "  ✅ DEPLOYMENT COMPLETADO EXITOSAMENTE"
echo "======================================================================"
echo ""
echo "URLs de acceso:"
echo "  - Frontend: http://31.220.73.136"
echo "  - API: http://31.220.73.136:8000"
echo "  - API Docs: http://31.220.73.136:8000/docs"
echo "  - Search Engine: http://31.220.73.136:8001"
echo ""
echo "Credenciales guardadas en:"
echo "  /root/cliniccloud-credentials.txt"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: docker-compose logs -f"
echo "  - Ver estado: docker-compose ps"
echo "  - Restart: docker-compose restart"
echo "  - Stop: docker-compose down"
echo ""
echo "Siguiente paso:"
echo "  1. Abre http://31.220.73.136 en tu navegador"
echo "  2. Verifica que todo funciona correctamente"
echo "  3. Guarda las credenciales en un lugar seguro"
echo "  4. Elimina /root/cliniccloud-credentials.txt del servidor"
echo ""
echo "======================================================================"
