# ClinicCloud

![ClinicCloud Logo](frontend/src/assets/clinic-cloud-logo.png)

**Advanced semantic search system for medical and scientific documentation**

**Copyright (C) 2025 Rubén García Rodríguez**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub release](https://img.shields.io/github/v/release/RubenGarrod/cliniccloud)](https://github.com/RubenGarrod/cliniccloud/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/RubenGarrod/cliniccloud)](https://github.com/RubenGarrod/cliniccloud/releases)
[![GitHub last commit](https://img.shields.io/github/last-commit/RubenGarrod/cliniccloud)](https://github.com/RubenGarrod/cliniccloud/commits)

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-19.1-61DAFB?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.101.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql)](https://github.com/pgvector/pgvector)

**🇬🇧 English** | **[🇪🇸 Español](README_ES.md)**

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technologies Used](#-technologies-used)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Using the System](#-using-the-system)
- [Project Structure](#-project-structure)
- [REST API](#-rest-api)
- [Database](#-database)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 📖 About the Project

**ClinicCloud** is an advanced medical and scientific information search system that uses **natural language processing (NLP)** and **semantic vector search** to facilitate access to high-quality medical documents.

The project is built with a **microservices architecture** deployed in Docker containers, ensuring scalability, portability, and easy maintenance.

### Motivation

Healthcare professionals need rapid access to updated and reliable scientific information. ClinicCloud solves this problem by providing:

- Intelligent semantic search that understands medical context
- Quick access to verified sources like PubMed
- Personalized organization of saved documents
- Search history for research tracking
- Intuitive interface optimized for healthcare professionals

---

## ✨ Key Features

### Advanced Search
- **Semantic vector search** with 768-dimensional embeddings
- **Multilingual processing** (Spanish and English)
- **Medical category filters** (25+ specialties)
- **Sort by relevance, date, or author**
- **Automatic translation** of abstracts (Azure Translator API)

### User Management
- **Authentication system** with JWT
- **Customizable profiles** with 35 animal avatars and 16 colors
- **Language preferences** (ES/EN)
- **Password recovery** via email
- **Email verification** system

### Saved Documents
- **Save documents** for future reference
- **Personal notes** per document
- **Customizable tag system**
- **Search and filter** by tags
- **Flexible organization** of personal library

### History and Analytics
- **Complete search history**
- **Applied filters and categories** recorded
- **Number of results** per search
- **Support for anonymous users** with temporary sessions

### Communication and Support
- **Report issues** directly from the application
- **Automatic email sending** to support team
- **Notification system** with informative toasts
- **Integrated help center**

### Future Improvements (In Development)
- **AI Assistant with RAG** for in-depth document analysis
- **Contextualized answers** based on scientific evidence
- **Conversation history** with the assistant
- **Medical terminology simplification**

---

## 🏗️ System Architecture

ClinicCloud is built with a **decoupled microservices architecture** that communicates through an internal Docker network:

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│                    Port: 80 (HTTP)                           │
│  - Responsive user interface                                │
│  - Internationalization (i18next)                           │
│  - State management with Context API                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    REST API (FastAPI)                        │
│                    Port: 8000 (HTTP)                         │
│  - JWT Authentication                                        │
│  - User, search, favorites endpoints                        │
│  - Email service (SMTP)                                     │
│  - Automatic translation (Azure)                            │
└──────────┬──────────────────────────────┬───────────────────┘
           │                               │
           │ SQL                           │ HTTP
           ▼                               ▼
┌──────────────────────┐    ┌─────────────────────────────────┐
│   DATABASE (Postgres) │    │  SEARCH ENGINE (FastAPI)       │
│   Port: 5432          │    │  Port: 8001                     │
│  - pgvector extension │    │  - Vector search                │
│  - Auth schema        │    │  - Sentence Transformers        │
│  - Public schema      │    │  - Similarity calculation       │
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
                  │  - Categorizer     │
                  │  - NLP Inference   │
                  └────────────────────┘
```

### Services

| Service | Technology | Port | Description |
|---------|-----------|------|-------------|
| **frontend** | React 19 + Nginx | 80 | User web interface |
| **api** | FastAPI + Uvicorn | 8000 | Main REST API |
| **search-engine** | FastAPI + Sentence Transformers | 8001 | Semantic search engine |
| **db** | PostgreSQL + pgvector | 5432 | Vector database |
| **redis** | Redis 7 Alpine | 6379 | Cache and rate limiting |
| **scraper** | Scrapy + Transformers | - | Data extraction and processing (continuous mode) |
| **portainer** | Portainer CE | 9443/9000 | Container management UI |

---

## 🛠️ Technologies Used

### Backend

**Main API:**
- **FastAPI 0.101.0** - Modern and fast web framework
- **Uvicorn 0.23.2** - High-performance ASGI server
- **Pydantic 2.1.1** - Data validation with types
- **PyJWT 2.8.0** - JWT authentication
- **bcrypt 4.0.1** - Secure password hashing
- **psycopg2-binary 2.9.7** - PostgreSQL client
- **asyncpg 0.29.0** - Async PostgreSQL driver
- **psycopg2-pool 1.1** - Connection pooling
- **httpx** - Asynchronous HTTP client
- **email-validator 2.1.0** - Email validation
- **redis 4.6.0** - Redis client for caching
- **fastapi-limiter 0.1.5** - Rate limiting middleware

**Search Engine:**
- **Sentence Transformers 2.2.2** - Embedding generation
  - Model: `pritamdeka/S-PubMedBert-MS-MARCO`
  - Specialized BioBERT fine-tuned on MS-MARCO for medical semantic search
  - Dimension: 768 (native, no padding required)
  - Optimized for medical terminology and scientific literature
- **NumPy 1.25.2** - Vector operations
- **psycopg2-binary 2.9.7** - PostgreSQL client
- **Pydantic 2.1.1 + pydantic-settings 2.0.3** - Configuration management

**Scraper:**
- **Scrapy 2.12.0** - Web scraping framework
- **Transformers 4.30.2** - NLP models for categorization
- **Sentence Transformers 2.2.2** - Medical embedding generation (S-PubMedBert-MS-MARCO)
- **SQLAlchemy 2.0.21** - ORM for database operations
- **schedule 1.2.0** - Continuous scraping scheduler
- **torch** - PyTorch for model inference

### Frontend

- **React 19.1** - Modern UI library
- **React Router 7.5.3** - SPA navigation
- **i18next 25.1** - Internationalization
  - `react-i18next` - React integration
  - `i18next-http-backend` - Translation loading
  - `i18next-browser-languagedetector` - Automatic language detection
- **Lucide React 0.535** - SVG icons
- **React Icons 5.5** - Additional icons
- **Tailwind CSS 3.4** - Utility-first styling framework
  - `@tailwindcss/forms` - Form styles
  - `@tailwindcss/typography` - Typographic styles
- **clsx 2.1** - Conditional class utility

### Database

- **PostgreSQL 16** (pgvector/pgvector:pg16 image)
- **pgvector** - Vector search extension
  - Cosine similarity and inner product operations support
  - Optimized IVFFlat indexes for 768-dimensional vectors
  - Supports vector operations: `<=>` (cosine distance), `<#>` (inner product)

### Cache & Performance

- **Redis 7 Alpine** - In-memory data store
  - Rate limiting for API endpoints
  - Session caching
  - Query result caching

### Infrastructure

- **Docker & Docker Compose** - Containerization
- **Nginx** - Web server for frontend

---

## 📦 Prerequisites

To run ClinicCloud locally, you need:

- **Docker** 20.10+ and **Docker Compose** 2.0+
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Git** 2.30+
  - [Download Git](https://git-scm.com/downloads)
- **Recommended hardware:**
  - 4GB RAM minimum (8GB recommended)
  - 20GB disk space
  - 2+ core processor

### Additional Requirements for Full Functionality

**Optional (for automatic translation):**
- Azure account with Translator API access
- Configured API Key and region

**Optional (for email sending):**
- Gmail account with app password
- Or configured SMTP server

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/RubenGarrod/cliniccloud.git
cd cliniccloud
```

### 2. Configure Environment Variables (Optional)

The project works with default values, but you can customize the configuration by creating a `.env` file in the root directory:

```bash
# ============================================
# DATABASE CONFIGURATION
# ============================================
POSTGRES_USER=cliniccloud
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=cliniccloud

# Database connection (uses POSTGRES_* vars by default)
DB_HOST=db
DB_PORT=5432
DB_NAME=cliniccloud
DB_USER=cliniccloud
DB_PASSWORD=your_secure_password_here

# ============================================
# TRANSLATION CONFIGURATION (Azure Translator)
# ============================================
# Get at: https://portal.azure.com
TRANSLATOR_API_KEY=your_api_key_here
TRANSLATOR_REGION=your_region_here

# ============================================
# EMAIL CONFIGURATION (SMTP)
# ============================================
# For Gmail: use app password
# Instructions: https://support.google.com/accounts/answer/185833
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=ClinicCloud

# ============================================
# APPLICATION CONFIGURATION
# ============================================
APP_URL=http://localhost
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# ============================================
# JWT SECURITY
# ============================================
JWT_SECRET=your_secret_key_here_min_32_chars
JWT_EXPIRE_HOURS=24
JWT_ALGORITHM=HS256
BCRYPT_ROUNDS=12

# ============================================
# REDIS CONFIGURATION
# ============================================
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=
RATE_LIMIT_ENABLED=true

# ============================================
# SEARCH ENGINE CONFIGURATION
# ============================================
MODEL_NAME=pritamdeka/S-PubMedBert-MS-MARCO
EMBEDDING_DIMENSION=768
MAX_QUERY_LENGTH=512

# ============================================
# SCRAPER CONTINUOUS MODE CONFIGURATION
# ============================================
SCRAPER_MAX_DOCS=1000
SCRAPER_BATCH_SIZE=25
SCRAPER_START_HOUR=0
SCRAPER_STOP_HOUR=23
SCRAPER_LOOP_DELAY=1800
```

### 3. Start the Services

```bash
docker-compose up -d
```

This command will:
1. Download necessary Docker images
2. Build custom containers
3. Initialize the database with complete schema
4. Start all microservices

**Note:** The first execution may take 5-10 minutes depending on your Internet connection, as it will download ML models (~500MB).

### 4. Verify Service Status

```bash
docker-compose ps
```

You should see all services as `Up` (running):

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

### 5. Check Logs (Optional)

```bash
# Logs of all services
docker-compose logs -f

# Logs of a specific service
docker-compose logs -f api
docker-compose logs -f search-engine
```

---

## 🔧 Configuration

### Initial Database Configuration

The database is automatically initialized with:

- **pgvector extension** for vector search
- **Auth schema** for users and authentication
- **Public schema** for documents and searches
- **25 predefined medical categories**
- **Optimized indexes** for fast searches
- **Automatic triggers** for timestamps

The file `database/consolidated_schema.sql` is automatically executed on first startup.

### Email Configuration

To enable email sending (account verification, password recovery, issue reports):

1. **Create an app password in Gmail:**
   - Go to [Google Account → Security](https://myaccount.google.com/security)
   - Enable two-step verification
   - Go to "App passwords"
   - Generate a password for "Mail"

2. **Configure in `.env`:**
   ```bash
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=the_generated_app_password
   SMTP_FROM_EMAIL=your_email@gmail.com
   ```

3. **Restart the API service:**
   ```bash
   docker-compose restart api
   ```

### Automatic Translation Configuration

To enable abstract translation:

1. **Create resource in Azure:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create "Translator" resource
   - Get API Key and Region

2. **Configure in `.env`:**
   ```bash
   TRANSLATOR_API_KEY=your_key_here
   TRANSLATOR_REGION=your_region_here  # Example: westeurope
   ```

3. **Restart the API service:**
   ```bash
   docker-compose restart api
   ```

---

## 💻 Using the System

### Access to Interfaces

Once all services are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Web Application** | http://localhost:80 | Main user interface |
| **REST API** | http://localhost:8000 | API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger documentation |
| **API Health** | http://localhost:8000/api/health | Health check endpoint |
| **Search Engine** | http://localhost:8001 | Search engine API |
| **Search Health** | http://localhost:8001/health | Search engine health check |
| **Portainer** | http://localhost:9000 or https://localhost:9443 | Container management UI |

### Database Access

To access the PostgreSQL database directly:

**Using psql:**
```bash
docker-compose exec db psql -U cliniccloud -d cliniccloud
```

**Using Portainer:**
1. Navigate to http://localhost:9000
2. Create an admin account on first access
3. Connect to the local Docker environment
4. Manage containers, view logs, and access console

**Default credentials:**
```
Username:    cliniccloud (configurable via POSTGRES_USER)
Password:    set via POSTGRES_PASSWORD in .env
Database:    cliniccloud
Host:        db (internal) or localhost:5432 (external)
```

### Main Functionalities

#### 1. Document Search

1. Open http://localhost:80
2. Enter medical terms in the search field
   - Example: "diabetes treatment guidelines"
   - Example: "hypertension treatment"
3. Optionally, apply category filters
4. Click the search button (magnifying glass)
5. Explore results sorted by relevance
6. Access original sources through links

#### 2. Create Account and Customize Profile

1. Click "Sign up" in the header
2. Complete the registration form:
   - Full name
   - Email
   - Password (minimum 8 characters)
   - Professional title (Dr., Nurse, etc.)
   - Country and region
   - Institution and specialty
3. Select your favorite avatar (35 animals available)
4. Choose a background color (16 colors)
5. Confirm your email (if SMTP is configured)
6. Log in

#### 3. Save Documents

1. Perform a search
2. In the results, click "Save document"
3. Optionally:
   - Add a personal note
   - Add tags for organization
4. Access your saved documents from the side menu

#### 4. Manage Saved Documents

1. Access "Saved documents" in the side menu
2. Search by title or filter by tags
3. Edit notes or add new tags
4. Consult with AI assistant (coming soon)
5. Remove documents you no longer need

#### 5. Review History

1. Access "History" in the side menu
2. Review all your previous searches
3. Repeat searches with one click
4. Identify patterns in your research

#### 6. Report Issues

1. Click "Report an issue" in the footer
2. Complete the form:
   - Type: Bug or Suggestion
   - Descriptive title
   - Detailed description
   - Contact email (optional)
3. Send the report
4. The team will receive an automatic email

---

## 📁 Project Structure

```
cliniccloud/
├── api/                           # Main REST API
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/         # Endpoints organized by resource
│   │   │       ├── auth/          # Authentication and users
│   │   │       │   ├── __init__.py
│   │   │       │   ├── dependencies.py  # JWT dependencies
│   │   │       │   ├── login.py         # Login and logout
│   │   │       │   ├── register.py      # User registration
│   │   │       │   ├── password.py      # Password recovery
│   │   │       │   └── profile.py       # Profile management
│   │   │       ├── categories.py  # Medical categories
│   │   │       ├── documents.py   # Medical documents
│   │   │       ├── favorites.py   # Saved documents
│   │   │       ├── history.py     # Search history
│   │   │       ├── report_issue.py # Issue reporting
│   │   │       ├── search.py      # Document search
│   │   │       └── translate.py   # Text translation
│   │   ├── config.py              # Global configuration
│   │   ├── db/
│   │   │   └── database.py        # PostgreSQL connection
│   │   ├── models/                # Pydantic models
│   │   │   ├── auth.py
│   │   │   ├── favorites.py
│   │   │   ├── history.py
│   │   │   ├── report_issue.py
│   │   │   ├── search.py
│   │   │   ├── translate.py
│   │   │   └── user.py
│   │   └── services/              # Business logic
│   │       └── email_service.py   # SMTP email service
│   ├── main.py                    # FastAPI entry point
│   ├── requirements.txt           # Python dependencies
│   └── Dockerfile
│
├── motor_busqueda/                # Vector search engine
│   ├── main.py                    # Semantic search API
│   ├── requirements.txt
│   └── Dockerfile
│
├── scraper/                       # Medical data scraper
│   ├── clinic_scraper/
│   │   ├── spiders/
│   │   │   └── pubmed_spider.py  # PubMed spider
│   │   ├── pipelines.py          # Data processing
│   │   └── settings.py           # Scrapy configuration
│   ├── inferencia/
│   │   ├── categorizador.py      # Document classification
│   │   └── motor_inferencia.py   # NLP inference engine
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                      # React application
│   ├── public/
│   │   ├── locales/               # i18next translations
│   │   │   ├── es/
│   │   │   │   └── translation.json
│   │   │   └── en/
│   │   │       └── translation.json
│   │   └── index.html
│   ├── src/
│   │   ├── assets/                # Static resources
│   │   │   ├── animal-icons/      # 35 animal avatars
│   │   │   ├── clinic-cloud-logo.png
│   │   │   ├── es.png             # Spanish flag
│   │   │   └── en.png             # English flag
│   │   ├── components/            # React components
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
│   │   ├── pages/                 # Main pages
│   │   │   ├── FavoritesPage.js
│   │   │   ├── HistoryPage.js
│   │   │   ├── PrivacyPage.js
│   │   │   └── TermsPage.js
│   │   ├── services/              # API services
│   │   │   └── favoritesService.js
│   │   ├── utils/
│   │   │   └── avatarUtils.js
│   │   ├── i18n/
│   │   │   └── index.js           # i18next configuration
│   │   ├── App.js                 # Root component
│   │   ├── index.js               # Entry point
│   │   └── index.css              # Tailwind styles
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── database/                      # Database scripts
│   ├── consolidated_schema.sql   # Complete schema (new installations)
│   ├── migrations/               # Historical migrations
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_auth_system.sql
│   │   ├── 003_search_history.sql
│   │   ├── 004_favorites.sql
│   │   └── 005_user_profiles.sql
│   └── README.md                 # DB documentation
│
├── .gitignore
├── .dockerignore
├── docker-compose.yml            # Service orchestration
├── LICENSE                       # GNU GPL v3.0
├── NOTICE                        # Legal notices
├── CLEANUP_SUMMARY.md            # Cleanup report
├── README.md                     # Spanish version
└── README_EN.md                  # This file
```

---

## 🔌 REST API

The REST API provides endpoints organized by resources:

### Public Endpoints (No authentication required)

#### Search

```http
POST /api/search
Content-Type: application/json

{
  "query": "diabetes treatment",
  "categories": ["Endocrinology"],
  "limit": 20
}
```

**Response:**
```json
{
  "results": [
    {
      "id": 123,
      "title": "Type 2 Diabetes Management Guidelines",
      "authors": ["Smith J.", "Johnson K."],
      "publication_date": "2024-01-15",
      "url": "https://pubmed.ncbi.nlm.nih.gov/...",
      "category": "Endocrinology",
      "similarity_score": 0.92
    }
  ],
  "total": 45,
  "query_time_ms": 120
}
```

#### Medical Categories

```http
GET /api/categories
```

**Response:**
```json
{
  "categories": [
    {"id": 1, "name": "Cardiology"},
    {"id": 2, "name": "Neurology"},
    ...
  ]
}
```

#### Translation

```http
POST /api/translate
Content-Type: application/json

{
  "text": "Type 2 diabetes mellitus treatment",
  "target_language": "es"
}
```

#### Authentication

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/forgot-password
POST /api/auth/reset-password
```

### Protected Endpoints (Require JWT)

Include header: `Authorization: Bearer <token>`

#### User Profile

```http
GET /api/auth/profile
PUT /api/auth/profile
DELETE /api/auth/profile
```

#### Saved Documents

```http
GET /api/favorites
POST /api/favorites
PUT /api/favorites/{id}
DELETE /api/favorites/{id}
GET /api/favorites/tags
```

#### Search History

```http
GET /api/history
DELETE /api/history/{id}
DELETE /api/history/clear
```

#### Issue Reporting

```http
POST /api/report-issue
```

### Interactive Documentation

Access complete Swagger documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## 🗄️ Database

### Main Schema (public)

**Table `documento`:**
- Stores indexed medical documents
- Includes 768-dimensional vector embeddings (S-PubMedBert-MS-MARCO model)
- Optimized IVFFlat indexes for semantic search
- New metadata fields (migration 006):
  - `mesh_terms`: Medical Subject Headings (official NLM categorization)
  - `journal`: Publication journal name
  - `doi`: Digital Object Identifier
  - `publication_types`: Publication type classifications
  - `language`: Document language (ISO 639-2)

**Table `resumen`:**
- Auto-generated summaries for documents
- Created by BART summarization model
- One-to-one relationship with documents

**Table `categoria`:**
- 25+ predefined medical specialties
- 1:N relationship with documents

**Table `search_history`:**
- User search history
- Support for anonymous sessions

**Table `favorites`:**
- User-saved documents
- Personal notes and tags
- Constraint: a user cannot save the same document twice

### Authentication Schema (auth)

**Table `auth.users`:**
- Registered users with hashed passwords (bcrypt)
- Professional information and preferences
- Customizable avatars (35 icons × 16 colors = 560 combinations)

**Table `auth.user_preferences`:**
- Search and display preferences
- Privacy settings

**Table `auth.password_reset_tokens`:**
- Temporary tokens for password recovery
- Automatic cleanup of expired tokens

### Functions and Triggers

- `update_updated_at_column()`: Automatically updates timestamps
- `auth.cleanup_expired_tokens()`: Cleans expired tokens

### Maintenance

**Database backup:**
```bash
docker-compose exec db pg_dump -U cliniccloud cliniccloud > backup.sql
```

**Restore backup:**
```bash
docker-compose exec -T db psql -U cliniccloud cliniccloud < backup.sql
```

**Check DB health:**
```bash
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT COUNT(*) FROM documento;
SELECT COUNT(*) FROM auth.users;
SELECT COUNT(*) FROM favorites;
SELECT COUNT(*) FROM resumen;
"
```

**Check vectorized documents:**
```bash
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL;
"
```

**Clean expired tokens:**
```bash
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT auth.cleanup_expired_tokens();
"
```

---

## 🛠️ Development

### Development Mode

#### Backend (API)

```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend will be available at http://localhost:3000 with hot-reload.

### Running Tests

```bash
# Frontend
cd frontend
npm test

# Backend (requires pytest)
cd api
pip install pytest pytest-asyncio
pytest
```

### Development Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100 search-engine
```

### Specific Rebuilding

If you make changes to a service:

```bash
# Rebuild only one service
docker-compose up -d --build api

# Rebuild everything
docker-compose up -d --build
```

### Development Environment Variables

Create `frontend/.env.development`:

```bash
REACT_APP_API_URL=http://localhost:8000
```

Create `api/.env.development`:

```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

---

## 🐛 Troubleshooting

### Issue: Database Service Won't Start

**Symptoms:**
```
cliniccloud-db exited with code 1
```

**Solution:**
```bash
# Remove volumes and restart
docker-compose down
docker volume rm cliniccloud_postgres-data
docker-compose up -d
```

### Issue: Scraper Not Extracting Data

**Symptoms:**
```
SELECT COUNT(*) FROM documento;
-- Result: 0
```

**Solution:**
```bash
# Check scraper logs
docker-compose logs scraper

# Restart the service
docker-compose restart scraper

# If it persists, check PubMed connectivity
docker-compose exec scraper curl -I https://pubmed.ncbi.nlm.nih.gov
```

### Issue: Search Returns No Results

**Possible causes:**
1. No documents in the database
2. Embeddings were not generated correctly
3. Similarity threshold too high

**Solution:**
```bash
# 1. Verify documents and embeddings
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT COUNT(*) FROM documento WHERE contenido_vectorizado IS NOT NULL;
"

# 2. Check search engine logs
docker-compose logs search-engine

# 3. Verify model is loaded correctly
docker-compose logs search-engine | grep "S-PubMedBert-MS-MARCO"

# 4. Check if vector extension is enabled
docker-compose exec db psql -U cliniccloud -d cliniccloud -c "
SELECT * FROM pg_extension WHERE extname = 'vector';
"
```

**Note:** The search engine now uses ranking by relevance instead of filtering by threshold, so all documents are returned sorted by similarity score.

### Issue: Frontend Doesn't Connect to API

**Symptoms:**
```
Network Error / CORS Error
```

**Solution:**
```bash
# Verify API is running
curl http://localhost:8000/api/health

# Check CORS configuration
docker-compose logs api | grep CORS

# Verify CORS_ORIGINS environment variable
docker-compose exec api printenv | grep CORS

# Restart services
docker-compose restart api frontend
```

**Note:** For production, frontend runs on port 80. For development with `npm start`, it runs on port 3000.

### Issue: Email Not Sending

**Symptoms:**
```
SMTPAuthenticationError: Username and Password not accepted
```

**Solution:**
1. Verify you're using app password (not Gmail password)
2. Verify SMTP_USER and SMTP_FROM_EMAIL are the same
3. Verify two-step verification is enabled

```bash
# Check configuration
docker-compose exec api printenv | grep SMTP

# Restart API
docker-compose restart api
```

### Issue: Port Already in Use

**Symptoms:**
```
Error starting userland proxy: listen tcp 0.0.0.0:80: bind: address already in use
```

**Solution:**
```bash
# Identify process using the port
lsof -i :80  # On Linux/Mac
netstat -ano | findstr :80  # On Windows

# Change port in docker-compose.yml
ports:
  - "8080:80"  # Instead of "80:80"
```

### Restart Everything

If nothing works:

```bash
# Stop everything
docker-compose down

# Remove volumes (WARNING: Deletes data)
docker-compose down -v

# Clean Docker system (WARNING: Affects other projects)
docker system prune -a

# Rebuild from scratch
docker-compose up -d --build
```

---

## 🤝 Contributing

Contributions are welcome! If you want to improve ClinicCloud:

### Contribution Process

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/cliniccloud.git
   cd cliniccloud
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make changes and commit**
   ```bash
   git add .
   git commit -m 'feat: add amazing feature'
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **Open Pull Request**
   - Describe your changes in detail
   - Include tests if applicable
   - Update documentation if necessary

### Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Formatting, whitespace, etc.
- `refactor:` Code refactoring
- `test:` Add or modify tests
- `chore:` Maintenance tasks

### Style Guide

**Python (Backend):**
- Follow PEP 8
- Use type hints
- Document functions with docstrings

**JavaScript (Frontend):**
- Use ESLint with React configuration
- Functional components with hooks
- PascalCase file names for components

### Contribution Areas

We need help with:

- NLP model improvements
- Search optimization
- Automated tests
- Translation to more languages
- UI/UX design
- Documentation
- Integration with more medical sources

### Reporting Bugs

Use the integrated system in the application or create an issue on GitHub including:

- Problem description
- Steps to reproduce
- Expected vs. actual behavior
- Screenshots if applicable
- Environment information (OS, Docker version, etc.)

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

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

### Important Terms

When using, modifying, or distributing this software, you **MUST**:

1. **Retain copyright notices** and attribution to the original author
2. **Release your code under GPL v3.0** (any modification)
3. **Provide source code access** to users
4. **Clearly document your changes**

### Attributions

**Animal Icons:**
- Provided by [Flaticon](https://www.flaticon.com/)
- License: Flaticon License (with attribution)
- Authors: Freepik, Smashicons, and others

**Machine Learning Models:**
- `pritamdeka/S-PubMedBert-MS-MARCO` - Medical semantic search model
  - BioBERT fine-tuned on MS-MARCO dataset
  - License: Apache 2.0
  - Model card: https://huggingface.co/pritamdeka/S-PubMedBert-MS-MARCO

See the [LICENSE](LICENSE) file for the complete license text and [NOTICE](NOTICE) for detailed attributions.

---

## 📧 Contact

**Rubén García Rodríguez**

- **Email:** cliniccloud.contact@gmail.com
- **GitHub:** [@RubenGarrod](https://github.com/RubenGarrod)
- **Project:** [ClinicCloud Repository](https://github.com/RubenGarrod/cliniccloud)

### Support

- **Report issues:** Use the integrated system in the application (footer → "Report an issue")
- **Technical questions:** Open an issue on GitHub
- **General inquiries:** cliniccloud.contact@gmail.com

---

## 🙏 Acknowledgments

- **PubMed/NCBI** for providing free access to medical literature
- **Open Source Community** for the incredible tools used
- **Healthcare professionals** who inspired this project
- **Contributors** who dedicate their time to improving ClinicCloud

---

## 🗺️ Roadmap

### In Development
- [ ] **AI Assistant with RAG** - Conversational document analysis
- [ ] **MCP Server** - Integration with Claude Desktop
- [ ] **Export favorites** to PDF/BibTeX
- [ ] **Analytics charts** for search history

### Future
- [ ] **More data sources** (ClinicalTrials.gov, Cochrane, etc.)
- [ ] **User collaboration** (share collections)
- [ ] **Offline mode** with PWA
- [ ] **Mobile app** (React Native)
- [ ] **Integration with Zotero/Mendeley**

---

<div align="center">

**ClinicCloud** - Intelligent semantic search for evidence-based medicine

Developed with ❤️ by Rubén García Rodríguez © 2025

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

[🇪🇸 Leer en Español](README.md)

</div>
