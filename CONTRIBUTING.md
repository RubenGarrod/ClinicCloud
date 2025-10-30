# Contributing to ClinicCloud

Thank you for your interest in contributing to ClinicCloud! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Age, body size, disability, ethnicity, gender identity and expression
- Level of experience, nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable behaviors:**
- Harassment, trolling, or discriminatory comments
- Publishing others' private information without permission
- Any conduct that could be considered unprofessional

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** - Descriptive and specific
- **Steps to reproduce** - Detailed instructions
- **Expected behavior** - What should happen
- **Actual behavior** - What actually happens
- **Environment** - OS, browser, versions
- **Screenshots** - If applicable
- **Logs** - Error messages or stack traces

**Template:**
```markdown
## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Docker: [e.g., 24.0.7]
- ClinicCloud Version: [e.g., 0.1.0]

## Logs
```
Paste relevant logs here
```
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear title** - What feature you're proposing
- **Use case** - Why this feature would be useful
- **Implementation ideas** - How it could work (optional)
- **Alternatives** - Other solutions you've considered

### Your First Code Contribution

Unsure where to start? Look for issues tagged with:
- `good-first-issue` - Simple issues for beginners
- `help-wanted` - Issues where we need help
- `documentation` - Improvements to docs

## Development Setup

### Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0
- Git >= 2.0
- Python 3.10+ (for local development)
- Node.js 18+ (for frontend local development)

### Setup Instructions

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/ClinicCloud.git
   cd ClinicCloud
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/RubenGarrod/ClinicCloud.git
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env
   ```

4. **Start development environment**
   ```bash
   docker-compose up -d
   ```

5. **Verify setup**
   ```bash
   # Check all services are running
   docker-compose ps

   # Check API health
   curl http://localhost:8000/api/health/detailed

   # Open in browser
   open http://localhost
   ```

### Development Workflow

```bash
# Keep your fork updated
git fetch upstream
git checkout main
git merge upstream/main

# Create a feature branch
git checkout -b feature/my-new-feature

# Make your changes
# ...

# Run tests
bash scripts/test-integraciones.sh

# Commit changes
git add .
git commit -m "Add: new feature X"

# Push to your fork
git push origin feature/my-new-feature

# Create Pull Request on GitHub
```

## Coding Standards

### Python (Backend)

- **Style Guide**: PEP 8
- **Formatter**: Black with line length 100
- **Linter**: Flake8
- **Type Hints**: Use type hints for function signatures

```python
# Good
def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a user by their ID.

    Args:
        user_id: The user's unique identifier

    Returns:
        User dictionary if found, None otherwise
    """
    # Implementation...
    pass

# Bad
def get_user(id):
    # No docstring, no type hints
    pass
```

### JavaScript/React (Frontend)

- **Style Guide**: ESLint + Prettier
- **Component Style**: Functional components with hooks
- **File Naming**: PascalCase for components, camelCase for utilities
- **Props**: Use destructuring

```javascript
// Good
const UserProfile = ({ userId, onUpdate }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Load user
  }, [userId]);

  return <div>{user?.name}</div>;
};

// Bad
function UserProfile(props) {
  // Class component or non-destructured props
}
```

### General Guidelines

- **Comments**: Write code that's self-documenting; comment only complex logic
- **Functions**: Keep functions small and focused (< 50 lines)
- **Names**: Use descriptive names (no single letters except loop counters)
- **DRY**: Don't Repeat Yourself - extract common code
- **Error Handling**: Always handle errors gracefully with logging

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Commit Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, no logic change)
- `refactor` - Code refactoring (no feature change)
- `perf` - Performance improvements
- `test` - Adding or updating tests
- `chore` - Maintenance tasks (dependencies, build, etc.)

### Examples

```bash
# Feature
git commit -m "feat(api): add endpoint for user preferences"

# Bug fix
git commit -m "fix(auth): correct JWT expiration validation"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Refactor
git commit -m "refactor(search): optimize query performance"
```

### Commit Body (Optional)

For complex changes, add a body explaining:
- **Why** the change was made
- **What** was the previous behavior
- **What** is the new behavior

```
feat(api): add rate limiting to search endpoint

Search endpoint was vulnerable to abuse. Added rate limiting
with Redis backend to allow max 30 requests/minute for
authenticated users and 10/minute for anonymous users.

Closes #123
```

## Pull Request Process

### Before Submitting

1. ✅ Update your branch with latest `main`
2. ✅ Run all tests and ensure they pass
3. ✅ Update documentation if needed
4. ✅ Add tests for new features
5. ✅ Follow coding standards
6. ✅ Commit messages follow guidelines

### PR Title and Description

**Title**: Use same format as commit messages
```
feat(api): add user session management
```

**Description**: Include:
- **What** - What does this PR do?
- **Why** - Why is this change needed?
- **How** - How was it implemented?
- **Testing** - How was it tested?
- **Screenshots** - For UI changes
- **Related Issues** - Closes #123

**Template:**
```markdown
## Description
Brief description of what this PR does.

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- Change 1
- Change 2
- Change 3

## Testing
How has this been tested?
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
- [ ] Branch updated with main

## Screenshots (if applicable)
Before | After
```

### Review Process

1. **Automated checks** - CI/CD must pass
2. **Code review** - At least 1 approval required
3. **Testing** - Reviewer may test manually
4. **Feedback** - Address comments and suggestions
5. **Approval** - Once approved, maintainers will merge

### After Merge

- Delete your feature branch
- Update your local `main` branch
- Close related issues

## Testing

### Running Tests

```bash
# All integration tests
bash scripts/test-integraciones.sh

# Backend unit tests
docker-compose exec api pytest tests/

# Backend with coverage
docker-compose exec api pytest --cov=app tests/

# Frontend tests
docker-compose exec frontend npm test

# Linting
docker-compose exec api flake8 app/
docker-compose exec frontend npm run lint
```

### Writing Tests

**Backend (pytest):**
```python
import pytest
from app.core.validation import validate_email

def test_validate_email_valid():
    valid, error = validate_email("user@example.com")
    assert valid is True
    assert error is None

def test_validate_email_invalid():
    valid, error = validate_email("invalid-email")
    assert valid is False
    assert "formato inválido" in error.lower()
```

**Frontend (Jest):**
```javascript
import { render, screen } from '@testing-library/react';
import LoginModal from './LoginModal';

test('renders login form', () => {
  render(<LoginModal isOpen={true} />);
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
});
```

### Test Coverage

We aim for:
- **Backend**: > 80% coverage
- **Frontend**: > 70% coverage
- **Critical paths**: 100% coverage (auth, payment, data loss)

## Questions?

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and ideas
- **Email**: soporte@cliniccloud.com

## Recognition

Contributors will be recognized in:
- README.md contributors section
- GitHub contributors page
- Release notes

Thank you for contributing to ClinicCloud! 🏥💙
