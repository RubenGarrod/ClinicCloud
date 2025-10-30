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
