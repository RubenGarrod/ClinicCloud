# Changelog

All notable changes to ClinicCloud will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-11

### 🎉 First Stable Release

ClinicCloud v1.0.0 marks the first stable release of our advanced semantic search system for medical and scientific documentation. This release provides a fully functional platform for healthcare professionals to search and organize medical literature.

### ✨ Features

#### Search & Discovery
- Medical semantic search using S-PubMedBert-MS-MARCO model specialized for biomedical literature
- 768-dimensional vector embeddings for accurate semantic matching
- 25+ medical specialty categories for filtering
- Multilingual support (Spanish and English)
- Sort results by relevance, date, or author
- Automatic translation of abstracts (Azure Translator API integration)

#### User Management
- Secure JWT-based authentication system
- Customizable user profiles with 35 animal avatars and 16 color themes (560 combinations)
- Language preferences (ES/EN)
- Password recovery via email
- Email verification system

#### Personal Library
- Save documents for future reference
- Add personal notes to each document
- Customizable tag system for organization
- Search and filter saved documents by tags
- Document metadata enrichment (MeSH terms, DOI, journal, publication types)

#### History & Analytics
- Complete search history tracking
- Record of applied filters and categories
- Number of results per search
- Support for anonymous users with temporary sessions

#### Communication & Support
- Integrated issue reporting system
- Automatic email notifications to support team
- Toast notification system
- Comprehensive help center with documentation

#### Technical Infrastructure
- Containerized microservices architecture with Docker
- PostgreSQL 16 with pgvector extension for vector search
- Redis 7 for caching and rate limiting
- Continuous scraper mode for PubMed data extraction
- FastAPI 0.101.0 backend with async support
- React 19.1 frontend with Tailwind CSS
- Health check endpoints for all services
- Portainer CE for container management

### 🖥️ Platform Support
- **Desktop/Laptop**: ✅ Fully optimized
- **Tablet**: ✅ Functional (landscape mode recommended)
- **Mobile**: ⚠️ Functional but UI not optimized (planned for v1.1.0)

### ⚠️ Known Limitations
- Mobile UI requires horizontal scrolling in some views
- Mobile navigation could be improved
- Touch interactions not fully optimized

**Note:** ClinicCloud is designed primarily for desktop use, matching the workflow of healthcare professionals conducting literature research. Mobile optimization is planned for the next minor release.

### 🛠️ Technical Stack

#### Backend
- FastAPI 0.101.0
- Uvicorn 0.23.2
- PostgreSQL 16 with pgvector
- Redis 7 Alpine
- Python 3.11

#### Frontend
- React 19.1
- React Router 7.5.3
- Tailwind CSS 3.4
- i18next 25.1

#### AI/ML
- Sentence Transformers 2.2.2
- S-PubMedBert-MS-MARCO model
- Transformers 4.30.2
- BioBERT for medical NLP

#### Infrastructure
- Docker & Docker Compose
- Nginx
- Scrapy 2.12.0

### 📝 Documentation
- Comprehensive README in English and Spanish
- Detailed installation and configuration guides
- API documentation via Swagger/OpenAPI
- Troubleshooting section
- Architecture diagrams

### 🔒 Security
- Secure password hashing with bcrypt
- JWT token authentication
- Rate limiting on API endpoints
- Environment-based configuration
- No hardcoded credentials

### 🗺️ Roadmap

#### v1.1.0 (Planned - Q1 2025)
- Mobile UI optimization
- Responsive design improvements
- Touch-friendly controls
- Hamburger menu navigation

#### v1.2.0 (Planned - Q2 2025)
- AI Assistant with RAG (Retrieval-Augmented Generation)
- Contextualized answers based on scientific evidence
- Conversation history
- Medical terminology simplification

#### v1.3.0 (Planned - Q2 2025)
- MCP (Model Context Protocol) Server integration
- Claude Desktop integration
- Export favorites to PDF/BibTeX
- Analytics charts for search history

#### Future Enhancements
- Additional data sources (ClinicalTrials.gov, Cochrane, etc.)
- User collaboration features
- Offline mode with PWA
- Mobile applications (React Native)
- Integration with Zotero/Mendeley

### 🙏 Acknowledgments
- PubMed/NCBI for providing free access to medical literature
- HuggingFace for the S-PubMedBert-MS-MARCO model
- Open Source Community for the incredible tools used
- Healthcare professionals who inspired this project

### 📦 Installation

See [README.md](README.md) for detailed installation instructions.

Quick start:
```bash
git clone https://github.com/RubenGarrod/cliniccloud.git
cd cliniccloud
docker-compose up -d
```

Access the application at http://localhost:80

### 🐛 Known Issues
- None reported for core functionality

### 📄 License
GNU General Public License v3.0 (GPL-3.0)

---

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Fixed
- Nothing yet

---

[1.0.0]: https://github.com/RubenGarrod/cliniccloud/releases/tag/v1.0.0
