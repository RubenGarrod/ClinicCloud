# 🚀 ClinicCloud Deployment Scripts

Automated deployment scripts for ClinicCloud on production servers.

---

## 📁 Files in this Directory

### `deploy.sh`
**Fully automated deployment script**

- Detects previous deployments automatically
- Installs Docker and Docker Compose
- Configures firewall and system directories
- Clones repository from GitHub
- Generates secure credentials (PostgreSQL, Redis, JWT)
- Initializes database with schema and migrations
- Builds and starts all Docker services
- Verifies deployment success
- Configures automatic daily backups

**Usage:**
```bash
curl -o deploy.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/deployment/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### `cleanup.sh`
**Safe cleanup of previous deployments**

- Creates database backup before any cleanup
- Removes old containers and images
- Cleans up application directories
- Interactive confirmations for destructive operations
- Preserves backup in `/root/cliniccloud-backup-{date}/`

**Usage:**
```bash
curl -o cleanup.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/deployment/cleanup.sh
chmod +x cleanup.sh
./cleanup.sh
```

### `STEPS.md`
**Quick reference guide** with step-by-step instructions, verification commands, troubleshooting tips, and rollback procedures.

---

## 🎯 Quick Start - New Deployment

**For Contabo Server (31.220.73.136):**

```bash
# 1. Connect to server
ssh root@31.220.73.136

# 2. Download and run deployment script
curl -o deploy.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/deployment/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Detect if there's a previous deployment
- Offer to clean it up automatically (with backup)
- Install everything needed
- Deploy the application
- Verify it's working

**Total time: ~15-20 minutes** (depending on internet speed for Docker images)

---

## 🔄 Upgrading Existing Deployment

If you already have ClinicCloud running and want to upgrade:

```bash
cd /root/ClinicCloud
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

Or use the deployment script which will handle everything:
```bash
./deploy.sh
# Select option 1 when asked about previous deployment
```

---

## 🧹 Clean Deployment from Scratch

If you want a completely fresh start:

```bash
# 1. Download cleanup script
curl -o cleanup.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/deployment/cleanup.sh
chmod +x cleanup.sh

# 2. Run cleanup (will backup database first)
./cleanup.sh

# 3. Run deployment
curl -o deploy.sh https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/deployment/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

---

## ✅ Post-Deployment Verification

### Check all services are running
```bash
docker ps
```

### Test API health
```bash
curl http://localhost:8000/api/health
```

### Test frontend
```bash
curl -I http://localhost:80
```

### View logs
```bash
cd /root/ClinicCloud
docker-compose logs -f
```

---

## 📊 What Gets Deployed

- **Frontend**: React 18 application (port 80)
- **API**: FastAPI backend (port 8000)
- **Search Engine**: FastAPI microservice (port 8001)
- **Database**: PostgreSQL 15 with pgvector
- **Redis**: Session and rate limiting cache
- **Scraper**: Automated document scraper

---

## 🔒 Security Features

- Automatic generation of secure passwords (OpenSSL random)
- JWT secret key generation
- Firewall configuration (UFW)
- Rate limiting enabled
- Session management with Redis
- Input validation (dual-layer)
- XSS protection (DOMPurify)

Credentials are saved in `/root/cliniccloud-credentials.txt` - **save them and delete the file**.

---

## 💾 Backups

### Automatic Backups
The deployment script configures daily automatic backups at 3 AM via cron:
```bash
crontab -l  # View scheduled backups
```

### Manual Backup
```bash
cd /root/ClinicCloud
./scripts/backup-db.sh
```

Backups are stored in `/root/cliniccloud-data/backups/`

---

## 🐛 Troubleshooting

### Service won't start
```bash
docker-compose logs service-name
docker stats  # Check resources
df -h  # Check disk space
```

### Database connection issues
```bash
docker-compose logs db
docker exec -it cliniccloud_db psql -U admin -d cliniccloud
```

### Out of memory
```bash
free -h
docker system prune -a  # Clean up unused images
```

### Port conflicts
```bash
netstat -tulpn | grep :8000
# Kill process if needed
```

---

## 📚 Additional Documentation

- **Complete Guide**: See `../DEPLOYMENT_CONTABO.md` in repository root
- **Quick Steps**: See `STEPS.md` in this directory
- **Main README**: See `../README.md` for project overview

---

## 🆘 Support

- **Issues**: https://github.com/RubenGarrod/ClinicCloud/issues
- **Documentation**: Check `DEPLOYMENT_CONTABO.md` for comprehensive guide
- **Logs**: Always check `docker-compose logs` first

---

## 📝 Requirements

- Ubuntu 20.04+ or Debian 11+
- 4GB+ RAM (8GB recommended)
- 20GB+ disk space
- Root access
- Internet connection

---

**Copyright (C) 2025 Rubén García Rodríguez**
**License: GNU GPL v3**
