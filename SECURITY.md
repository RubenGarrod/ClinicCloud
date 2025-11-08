# Security Policy

**Copyright (C) 2025 Rubén García Rodríguez**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

---

## Known Vulnerabilities

### Current Status

ClinicCloud has **41 identified dependency vulnerabilities** reported by Dependabot:
- **2 Critical** - Deserialization vulnerabilities in `transformers`
- **10 High** - Deserialization and ReDoS vulnerabilities
- **25 Moderate** - Various ReDoS and input validation issues
- **4 Low** - Minor security concerns

### Risk Assessment

#### Transformers Library (Critical/High)
- **Affected packages**: `transformers==4.30.2`
- **Location**: `motor_busqueda/requirements.txt`, `scraper/requirements.txt`
- **Vulnerabilities**: Deserialization of Untrusted Data (CVE-2024-XXXXX)
- **Risk Level**: **LOW** in production context
- **Rationale**:
  - Application uses only pre-validated models from Hugging Face Hub
  - No user-supplied model loading capability
  - Models are pinned to specific, vetted versions
  - No arbitrary file deserialization endpoints exposed

#### Pydantic (Moderate)
- **Affected packages**: `pydantic==2.1.1`
- **Location**: `api/requirements.txt`, `motor_busqueda/requirements.txt`
- **Vulnerabilities**: Regular Expression Denial of Service (ReDoS)
- **Risk Level**: **LOW**
- **Rationale**: Application implements input validation and rate limiting

#### Scrapy (High)
- **Affected packages**: `Scrapy`
- **Location**: `scraper/requirements.txt`
- **Vulnerabilities**: Brotli decompression DoS
- **Risk Level**: **MEDIUM**
- **Rationale**: Scraper targets trusted medical databases (PubMed) only

#### nth-check (High)
- **Affected package**: `nth-check`
- **Location**: `frontend/package-lock.json`
- **Vulnerability**: Inefficient Regular Expression Complexity (ReDoS)
- **Risk Level**: **LOW**
- **Rationale**: Indirect dependency via `svgo` → `react-scripts`. Not exposed in production build.

#### webpack-dev-server (Moderate)
- **Affected package**: `webpack-dev-server`
- **Location**: `frontend/package-lock.json`
- **Vulnerability**: Source code theft via malicious websites
- **Risk Level**: **VERY LOW**
- **Rationale**: Development-only dependency, never deployed to production. Requires developer to visit malicious site during development.

#### PostCSS (Moderate)
- **Affected package**: `postcss`
- **Location**: `frontend/package-lock.json`
- **Vulnerability**: Line return parsing error
- **Risk Level**: **LOW**
- **Rationale**: Build-time dependency, not exposed in production runtime.

---

## Mitigation Strategy

### Immediate Actions Taken
1. **Network Isolation**: Services run in isolated Docker networks
2. **Input Validation**: Comprehensive input sanitization at API level
3. **Rate Limiting**: Redis-based rate limiting prevents DoS attacks
4. **Model Pinning**: Transformer models are explicitly pinned and validated

### Planned Updates
- **Q2 2025**: Upgrade `transformers` to 4.46.x (requires compatibility testing)
- **Q2 2025**: Upgrade `pydantic` to 2.10.x (breaking changes evaluation pending)
- **Q3 2025**: Migrate to React Scripts 6.x (major refactor required)

### Why Not Update Immediately?
Updating dependencies carries significant risk:
- `transformers` 4.30.2 → 4.46.x: Potential breaking changes in model loading
- `pydantic` 2.1.1 → 2.10.x: API changes may affect validation logic
- `react-scripts` 5.0.1 → 6.x: Requires comprehensive frontend refactoring

These updates require dedicated testing sprints to ensure system stability.

---

## Security Best Practices

### For Developers
1. Never load untrusted model files
2. Always validate user inputs before processing
3. Keep Docker images updated via CI/CD pipeline
4. Review Dependabot alerts monthly

### For Deployment
1. Use environment variables for secrets (never hardcode)
2. Enable HTTPS/TLS in production
3. Implement firewall rules (ports 8000, 8001, 80 only)
4. Regular database backups
5. Monitor logs for suspicious activity

---

## Reporting a Vulnerability

If you discover a security vulnerability in ClinicCloud:

1. **DO NOT** open a public GitHub issue
2. Email: cliniccloud.contact@gmail.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if available)

**Response Time**: We aim to respond within 48 hours and provide a fix within 7 days for critical issues.

---

## Security Updates

Security patches are released as soon as possible. Subscribe to:
- GitHub Security Advisories
- Repository releases
- Dependabot alerts (for contributors)

---

**Last Updated**: 2025-01-08
