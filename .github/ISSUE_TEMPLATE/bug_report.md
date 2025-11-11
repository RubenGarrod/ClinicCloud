---
name: Bug Report
about: Report a bug to help us improve ClinicCloud
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 Bug Description

A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce

1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## ✅ Expected Behavior

A clear description of what you expected to happen.

## ❌ Actual Behavior

What actually happened.

## 📸 Screenshots

If applicable, add screenshots to help explain your problem.

## 🖥️ Environment

**Desktop/Laptop:**
- OS: [e.g. Windows 11, Ubuntu 22.04, macOS 14]
- Browser: [e.g. Chrome 120, Firefox 121, Safari 17]
- Docker version: [e.g. 24.0.5]
- Docker Compose version: [e.g. 2.23.0]

**Mobile/Tablet (if applicable):**
- Device: [e.g. iPhone 13, iPad Pro, Samsung Galaxy S23]
- OS: [e.g. iOS 17.2, Android 14]
- Browser: [e.g. Safari, Chrome]

## 📋 Service Logs

Please provide relevant logs from the affected service:

```bash
# For API issues:
docker-compose logs api

# For search issues:
docker-compose logs search-engine

# For database issues:
docker-compose logs db

# For frontend issues:
docker-compose logs frontend
```

<details>
<summary>Paste logs here</summary>

```
[Paste your logs here]
```

</details>

## 🔧 Docker Status

Output of `docker-compose ps`:

```
[Paste output here]
```

## 🌐 Additional Context

Add any other context about the problem here:
- When did this start happening?
- Does it happen consistently or intermittently?
- Have you made any configuration changes?
- Are you using custom environment variables?

## 🔍 Possible Solution (Optional)

If you have an idea of what might be causing the issue or how to fix it, please share!
