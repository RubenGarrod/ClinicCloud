# 🚀 Guía de Deployment - Servidor Contabo

**Servidor**: 31.220.73.136
**Proyecto**: ClinicCloud v1.0
**Fecha**: Octubre 2025

---

## 📋 Pre-requisitos del Servidor

### 1. Software Requerido

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### 2. Configuración del Firewall

```bash
# Puertos necesarios
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8000/tcp    # API (temporal, luego usar nginx)
sudo ufw allow 8001/tcp    # Search Engine (temporal)
sudo ufw enable
```

### 3. Crear Directorios de Datos

```bash
# Crear estructura de directorios
sudo mkdir -p /root/cliniccloud-data/pgdata
sudo mkdir -p /root/cliniccloud-data/transformers-cache
sudo mkdir -p /root/cliniccloud-data/backups

# Permisos
sudo chmod 777 /root/cliniccloud-data/pgdata
sudo chmod 777 /root/cliniccloud-data/transformers-cache
sudo chmod 755 /root/cliniccloud-data/backups
```

---

## 📦 Deployment Steps

### Paso 1: Clonar el Repositorio

```bash
cd /root
git clone https://github.com/RubenGarrod/ClinicCloud.git
cd ClinicCloud
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar el ejemplo
cp .env.example .env

# Editar con credenciales seguras
nano .env
```

**Variables críticas a configurar:**

```bash
# Database (CAMBIAR CONTRASEÑAS)
POSTGRES_USER=admin
POSTGRES_PASSWORD=TU_PASSWORD_SEGURA_AQUI  # ⚠️ CAMBIAR
POSTGRES_DB=cliniccloud

# Redis (CAMBIAR CONTRASEÑAS)
REDIS_PASSWORD=TU_REDIS_PASSWORD_AQUI  # ⚠️ CAMBIAR

# JWT Secret (GENERAR UNO NUEVO)
JWT_SECRET_KEY=TU_JWT_SECRET_SUPER_SEGURO_AQUI  # ⚠️ CAMBIAR

# Email (si usas email service)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password  # ⚠️ CAMBIAR
```

**Generar contraseñas seguras:**

```bash
# Generar password de PostgreSQL
openssl rand -base64 32

# Generar JWT secret
openssl rand -hex 64

# Generar Redis password
openssl rand -base64 32
```

### Paso 3: Inicializar Base de Datos

```bash
# Aplicar schema consolidado
docker-compose up -d db
sleep 10  # Esperar a que PostgreSQL inicie

# Aplicar schema
docker-compose exec -T db psql -U admin -d cliniccloud < database/consolidated_schema.sql

# Aplicar migraciones
for migration in database/migrations/*.sql; do
    echo "Aplicando: $migration"
    docker-compose exec -T db psql -U admin -d cliniccloud < "$migration"
done

# Verificar
docker-compose exec db psql -U admin -d cliniccloud -c "\dt"
```

### Paso 4: Build de Servicios

```bash
# Build de todos los servicios
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Verificar que no hay errores
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config
```

### Paso 5: Iniciar Servicios

```bash
# Iniciar en modo detached
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Ver logs
docker-compose logs -f
```

### Paso 6: Verificar Servicios

```bash
# Verificar que todos los contenedores están corriendo
docker-compose ps

# Verificar logs de cada servicio
docker-compose logs api
docker-compose logs frontend
docker-compose logs search-engine
docker-compose logs scraper
```

---

## ✅ Verificación Post-Deployment

### 1. Health Checks

```bash
# API Health
curl http://31.220.73.136:8000/api/health

# Respuesta esperada:
# {"status":"healthy","database":"connected","redis":"connected"}
```

### 2. Test de Endpoints

```bash
# Test de categorías
curl http://31.220.73.136:8000/api/categories

# Test de búsqueda (requiere autenticación)
curl -X POST http://31.220.73.136:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"diabetes","limit":10}'
```

### 3. Frontend

```bash
# Verificar que el frontend responde
curl -I http://31.220.73.136:80

# Abrir en navegador
# http://31.220.73.136
```

### 4. Verificar Base de Datos

```bash
# Contar documentos
docker-compose exec db psql -U admin -d cliniccloud \
  -c "SELECT COUNT(*) FROM documento;"

# Verificar embeddings
docker-compose exec db psql -U admin -d cliniccloud \
  -c "SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL;"
```

---

## 🔧 Mantenimiento

### Backups Automáticos

```bash
# Configurar cron para backup diario
crontab -e

# Añadir línea (backup a las 3 AM diariamente)
0 3 * * * /root/ClinicCloud/scripts/backup-db.sh
```

### Monitoreo de Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f --tail=100

# Ver logs de un servicio específico
docker-compose logs -f api

# Ver logs con timestamp
docker-compose logs -f -t
```

### Actualizar Aplicación

```bash
# Pull últimos cambios
cd /root/ClinicCloud
git pull origin main

# Rebuild y restart
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Ver logs para verificar
docker-compose logs -f
```

### Restart de Servicios

```bash
# Restart de todos los servicios
docker-compose restart

# Restart de un servicio específico
docker-compose restart api

# Stop y start (más limpio)
docker-compose stop
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🚨 Troubleshooting

### Problema: Servicio no inicia

```bash
# Ver logs detallados
docker-compose logs servicio-problema

# Verificar recursos
docker stats

# Verificar espacio en disco
df -h
```

### Problema: Base de datos no conecta

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps db

# Entrar al contenedor de DB
docker-compose exec db psql -U admin -d cliniccloud

# Verificar logs de DB
docker-compose logs db
```

### Problema: Out of memory

```bash
# Ver uso de memoria
docker stats

# Limpiar imágenes no usadas
docker system prune -a

# Restart con límites de memoria
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Problema: Scraper no funciona

```bash
# Ver logs del scraper
docker-compose logs scraper

# Verificar modelos ML
docker-compose exec scraper ls -lh /app/models

# Reiniciar scraper
docker-compose restart scraper
```

---

## 🔒 Seguridad Post-Deployment

### 1. Cambiar Puertos Expuestos (Opcional con Nginx)

Una vez tengas Nginx configurado, puedes cerrar los puertos 8000 y 8001:

```bash
# Actualizar docker-compose para no exponer puertos directamente
# Dejar que Nginx maneje todo el tráfico
```

### 2. Configurar SSL/TLS con Let's Encrypt

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado (requiere dominio apuntando al servidor)
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

### 3. Configurar Rate Limiting Adicional

Ya tienes rate limiting en la API, pero puedes añadir a nivel de Nginx también.

### 4. Monitoreo de Seguridad

```bash
# Revisar logs de acceso sospechoso
docker-compose logs api | grep -i "429\|401\|403"

# Configurar fail2ban (opcional)
sudo apt install fail2ban
```

---

## 📊 Monitoreo y Métricas

### Logs Centralizados

```bash
# Ver todos los logs con filtro
docker-compose logs -f | grep ERROR

# Exportar logs a archivo
docker-compose logs --since 24h > logs-$(date +%Y%m%d).txt
```

### Métricas de Uso

```bash
# CPU y RAM por contenedor
docker stats --no-stream

# Espacio de volúmenes
docker system df -v
```

---

## 🎯 Checklist Final

Antes de considerar el deployment completo, verificar:

- [ ] Todos los servicios están corriendo (`docker-compose ps`)
- [ ] Health check de API responde OK
- [ ] Frontend accesible desde navegador
- [ ] Base de datos tiene datos (documentos y embeddings)
- [ ] Scraper puede conectarse a la base de datos
- [ ] Logs no muestran errores críticos
- [ ] Backups configurados en cron
- [ ] Contraseñas cambiadas de los defaults
- [ ] Firewall configurado correctamente
- [ ] Espacio en disco suficiente (mínimo 20GB libres)
- [ ] Certificado SSL configurado (si aplica)

---

## 📞 Comandos Útiles de Referencia Rápida

```bash
# Estado de servicios
docker-compose ps

# Logs en tiempo real
docker-compose logs -f

# Restart completo
docker-compose restart

# Stop todos los servicios
docker-compose down

# Start en producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Rebuild forzado
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build --force-recreate

# Entrar a contenedor
docker-compose exec api bash
docker-compose exec db psql -U admin -d cliniccloud

# Backup manual
./scripts/backup-db.sh

# Ver uso de recursos
docker stats

# Limpiar sistema
docker system prune -a
```

---

**Copyright (C) 2025 Rubén García Rodríguez**
**Licencia: GNU GPL v3**
