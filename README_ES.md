# ClinicCloud

![ClinicCloud Logo](frontend/src/assets/clinic-cloud-logo.png)

**Sistema avanzado de búsqueda semántica para documentación médica y científica**

**Copyright (C) 2025 Rubén García Rodríguez**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-19.1-61DAFB?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.101.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql)](https://github.com/pgvector/pgvector)

**[🇬🇧 English](README.md)** | **🇪🇸 Español**

---

## 📋 Tabla de Contenidos

- [Acerca del Proyecto](#-acerca-del-proyecto)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso del Sistema](#-uso-del-sistema)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API REST](#-api-rest)
- [Base de Datos](#-base-de-datos)
- [Desarrollo](#-desarrollo)
- [Troubleshooting](#-troubleshooting)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## 📖 Acerca del Proyecto

**ClinicCloud** es un sistema de búsqueda avanzada de información médica y científica que utiliza **procesamiento de lenguaje natural (NLP)** y **búsqueda vectorial semántica** para facilitar el acceso a documentos médicos de alta calidad.

El proyecto está construido con una **arquitectura de microservicios** desplegada en contenedores Docker, lo que garantiza escalabilidad, portabilidad y fácil mantenimiento.

### Motivación

Los profesionales de la salud necesitan acceder rápidamente a información científica actualizada y confiable. ClinicCloud soluciona este problema proporcionando:

- Búsqueda semántica inteligente que entiende el contexto médico
- Acceso rápido a fuentes verificadas como PubMed
- Organización personalizada de documentos guardados
- Historial de búsquedas para seguimiento de investigaciones
- Interfaz intuitiva optimizada para profesionales de la salud

---

## ✨ Características Principales

### Búsqueda Avanzada
- **Búsqueda vectorial semántica** con embeddings de 768 dimensiones
- **Procesamiento multilingüe** (español e inglés)
- **Filtros por categoría médica** (25+ especialidades)
- **Ordenación por relevancia, fecha o autor**
- **Traducción automática** de resúmenes (Azure Translator API)

### Gestión de Usuarios
- **Sistema de autenticación** con JWT
- **Perfiles personalizables** con avatares de 35 animales y 16 colores
- **Preferencias de idioma** (ES/EN)
- **Recuperación de contraseña** por email
- **Sistema de verificación** de email

### Documentos Guardados
- **Guardar documentos** para referencia futura
- **Notas personales** por documento
- **Sistema de etiquetas (tags)** personalizables
- **Búsqueda y filtrado** por tags
- **Organización flexible** de la biblioteca personal

### Historial y Análisis
- **Historial completo** de búsquedas
- **Filtros y categorías** aplicadas registradas
- **Número de resultados** por búsqueda
- **Soporte para usuarios anónimos** con sesiones temporales

### Comunicación y Soporte
- **Reportar problemas** directamente desde la aplicación
- **Envío automático de emails** al equipo de soporte
- **Sistema de notificaciones** con toasts informativos
- **Centro de ayuda** integrado

### Futuras Mejoras (En Desarrollo)
- **Asistente IA con RAG** para análisis profundo de documentos
- **Respuestas contextualizadas** basadas en evidencia científica
- **Historial de conversaciones** con el asistente
- **Simplificación de terminología** médica

---

## 🏗️ Arquitectura del Sistema

ClinicCloud está construido con una arquitectura de **microservicios desacoplados** que se comunican a través de una red Docker interna:

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│                    Puerto: 80 (HTTP)                         │
│  - Interfaz de usuario responsive                           │
│  - Internacionalización (i18next)                           │
│  - Gestión de estado con Context API                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API REST (FastAPI)                        │
│                    Puerto: 8000 (HTTP)                       │
│  - Autenticación JWT                                         │
│  - Endpoints de usuarios, búsqueda, favoritos               │
│  - Servicio de emails (SMTP)                                │
│  - Traducción automática (Azure)                            │
└──────────┬──────────────────────────────┬───────────────────┘
           │                               │
           │ SQL                           │ HTTP
           ▼                               ▼
┌──────────────────────┐    ┌─────────────────────────────────┐
│   DATABASE (Postgres) │    │  MOTOR BÚSQUEDA (FastAPI)      │
│   Puerto: 5432        │    │  Puerto: 8001                   │
│  - pgvector extension │    │  - Búsqueda vectorial           │
│  - Schema auth        │    │  - Sentence Transformers        │
│  - Schema public      │    │  - Cálculo de similitud         │
└──────────┬───────────┘    └─────────────┬───────────────────┘
           │                               │
           │ SQL                           │ SQL
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │  SCRAPER (Scrapy)  │
                  │  - PubMed Spider   │
                  │  - Categorizador   │
                  │  - Inferencia NLP  │
                  └────────────────────┘
```

### Servicios

| Servicio | Tecnología | Puerto | Descripción |
|----------|-----------|--------|-------------|
| **frontend** | React 19 + Nginx | 80 | Interfaz web del usuario |
| **api** | FastAPI + Uvicorn | 8000 | API REST principal |
| **search-engine** | FastAPI + Sentence Transformers | 8001 | Motor de búsqueda semántica |
| **db** | PostgreSQL + pgvector | 5432 | Base de datos vectorial |
| **redis** | Redis 7 Alpine | 6379 | Caché y limitación de peticiones |
| **scraper** | Scrapy + Transformers | - | Extracción y procesamiento (modo continuo) |
| **portainer** | Portainer CE | 9443/9000 | Interfaz de gestión de contenedores |

---

## 🛠️ Tecnologías Utilizadas

### Backend

**API Principal:**
- **FastAPI 0.101.0** - Framework web moderno y rápido
- **Uvicorn 0.23.2** - Servidor ASGI de alto rendimiento
- **Pydantic 2.1.1** - Validación de datos con tipos
- **PyJWT 2.8.0** - Autenticación JWT
- **bcrypt 4.0.1** - Hash seguro de contraseñas
- **psycopg2-binary 2.9.7** - Cliente PostgreSQL
- **asyncpg 0.29.0** - Driver PostgreSQL asíncrono
- **psycopg2-pool 1.1** - Pool de conexiones
- **httpx** - Cliente HTTP asíncrono
- **email-validator 2.1.0** - Validación de emails
- **redis 4.6.0** - Cliente Redis para caché
- **fastapi-limiter 0.1.5** - Middleware de limitación de peticiones

**Motor de Búsqueda:**
- **Sentence Transformers 2.2.2** - Generación de embeddings
  - Modelo: `pritamdeka/S-PubMedBert-MS-MARCO`
  - BioBERT especializado fine-tuned en MS-MARCO para búsqueda semántica médica
  - Dimensión: 768 (nativa, sin relleno requerido)
  - Optimizado para terminología médica y literatura científica
- **NumPy 1.25.2** - Operaciones vectoriales
- **psycopg2-binary 2.9.7** - Cliente PostgreSQL
- **Pydantic 2.1.1 + pydantic-settings 2.0.3** - Gestión de configuración

**Scraper:**
- **Scrapy 2.12.0** - Framework de web scraping
- **Transformers 4.30.2** - Modelos NLP para categorización
- **Sentence Transformers 2.2.2** - Generación de embeddings médicos (S-PubMedBert-MS-MARCO)
- **SQLAlchemy 2.0.21** - ORM para operaciones de base de datos
- **schedule 1.2.0** - Programador de scraping continuo
- **torch** - PyTorch para inferencia de modelos

### Frontend

- **React 19.1** - Biblioteca UI moderna
- **React Router 7.5.3** - Navegación SPA
- **i18next 25.1** - Internacionalización
  - `react-i18next` - Integración React
  - `i18next-http-backend` - Carga de traducciones
  - `i18next-browser-languagedetector` - Detección automática de idioma
- **Lucide React 0.535** - Iconos SVG
- **React Icons 5.5** - Iconos adicionales
- **Tailwind CSS 3.4** - Framework de estilos utility-first
  - `@tailwindcss/forms` - Estilos de formularios
  - `@tailwindcss/typography` - Estilos tipográficos
- **clsx 2.1** - Utilidad para clases condicionales

### Base de Datos

- **PostgreSQL 16** (imagen pgvector/pgvector:pg16)
- **pgvector** - Extensión para búsqueda vectorial
  - Soporte para similitud coseno y producto interno
  - Índices IVFFlat optimizados para vectores de 768 dimensiones
  - Soporta operaciones vectoriales: `<=>` (distancia coseno), `<#>` (producto interno)

### Caché y Rendimiento

- **Redis 7 Alpine** - Almacenamiento de datos en memoria
  - Limitación de peticiones para endpoints de API
  - Caché de sesiones
  - Caché de resultados de búsqueda

### Infraestructura

- **Docker & Docker Compose** - Contenedorización
- **Nginx** - Servidor web para el frontend

---

## 📦 Requisitos Previos

Para ejecutar ClinicCloud localmente, necesitas:

- **Docker** 20.10+ y **Docker Compose** 2.0+
  - [Descargar Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Git** 2.30+
  - [Descargar Git](https://git-scm.com/downloads)
- **Hardware recomendado:**
  - 4GB RAM mínimo (8GB recomendado)
  - 20GB de espacio en disco
  - Procesador de 2+ núcleos

### Requisitos Adicionales para Funcionalidad Completa

**Opcional (para traducción automática):**
- Cuenta de Azure con acceso a Translator API
- API Key y región configuradas

**Opcional (para envío de emails):**
- Cuenta de Gmail con contraseña de aplicación
- O servidor SMTP configurado

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/RubenGarrod/cliniccloud.git
cd cliniccloud
```

### 2. Configurar Variables de Entorno (Opcional)

El proyecto funciona con valores predeterminados, pero puedes personalizar la configuración creando un archivo `.env` en el directorio raíz:

```bash
# ============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================
POSTGRES_USER=cliniccloud
POSTGRES_PASSWORD=tu_contraseña_segura_aqui
POSTGRES_DB=cliniccloud

# Conexión a base de datos (usa POSTGRES_* por defecto)
DB_HOST=db
DB_PORT=5432
DB_NAME=cliniccloud
DB_USER=cliniccloud
DB_PASSWORD=tu_contraseña_segura_aqui

# ============================================
# CONFIGURACIÓN DE TRADUCCIÓN (Azure Translator)
# ============================================
# Obtener en: https://portal.azure.com
TRANSLATOR_API_KEY=tu_api_key_aqui
TRANSLATOR_REGION=tu_region_aqui

# ============================================
# CONFIGURACIÓN DE EMAIL (SMTP)
# ============================================
# Para Gmail: usar contraseña de aplicación
# Instrucciones: https://support.google.com/accounts/answer/185833
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion
SMTP_FROM_EMAIL=tu_email@gmail.com
SMTP_FROM_NAME=ClinicCloud

# ============================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================
APP_URL=http://localhost
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# ============================================
# SEGURIDAD JWT
# ============================================
JWT_SECRET=tu_clave_secreta_aqui_min_32_caracteres
JWT_EXPIRE_HOURS=24
JWT_ALGORITHM=HS256
BCRYPT_ROUNDS=12

# ============================================
# CONFIGURACIÓN DE REDIS
# ============================================
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=
RATE_LIMIT_ENABLED=true

# ============================================
# CONFIGURACIÓN DEL MOTOR DE BÚSQUEDA
# ============================================
MODEL_NAME=pritamdeka/S-PubMedBert-MS-MARCO
EMBEDDING_DIMENSION=768
MAX_QUERY_LENGTH=512

# ============================================
# CONFIGURACIÓN DEL SCRAPER EN MODO CONTINUO
# ============================================
SCRAPER_MAX_DOCS=1000
SCRAPER_BATCH_SIZE=25
SCRAPER_START_HOUR=0
SCRAPER_STOP_HOUR=23
SCRAPER_LOOP_DELAY=1800
```

### 3. Iniciar los Servicios

```bash
docker-compose up -d
```

Este comando:
1. Descarga las imágenes Docker necesarias
2. Construye los contenedores personalizados
3. Inicializa la base de datos con el schema completo
4. Inicia todos los microservicios

**Nota:** La primera ejecución puede tardar 5-10 minutos dependiendo de tu conexión a Internet, ya que descargará los modelos de ML (~500MB).

### 4. Verificar el Estado de los Servicios

```bash
docker-compose ps
```

Deberías ver todos los servicios como `Up` (running):

```
NAME                           STATUS
cliniccloud-api                Up
cliniccloud-db                 Up
cliniccloud-frontend           Up
cliniccloud-search-engine      Up
cliniccloud-redis              Up
cliniccloud-scraper            Up
cliniccloud-portainer          Up
```

### 5. Verificar los Logs (Opcional)

```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f api
docker-compose logs -f search-engine
```

---

## 🔧 Configuración

### Configuración Inicial de Base de Datos

La base de datos se inicializa automáticamente con:

- **Extensión pgvector** para búsqueda vectorial
- **Schema auth** para usuarios y autenticación
- **Schema public** para documentos y búsquedas
- **25 categorías médicas** predefinidas
- **Índices optimizados** para búsquedas rápidas
- **Triggers automáticos** para timestamps

El archivo `database/consolidated_schema.sql` se ejecuta automáticamente en el primer inicio.

### Configuración de Email

Para habilitar el envío de emails (verificación de cuenta, recuperación de contraseña, reportes de problemas):

1. **Crear una contraseña de aplicación en Gmail:**
   - Ir a [Cuenta de Google → Seguridad](https://myaccount.google.com/security)
   - Habilitar verificación en dos pasos
   - Ir a "Contraseñas de aplicaciones"
   - Generar una contraseña para "Correo"

2. **Configurar en `.env`:**
   ```bash
   SMTP_USER=tu_email@gmail.com
   SMTP_PASSWORD=la_contraseña_de_aplicacion_generada
   SMTP_FROM_EMAIL=tu_email@gmail.com
   ```

3. **Reiniciar el servicio API:**
   ```bash
   docker-compose restart api
   ```

### Configuración de Traducción Automática

Para habilitar la traducción de resúmenes:

1. **Crear recurso en Azure:**
   - Ir a [Azure Portal](https://portal.azure.com)
   - Crear recurso "Translator"
   - Obtener API Key y Región

2. **Configurar en `.env`:**
   ```bash
   TRANSLATOR_API_KEY=tu_clave_aqui
   TRANSLATOR_REGION=tu_region_aqui  # Ejemplo: westeurope
   ```

3. **Reiniciar el servicio API:**
   ```bash
   docker-compose restart api
   ```

---

## 💻 Uso del Sistema

### Acceso a las Interfaces

Una vez que todos los servicios estén funcionando:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Aplicación Web** | http://localhost:80 | Interfaz principal de usuario |
| **API REST** | http://localhost:8000 | Endpoints de la API |
| **Docs API** | http://localhost:8000/docs | Documentación interactiva Swagger |
| **API Health** | http://localhost:8000/api/health | Endpoint de verificación de salud |
| **Motor de Búsqueda** | http://localhost:8001 | API del motor de búsqueda |
| **Search Health** | http://localhost:8001/health | Verificación de salud del motor |
| **Portainer** | http://localhost:9000 o https://localhost:9443 | Interfaz de gestión de contenedores |

### Acceso a la Base de Datos

Para acceder directamente a la base de datos PostgreSQL:

**Usando psql:**
```bash
docker-compose exec db psql -U cliniccloud -d cliniccloud
```

**Usando Portainer:**
1. Navega a http://localhost:9000
2. Crea una cuenta de administrador en el primer acceso
3. Conecta al entorno Docker local
4. Gestiona contenedores, visualiza logs y accede a la consola

**Credenciales predeterminadas:**
```
Usuario:     cliniccloud (configurable via POSTGRES_USER)
Contraseña:  establecida mediante POSTGRES_PASSWORD en .env
Base de datos: cliniccloud
Host:        db (interno) o localhost:5432 (externo)
```

### Funcionalidades Principales

#### 1. Búsqueda de Documentos

1. Abre http://localhost:80
2. Introduce términos médicos en el campo de búsqueda
   - Ejemplo: "diabetes treatment guidelines"
   - Ejemplo: "hipertensión arterial tratamiento"
3. Opcionalmente, aplica filtros por categoría
4. Haz clic en el botón de búsqueda (lupa)
5. Explora los resultados ordenados por relevancia
6. Accede a las fuentes originales mediante los enlaces

#### 2. Crear Cuenta y Personalizar Perfil

1. Haz clic en "Registrarse" en el header
2. Completa el formulario de registro:
   - Nombre completo
   - Email
   - Contraseña (mínimo 8 caracteres)
   - Título profesional (Dr., Dra., Enf., etc.)
   - País y región
   - Institución y especialidad
3. Selecciona tu avatar favorito (35 animales disponibles)
4. Elige un color de fondo (16 colores)
5. Confirma tu email (si SMTP está configurado)
6. Inicia sesión

#### 3. Guardar Documentos

1. Realiza una búsqueda
2. En los resultados, haz clic en "Guardar documento"
3. Opcionalmente:
   - Añade una nota personal
   - Añade etiquetas (tags) para organizar
4. Accede a tus documentos guardados desde el menú lateral

#### 4. Gestionar Documentos Guardados

1. Accede a "Documentos guardados" en el menú lateral
2. Busca por título o filtra por tags
3. Edita notas o añade nuevos tags
4. Consulta con el asistente IA (próximamente)
5. Elimina documentos que ya no necesites

#### 5. Revisar Historial

1. Accede a "Historial" en el menú lateral
2. Revisa todas tus búsquedas anteriores
3. Repite búsquedas con un solo clic
4. Identifica patrones en tu investigación

#### 6. Reportar Problemas

1. Haz clic en "Report an issue" en el footer
2. Completa el formulario:
   - Tipo: Bug o Sugerencia
   - Título descriptivo
   - Descripción detallada
   - Email de contacto (opcional)
3. Envía el reporte
4. El equipo recibirá un email automático

---

## 📁 Estructura del Proyecto

```
cliniccloud/
├── api/                           # API REST principal
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/         # Endpoints organizados por recurso
│   │   │       ├── auth/          # Autenticación y usuarios
│   │   │       │   ├── __init__.py
│   │   │       │   ├── dependencies.py  # Dependencias JWT
│   │   │       │   ├── login.py         # Login y logout
│   │   │       │   ├── register.py      # Registro de usuarios
│   │   │       │   ├── password.py      # Recuperación contraseña
│   │   │       │   └── profile.py       # Gestión de perfil
│   │   │       ├── categories.py  # Categorías médicas
│   │   │       ├── documents.py   # Documentos médicos
│   │   │       ├── favorites.py   # Documentos guardados
│   │   │       ├── history.py     # Historial de búsquedas
│   │   │       ├── report_issue.py # Reporte de problemas
│   │   │       ├── search.py      # Búsqueda de documentos
│   │   │       └── translate.py   # Traducción de textos
│   │   ├── config.py              # Configuración global
│   │   ├── db/
│   │   │   └── database.py        # Conexión a PostgreSQL
│   │   ├── models/                # Modelos Pydantic
│   │   │   ├── auth.py
│   │   │   ├── favorites.py
│   │   │   ├── history.py
│   │   │   ├── report_issue.py
│   │   │   ├── search.py
│   │   │   ├── translate.py
│   │   │   └── user.py
│   │   └── services/              # Lógica de negocio
│   │       └── email_service.py   # Servicio de emails SMTP
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── requirements.txt           # Dependencias Python
│   └── Dockerfile
│
├── motor_busqueda/                # Motor de búsqueda vectorial
│   ├── main.py                    # API de búsqueda semántica
│   ├── requirements.txt
│   └── Dockerfile
│
├── scraper/                       # Scraper de datos médicos
│   ├── clinic_scraper/
│   │   ├── spiders/
│   │   │   └── pubmed_spider.py  # Spider de PubMed
│   │   ├── pipelines.py          # Procesamiento de datos
│   │   └── settings.py           # Configuración Scrapy
│   ├── inferencia/
│   │   ├── categorizador.py      # Clasificación de documentos
│   │   └── motor_inferencia.py   # Motor de inferencia NLP
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                      # Aplicación React
│   ├── public/
│   │   ├── locales/               # Traducciones i18next
│   │   │   ├── es/
│   │   │   │   └── translation.json
│   │   │   └── en/
│   │   │       └── translation.json
│   │   └── index.html
│   ├── src/
│   │   ├── assets/                # Recursos estáticos
│   │   │   ├── animal-icons/      # 35 avatares de animales
│   │   │   ├── clinic-cloud-logo.png
│   │   │   ├── es.png             # Bandera española
│   │   │   └── en.png             # Bandera inglesa
│   │   ├── components/            # Componentes React
│   │   │   ├── layout/
│   │   │   │   ├── Layout.js
│   │   │   │   ├── TopBar.js
│   │   │   │   ├── Sidebar.js
│   │   │   │   └── Footer.js
│   │   │   ├── ui/
│   │   │   │   ├── Modal.js
│   │   │   │   ├── Button.js
│   │   │   │   ├── Input.js
│   │   │   │   ├── Toast.js
│   │   │   │   └── UserDropdown.js
│   │   │   ├── AboutModal.js
│   │   │   ├── AIAssistantModal.js
│   │   │   ├── AvatarSelector.js
│   │   │   ├── HelpModal.js
│   │   │   ├── HomePage.js
│   │   │   ├── LanguageSelector.js
│   │   │   ├── LoginPage.js
│   │   │   ├── ProfileModal.js
│   │   │   ├── RegisterPage.js
│   │   │   ├── ReportIssueModal.js
│   │   │   ├── ResetPasswordPage.js
│   │   │   ├── ResultsPage.js
│   │   │   └── ThemeToggle.js
│   │   ├── contexts/              # Context API
│   │   │   ├── AuthContext.js
│   │   │   ├── ThemeContext.js
│   │   │   └── ToastContext.js
│   │   ├── pages/                 # Páginas principales
│   │   │   ├── FavoritesPage.js
│   │   │   ├── HistoryPage.js
│   │   │   ├── PrivacyPage.js
│   │   │   └── TermsPage.js
│   │   ├── services/              # Servicios API
│   │   │   └── favoritesService.js
│   │   ├── utils/
│   │   │   └── avatarUtils.js
│   │   ├── i18n/
│   │   │   └── index.js           # Configuración i18next
│   │   ├── App.js                 # Componente raíz
│   │   ├── index.js               # Punto de entrada
│   │   └── index.css              # Estilos Tailwind
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── database/                      # Scripts de base de datos
│   ├── consolidated_schema.sql   # Schema completo (nuevas instalaciones)
│   ├── migrations/               # Migraciones históricas
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_auth_system.sql
│   │   ├── 003_search_history.sql
│   │   ├── 004_favorites.sql
│   │   └── 005_user_profiles.sql
│   └── README.md                 # Documentación de BD
│
├── .gitignore
├── .dockerignore
├── docker-compose.yml            # Orquestación de servicios
├── LICENSE                       # GNU GPL v3.0
├── NOTICE                        # Avisos legales
├── CLEANUP_SUMMARY.md            # Reporte de limpieza
└── README.md                     # Este archivo
```

---

## 🔌 API REST

La API REST proporciona endpoints organizados por recursos:

### Endpoints Públicos (No requieren autenticación)

#### Búsqueda

```http
POST /api/search
Content-Type: application/json

{
  "query": "diabetes treatment",
  "categories": ["Endocrinología"],
  "limit": 20
}
```

**Respuesta:**
```json
{
  "results": [
    {
      "id": 123,
      "title": "Type 2 Diabetes Management Guidelines",
      "authors": ["Smith J.", "Johnson K."],
      "publication_date": "2024-01-15",
      "url": "https://pubmed.ncbi.nlm.nih.gov/...",
      "category": "Endocrinología",
      "similarity_score": 0.92
    }
  ],
  "total": 45,
  "query_time_ms": 120
}
```

#### Categorías Médicas

```http
GET /api/categories
```

**Respuesta:**
```json
{
  "categories": [
    {"id": 1, "name": "Cardiología"},
    {"id": 2, "name": "Neurología"},
    ...
  ]
}
```

#### Traducción

```http
POST /api/translate
Content-Type: application/json

{
  "text": "Type 2 diabetes mellitus treatment",
  "target_language": "es"
}
```

#### Autenticación

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/forgot-password
POST /api/auth/reset-password
```

### Endpoints Protegidos (Requieren JWT)

Incluir header: `Authorization: Bearer <token>`

#### Perfil de Usuario

```http
GET /api/auth/profile
PUT /api/auth/profile
DELETE /api/auth/profile
```

#### Documentos Guardados

```http
GET /api/favorites
POST /api/favorites
PUT /api/favorites/{id}
DELETE /api/favorites/{id}
GET /api/favorites/tags
```

#### Historial de Búsquedas

```http
GET /api/history
DELETE /api/history/{id}
DELETE /api/history/clear
```

#### Reporte de Problemas

```http
POST /api/report-issue
```

### Documentación Interactiva

Accede a la documentación Swagger completa en:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## 🗄️ Base de Datos

### Schema Principal (public)

**Tabla `documento`:**
- Almacena documentos médicos indexados
- Incluye embeddings vectoriales de 768 dimensiones (modelo S-PubMedBert-MS-MARCO)
- Índices IVFFlat optimizados para búsqueda semántica
- Nuevos campos de metadata (migración 006):
  - `mesh_terms`: Medical Subject Headings (categorización oficial NLM)
  - `journal`: Nombre de la revista de publicación
  - `doi`: Digital Object Identifier
  - `publication_types`: Tipos de publicación clasificados
  - `language`: Idioma del documento (ISO 639-2)

**Tabla `resumen`:**
- Resúmenes auto-generados para documentos
- Creados por el modelo de summarización BART
- Relación uno-a-uno con documentos

**Tabla `categoria`:**
- 25+ especialidades médicas predefinidas
- Relación 1:N con documentos

**Tabla `search_history`:**
- Historial de búsquedas de usuarios
- Soporte para sesiones anónimas

**Tabla `favorites`:**
- Documentos guardados por usuarios
- Notas personales y tags
- Restricción: un usuario no puede guardar el mismo documento dos veces

### Schema de Autenticación (auth)

**Tabla `auth.users`:**
- Usuarios registrados con contraseñas hasheadas (bcrypt)
- Información profesional y preferencias
- Avatares personalizables (35 iconos × 16 colores = 560 combinaciones)

**Tabla `auth.user_preferences`:**
- Preferencias de búsqueda y visualización
- Configuración de privacidad

**Tabla `auth.password_reset_tokens`:**
- Tokens temporales para recuperación de contraseña
- Limpieza automática de tokens expirados

### Funciones y Triggers

- `update_updated_at_column()`: Actualiza automáticamente timestamps
- `auth.cleanup_expired_tokens()`: Limpia tokens expirados

### Mantenimiento

**Backup de base de datos:**
```bash
docker-compose exec db pg_dump -U cliniccloud cliniccloud > backup.sql
```

**Restaurar backup:**
```bash
docker-compose exec -T db psql -U cliniccloud cliniccloud < backup.sql
```

**Verificar salud de la BD:**
```bash
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT COUNT(*) FROM documento;
SELECT COUNT(*) FROM auth.users;
SELECT COUNT(*) FROM favorites;
SELECT COUNT(*) FROM resumen;
"
```

**Verificar documentos vectorizados:**
```bash
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL;
"
```

**Limpiar tokens expirados:**
```bash
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT auth.cleanup_expired_tokens();
"
```

---

## 🛠️ Desarrollo

### Modo Desarrollo

#### Backend (API)

```bash
cd api
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

El frontend estará disponible en http://localhost:3000 con hot-reload.

### Ejecutar Tests

```bash
# Frontend
cd frontend
npm test

# Backend (requiere pytest)
cd api
pip install pytest pytest-asyncio
pytest
```

### Logs en Desarrollo

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api

# Ver últimas 100 líneas
docker-compose logs --tail=100 search-engine
```

### Rebuilding Específico

Si realizas cambios en un servicio:

```bash
# Rebuild solo un servicio
docker-compose up -d --build api

# Rebuild todo
docker-compose up -d --build
```

### Variables de Entorno para Desarrollo

Crear `frontend/.env.development`:

```bash
REACT_APP_API_URL=http://localhost:8000
```

Crear `api/.env.development`:

```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

---

## 🐛 Troubleshooting

### Problema: Servicio de Base de Datos no Inicia

**Síntomas:**
```
cliniccloud-db exited with code 1
```

**Solución:**
```bash
# Eliminar volúmenes y reiniciar
docker-compose down
docker volume rm cliniccloud_postgres-data
docker-compose up -d
```

### Problema: Scraper no Extrae Datos

**Síntomas:**
```
SELECT COUNT(*) FROM documento;
-- Resultado: 0
```

**Solución:**
```bash
# Verificar logs del scraper
docker-compose logs scraper

# Reiniciar el servicio
docker-compose restart scraper

# Si persiste, verificar conectividad a PubMed
docker-compose exec scraper curl -I https://pubmed.ncbi.nlm.nih.gov
```

### Problema: Búsqueda no Devuelve Resultados

**Posibles causas:**
1. No hay documentos en la base de datos
2. Los embeddings no se generaron correctamente
3. Threshold de similitud demasiado alto

**Solución:**
```bash
# 1. Verificar documentos y embeddings
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL;
"

# 2. Verificar logs del motor de búsqueda
docker-compose logs search-engine

# 3. Verificar que el modelo se cargó correctamente
docker-compose logs search-engine | grep "S-PubMedBert-MS-MARCO"

# 4. Verificar que la extensión vector está habilitada
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT * FROM pg_extension WHERE extname = 'vector';
"
```

**Nota:** El motor de búsqueda ahora usa ranking por relevancia en lugar de filtrar por threshold, así que todos los documentos se retornan ordenados por score de similitud.

### Problema: Frontend no se Conecta a la API

**Síntomas:**
```
Network Error / CORS Error
```

**Solución:**
```bash
# Verificar que la API está corriendo
curl http://localhost:8000/api/health

# Verificar configuración CORS
docker-compose logs api | grep CORS

# Verificar variable de entorno CORS_ORIGINS
docker-compose exec api printenv | grep CORS

# Reiniciar servicios
docker-compose restart api frontend
```

**Nota:** En producción, el frontend corre en puerto 80. Para desarrollo con `npm start`, corre en puerto 3000.

### Problema: Email no se Envía

**Síntomas:**
```
SMTPAuthenticationError: Username and Password not accepted
```

**Solución:**
1. Verificar que usas contraseña de aplicación (no la contraseña de Gmail)
2. Verificar que SMTP_USER y SMTP_FROM_EMAIL son iguales
3. Verificar que la verificación en dos pasos está habilitada

```bash
# Verificar configuración
docker-compose exec api printenv | grep SMTP

# Reiniciar API
docker-compose restart api
```

### Problema: Puerto ya en Uso

**Síntomas:**
```
Error starting userland proxy: listen tcp 0.0.0.0:80: bind: address already in use
```

**Solución:**
```bash
# Identificar proceso usando el puerto
lsof -i :80  # En Linux/Mac
netstat -ano | findstr :80  # En Windows

# Cambiar puerto en docker-compose.yml
ports:
  - "8080:80"  # En lugar de "80:80"
```

### Reiniciar Todo

Si nada funciona:

```bash
# Parar todo
docker-compose down

# Eliminar volúmenes (CUIDADO: Borra datos)
docker-compose down -v

# Limpiar sistema Docker (CUIDADO: Afecta otros proyectos)
docker system prune -a

# Reconstruir desde cero
docker-compose up -d --build
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si deseas mejorar ClinicCloud:

### Proceso de Contribución

1. **Fork del repositorio**
   ```bash
   git clone https://github.com/tu-usuario/cliniccloud.git
   cd cliniccloud
   ```

2. **Crear rama de feature**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Realizar cambios y commits**
   ```bash
   git add .
   git commit -m 'feat: add amazing feature'
   ```

4. **Push a tu fork**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **Abrir Pull Request**
   - Describe tus cambios en detalle
   - Incluye tests si es aplicable
   - Actualiza documentación si es necesario

### Convenciones de Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formato, espacios, etc.
- `refactor:` Refactorización de código
- `test:` Añadir o modificar tests
- `chore:` Tareas de mantenimiento

### Guía de Estilo

**Python (Backend):**
- Seguir PEP 8
- Usar type hints
- Documentar funciones con docstrings

**JavaScript (Frontend):**
- Usar ESLint con configuración de React
- Componentes funcionales con hooks
- Nombres de archivos en PascalCase para componentes

### Áreas de Contribución

Necesitamos ayuda con:

- Mejora de modelos de NLP
- Optimización de búsquedas
- Tests automatizados
- Traducción a más idiomas
- Diseño UI/UX
- Documentación
- Integración con más fuentes médicas

### Reportar Bugs

Usa el sistema integrado en la aplicación o crea un issue en GitHub incluyendo:

- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs. actual
- Screenshots si es aplicable
- Información del entorno (OS, Docker version, etc.)

---

## 📄 Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3.0 (GPL-3.0)**.

```
Copyright (C) 2025 Rubén García Rodríguez

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

### Términos Importantes

Al usar, modificar o distribuir este software, **DEBES**:

1. **Retener avisos de copyright** y atribución al autor original
2. **Liberar tu código bajo GPL v3.0** (cualquier modificación)
3. **Proporcionar acceso al código fuente** a los usuarios
4. **Documentar tus cambios** claramente

### Atribuciones

**Iconos de Animales:**
- Proporcionados por [Flaticon](https://www.flaticon.com/)
- Licencia: Flaticon License (con atribución)
- Autores: Freepik, Smashicons, y otros

**Modelos de Machine Learning:**
- `pritamdeka/S-PubMedBert-MS-MARCO` - Modelo de búsqueda semántica médica
  - BioBERT fine-tuned en el dataset MS-MARCO
  - Licencia: Apache 2.0
  - Model card: https://huggingface.co/pritamdeka/S-PubMedBert-MS-MARCO

Consulta el archivo [LICENSE](LICENSE) para el texto completo de la licencia y [NOTICE](NOTICE) para atribuciones detalladas.

---

## 📧 Contacto

**Rubén García Rodríguez**

- **Email:** cliniccloud.contact@gmail.com
- **GitHub:** [@RubenGarrod](https://github.com/RubenGarrod)
- **Proyecto:** [ClinicCloud Repository](https://github.com/RubenGarrod/cliniccloud)

### Soporte

- **Reportar problemas:** Usa el sistema integrado en la aplicación (footer → "Report an issue")
- **Preguntas técnicas:** Abre un issue en GitHub
- **Consultas generales:** cliniccloud.contact@gmail.com

---

## 🙏 Agradecimientos

- **PubMed/NCBI** por proporcionar acceso libre a literatura médica
- **Comunidad de Open Source** por las increíbles herramientas utilizadas
- **Profesionales de la salud** que inspiraron este proyecto
- **Contribuidores** que dedican su tiempo a mejorar ClinicCloud

---

## 🗺️ Roadmap

### En Desarrollo
- [ ] **Asistente IA con RAG** - Análisis conversacional de documentos
- [ ] **MCP Server** - Integración con Claude Desktop
- [ ] **Exportación de favoritos** a PDF/BibTeX
- [ ] **Gráficas de análisis** de historial de búsquedas

### Futuro
- [ ] **Más fuentes de datos** (ClinicalTrials.gov, Cochrane, etc.)
- [ ] **Colaboración entre usuarios** (compartir colecciones)
- [ ] **Modo offline** con PWA
- [ ] **App móvil** (React Native)
- [ ] **Integración con Zotero/Mendeley**

---

<div align="center">

**ClinicCloud** - Búsqueda semántica inteligente para medicina basada en evidencia

Desarrollado con ❤️ por Rubén García Rodríguez © 2025

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

[🇬🇧 Read in English](README_EN.md)

</div>
