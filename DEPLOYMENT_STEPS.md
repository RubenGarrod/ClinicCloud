# 🚀 Pasos Rápidos para Deployment en Contabo

**Servidor**: 31.220.73.136
**Usuario**: root
**Password**: Ert441gh

---

## Opción A: Deployment Automático Completo (RECOMENDADO)

### 1. Conectarse al servidor

```bash
ssh root@31.220.73.136
# Password: Ert441gh
```

### 2. Descargar los scripts de deployment

```bash
# Crear directorio temporal
mkdir -p /tmp/cliniccloud-deploy
cd /tmp/cliniccloud-deploy

# Descargar scripts desde GitHub
curl -o cleanup-old-deployment.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/cleanup-old-deployment.sh
curl -o deploy.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/deploy.sh

# Dar permisos de ejecución
chmod +x cleanup-old-deployment.sh
chmod +x deploy.sh
```

### 3. Ejecutar deployment (incluye limpieza automática)

```bash
# El script detectará deployment anterior y te preguntará si quieres limpiarlo
./deploy.sh
```

**El script automáticamente:**
- ✅ Detecta si hay deployment anterior
- ✅ Ofrece ejecutar limpieza automática con backup
- ✅ Instala Docker y Docker Compose
- ✅ Configura firewall
- ✅ Clona el repositorio
- ✅ Genera credenciales seguras
- ✅ Inicializa base de datos
- ✅ Build y deploy de todos los servicios
- ✅ Verifica que todo funcione
- ✅ Configura backups automáticos

---

## Opción B: Limpieza Manual + Deployment

Si prefieres hacer la limpieza por separado:

### 1. Conectarse y descargar scripts

```bash
ssh root@31.220.73.136
cd /tmp
curl -o cleanup-old-deployment.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/cleanup-old-deployment.sh
chmod +x cleanup-old-deployment.sh
```

### 2. Ejecutar limpieza primero

```bash
./cleanup-old-deployment.sh
```

**Este script:**
- ✅ Hace backup de la base de datos actual
- ✅ Detiene y elimina todos los contenedores
- ✅ Elimina imágenes Docker antiguas
- ✅ Limpia directorios de la aplicación
- ✅ Limpia volúmenes Docker (pregunta antes)
- ✅ Guarda backup en `/root/cliniccloud-backup-FECHA/`

### 3. Luego ejecutar deployment

```bash
curl -o deploy.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

---

## Verificación Post-Deployment

### 1. Verificar que los servicios están corriendo

```bash
docker ps
```

Deberías ver 5+ contenedores corriendo:
- cliniccloud_db
- cliniccloud_api
- cliniccloud_frontend
- cliniccloud_search-engine
- cliniccloud_scraper
- cliniccloud_redis

### 2. Verificar health check de API

```bash
curl http://localhost:8000/api/health
```

Respuesta esperada:
```json
{"status":"healthy","database":"connected","redis":"connected"}
```

### 3. Verificar frontend

```bash
curl -I http://localhost:80
```

### 4. Verificar base de datos

```bash
docker exec cliniccloud_db psql -U admin -d cliniccloud -c "SELECT COUNT(*) FROM documento;"
```

### 5. Ver logs en tiempo real

```bash
docker-compose logs -f
```

---

## Acceder a la Aplicación

Una vez completado el deployment:

- **Frontend**: http://31.220.73.136
- **API**: http://31.220.73.136:8000
- **API Docs (Swagger)**: http://31.220.73.136:8000/docs
- **Search Engine**: http://31.220.73.136:8001

---

## Credenciales

Las credenciales generadas automáticamente están en:

```bash
cat /root/cliniccloud-credentials.txt
```

**IMPORTANTE**: Guarda estas credenciales en un lugar seguro y luego elimina el archivo del servidor:

```bash
rm /root/cliniccloud-credentials.txt
```

---

## Backup Anterior

Si ejecutaste el script de limpieza, el backup de la base de datos anterior está en:

```bash
ls -lh /root/cliniccloud-backup-*/
```

Para restaurar el backup si es necesario:

```bash
BACKUP_DIR=$(ls -d /root/cliniccloud-backup-* | tail -1)
docker exec -i cliniccloud_db psql -U admin -d cliniccloud < "$BACKUP_DIR/database_backup.sql"
```

---

## Comandos Útiles

### Ver estado de servicios

```bash
cd /root/ClinicCloud
docker-compose ps
```

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo API
docker-compose logs -f api

# Solo DB
docker-compose logs -f db

# Solo Frontend
docker-compose logs -f frontend
```

### Reiniciar servicios

```bash
# Restart de todos
docker-compose restart

# Restart de uno específico
docker-compose restart api
```

### Stop y Start

```bash
# Detener todo
docker-compose down

# Iniciar todo
docker-compose up -d
```

### Ver uso de recursos

```bash
docker stats
```

### Backups manuales

```bash
/root/ClinicCloud/scripts/backup-db.sh
```

---

## Troubleshooting

### Problema: Servicio no inicia

```bash
# Ver logs detallados
docker-compose logs servicio-problema

# Verificar recursos
docker stats

# Verificar espacio en disco
df -h
```

### Problema: Puerto ya en uso

```bash
# Ver qué proceso usa el puerto
netstat -tulpn | grep :8000

# Matar el proceso
kill -9 PID
```

### Problema: Base de datos no conecta

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps db

# Ver logs de DB
docker-compose logs db

# Entrar a PostgreSQL
docker exec -it cliniccloud_db psql -U admin -d cliniccloud
```

### Problema: Out of memory

```bash
# Ver uso de memoria
free -h

# Limpiar imágenes no usadas
docker system prune -a

# Restart con límites
docker-compose down
docker-compose up -d
```

---

## Rollback a Backup Anterior

Si algo sale mal y necesitas volver al estado anterior:

```bash
# 1. Detener servicios actuales
cd /root/ClinicCloud
docker-compose down

# 2. Restaurar backup de base de datos
BACKUP_DIR=$(ls -d /root/cliniccloud-backup-* | tail -1)

# 3. Iniciar solo la base de datos
docker-compose up -d db
sleep 10

# 4. Restaurar backup
docker exec -i cliniccloud_db psql -U admin -d cliniccloud < "$BACKUP_DIR/database_backup.sql"

# 5. Reiniciar todos los servicios
docker-compose up -d
```

---

## Próximos Pasos (Opcional)

### 1. Configurar Dominio

Si tienes un dominio apuntando al servidor:

```bash
# Instalar Nginx
apt install nginx

# Instalar certbot para SSL
apt install certbot python3-certbot-nginx

# Obtener certificado SSL
certbot --nginx -d tudominio.com
```

### 2. Configurar Monitoreo

- Instalar Prometheus + Grafana
- Configurar alertas
- Monitoreo de logs con ELK Stack

### 3. Optimización

- Configurar CDN para assets estáticos
- Implementar cache con Varnish
- Optimizar queries de base de datos

---

## Soporte

- **Documentación completa**: Ver `DEPLOYMENT_CONTABO.md`
- **GitHub Issues**: https://github.com/RubenGarrod/ClinicCloud/issues
- **Logs del servidor**: `/root/ClinicCloud` + `docker-compose logs`

---

**Copyright (C) 2025 Rubén García Rodríguez**
**Licencia: GNU GPL v3**
