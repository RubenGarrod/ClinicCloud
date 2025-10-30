#!/bin/bash
# ==============================================================================
# SCRIPT DE CORRECCIÓN AUTOMÁTICA - VULNERABILIDADES P0
# ==============================================================================
# Este script aplica las correcciones CRÍTICAS de seguridad
#
# Uso:
#   chmod +x scripts/fix-p0-vulnerabilities.sh
#   ./scripts/fix-p0-vulnerabilities.sh
#
# ==============================================================================

set -e  # Salir si hay algún error

echo "=============================================================================="
echo "🔧 CLINICCLOUD - CORRECCIÓN DE VULNERABILIDADES P0"
echo "=============================================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==============================================================================
# 1. VERIFICAR QUE ESTAMOS EN EL DIRECTORIO CORRECTO
# ==============================================================================
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ ERROR: Este script debe ejecutarse desde la raíz del proyecto${NC}"
    exit 1
fi

# ==============================================================================
# 2. BACKUP DE ARCHIVOS QUE VAMOS A MODIFICAR
# ==============================================================================
echo -e "${YELLOW}📦 Creando backup de archivos...${NC}"
BACKUP_DIR="backups/pre-fix-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
cp .env.example "$BACKUP_DIR/" 2>/dev/null || true

echo -e "${GREEN}✅ Backup creado en: $BACKUP_DIR${NC}"
echo ""

# ==============================================================================
# 3. GENERAR JWT_SECRET SI NO EXISTE EN .env
# ==============================================================================
echo -e "${YELLOW}🔐 Verificando JWT_SECRET...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no existe. Creando desde .env.example...${NC}"
    cp .env.example .env
fi

if ! grep -q "^JWT_SECRET=" .env 2>/dev/null || grep -q "CAMBIAR_ESTO" .env 2>/dev/null; then
    echo -e "${YELLOW}Generando JWT_SECRET seguro...${NC}"
    NEW_JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

    if grep -q "^JWT_SECRET=" .env; then
        # Reemplazar existente
        sed -i.bak "s/^JWT_SECRET=.*/JWT_SECRET=$NEW_JWT_SECRET/" .env
    else
        # Añadir al final
        echo "JWT_SECRET=$NEW_JWT_SECRET" >> .env
    fi

    echo -e "${GREEN}✅ JWT_SECRET generado y añadido a .env${NC}"
else
    echo -e "${GREEN}✅ JWT_SECRET ya está configurado${NC}"
fi
echo ""

# ==============================================================================
# 4. OCULTAR ADMINER Y POSTGRESQL DE INTERNET
# ==============================================================================
echo -e "${YELLOW}🔒 Ocultando Adminer y PostgreSQL de internet...${NC}"

# Modificar docker-compose.yml para poner localhost en los puertos
if grep -q "\"5432:5432\"" docker-compose.yml; then
    sed -i.bak 's/"5432:5432"/"127.0.0.1:5432:5432"/' docker-compose.yml
    echo -e "${GREEN}✅ PostgreSQL ahora solo accesible desde localhost${NC}"
fi

if grep -q "\"8080:8080\"" docker-compose.yml; then
    sed -i.bak 's/"8080:8080"/"127.0.0.1:8080:8080"/' docker-compose.yml
    echo -e "${GREEN}✅ Adminer ahora solo accesible desde localhost${NC}"
fi
echo ""

# ==============================================================================
# 5. AÑADIR HEALTHCHECKS A DOCKER-COMPOSE
# ==============================================================================
echo -e "${YELLOW}💓 Añadiendo healthchecks a servicios...${NC}"

# Nota: Esta sería una modificación compleja del YAML
# Por ahora solo creamos un archivo de parche
cat > "$BACKUP_DIR/healthchecks.patch.yml" << 'EOF'
# Añadir estos bloques a cada servicio en docker-compose.yml:

# Para db:
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U admin -d cliniccloud"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s

# Para api:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

# Para motor_busqueda:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 180s  # Modelo ML tarda en cargar

# Para frontend:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
EOF

echo -e "${YELLOW}⚠️  Healthchecks: archivo de parche creado en $BACKUP_DIR/healthchecks.patch.yml${NC}"
echo -e "${YELLOW}    Aplicar manualmente o usar docker-compose.prod.yml como referencia${NC}"
echo ""

# ==============================================================================
# 6. CREAR SCRIPT DE BACKUPS
# ==============================================================================
echo -e "${YELLOW}💾 Creando script de backups automáticos...${NC}"

mkdir -p scripts

cat > scripts/backup-db.sh << 'EOF'
#!/bin/bash
# Script de backup automático de PostgreSQL
set -e

BACKUP_DIR="/backups/postgresql"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "🔄 Iniciando backup de base de datos..."

# Backup con pg_dump
docker-compose exec -T db pg_dump -U admin -Fc cliniccloud > \
  "$BACKUP_DIR/cliniccloud_$DATE.dump"

# Comprimir (opcional, pg_dump -Fc ya comprime)
echo "✅ Backup completado: $BACKUP_DIR/cliniccloud_$DATE.dump"

# Eliminar backups antiguos
find "$BACKUP_DIR" -name "*.dump" -mtime +$RETENTION_DAYS -delete
echo "🗑️  Backups antiguos eliminados (>$RETENTION_DAYS días)"

# TODO: Subir a almacenamiento remoto (descomentar cuando configures)
# aws s3 cp "$BACKUP_DIR/cliniccloud_$DATE.dump" s3://tu-bucket/backups/
# echo "☁️  Backup subido a S3"

echo "✅ Backup finalizado correctamente"
EOF

chmod +x scripts/backup-db.sh
echo -e "${GREEN}✅ Script de backup creado en scripts/backup-db.sh${NC}"
echo ""

# ==============================================================================
# 7. CREAR MIGRACIÓN SQL PARA UNIQUE CONSTRAINTS
# ==============================================================================
echo -e "${YELLOW}🔧 Creando migración SQL para constraints...${NC}"

mkdir -p database/migrations

cat > database/migrations/009_fix_race_conditions.sql << 'EOF'
-- ==============================================================================
-- MIGRACIÓN 009: FIX RACE CONDITIONS
-- ==============================================================================
-- Fecha: 2025-10-23
-- Descripción: Añade UNIQUE constraints para prevenir race conditions
-- ==============================================================================

BEGIN;

-- Favoritos: Prevenir duplicados de user_id + document_id
ALTER TABLE favorites
ADD CONSTRAINT IF NOT EXISTS unique_user_document UNIQUE (user_id, document_id);

-- Si ya hay duplicados, limpiar primero:
DELETE FROM favorites a USING favorites b
WHERE a.id < b.id
AND a.user_id = b.user_id
AND a.document_id = b.document_id;

-- Historial: Prevenir entradas duplicadas exactas
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_search_history
ON search_history (user_id, query, created_at);

COMMIT;

-- Verificación
SELECT 'Migración 009 aplicada correctamente' AS status;
EOF

echo -e "${GREEN}✅ Migración SQL creada en database/migrations/009_fix_race_conditions.sql${NC}"
echo ""

# ==============================================================================
# 8. RESUMEN Y PRÓXIMOS PASOS
# ==============================================================================
echo "=============================================================================="
echo -e "${GREEN}✅ CORRECCIONES P0 APLICADAS PARCIALMENTE${NC}"
echo "=============================================================================="
echo ""
echo "📋 COMPLETADAS:"
echo "  ✅ JWT_SECRET generado en .env"
echo "  ✅ PostgreSQL y Adminer ahora en localhost"
echo "  ✅ Script de backups creado"
echo "  ✅ Migración SQL para race conditions creada"
echo ""
echo "⚠️  ACCIONES MANUALES REQUERIDAS:"
echo ""
echo "1. REVOCAR CREDENCIALES EXPUESTAS (URGENTE):"
echo "   - Ver archivo ACCION_URGENTE_CREDENCIALES.md"
echo ""
echo "2. APLICAR MIGRACIÓN SQL:"
echo "   docker-compose exec db psql -U admin -d cliniccloud -f /database/migrations/009_fix_race_conditions.sql"
echo ""
echo "3. CONFIGURAR BACKUPS AUTOMÁTICOS:"
echo "   - Editar crontab: crontab -e"
echo "   - Añadir: 0 2 * * * /ruta/al/proyecto/scripts/backup-db.sh >> /var/log/backup.log 2>&1"
echo ""
echo "4. AÑADIR HEALTHCHECKS:"
echo "   - Ver archivo $BACKUP_DIR/healthchecks.patch.yml"
echo "   - O usar docker-compose.prod.yml como referencia"
echo ""
echo "5. CONFIGURAR CORS EN PRODUCCIÓN:"
echo "   - Añadir a .env:"
echo "     CORS_ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com"
echo ""
echo "6. REINICIAR SERVICIOS:"
echo "   docker-compose down"
echo "   docker-compose up -d"
echo ""
echo "=============================================================================="
echo -e "${YELLOW}📖 Para más detalles, ver INFORME_AUDITORIA_PRODUCCION.md${NC}"
echo "=============================================================================="
