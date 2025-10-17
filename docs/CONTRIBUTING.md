# Contributing to Edurise LMS

Thank you for your interest in contributing to Edurise LMS! This document provides guidelines and information for contributors.

## 🌿 Branching Strategy

We follow a Git Flow branching model with the following structure:

```
main (production-ready)
├── production (pre-production staging)
    ├── development (integration branch)
        ├── feature/user-authentication
        ├── feature/live-class-integration
        ├── feature/ai-tutoring
        └── hotfix/critical-bug-fix
```

### Branch Descriptions

- **`main`** - Production-ready code that is deployed to live environment
- **`production`** - Pre-production staging branch for final testing
- **`development`** - Integration branch where features are merged and tested
- **`feature/*`** - Individual feature development branches
- **`hotfix/*`** - Critical bug fixes that need immediate deployment

## 🚀 Development Workflow

### 1. Setting Up Your Development Environment

```bash
# Clone the repository
git clone https://github.com/Muzamilz/Edurise.git
cd Edurise

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env.development
python manage.py migrate

# Set up frontend
cd ../frontend
npm install
cp .env.example .env.development
```

### 2. Creating a Feature Branch

```bash
# Switch to development branch
git checkout development
git pull origin development

# Create and switch to your feature branch
git checkout -b feature/your-feature-name

# Example feature branch names:
# feature/zoom-integration
# feature/ai-chat-interface
# feature/payment-processing
# feature/multi-language-support
```

### 3. Development Process

1. **Write Tests First** (TDD approach recommended)
   ```bash
   # Backend tests
   cd backend
   python manage.py test tests.test_your_feature
   
   # Frontend tests
   cd frontend
   npm test tests/your-feature.test.ts
   ```

2. **Implement Your Feature**
   - Follow coding standards (see below)
   - Write clean, documented code
   - Ensure all tests pass

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add zoom meeting integration
   
   - Implement ZoomService for meeting creation
   - Add live class scheduling functionality
   - Include attendance tracking features
   - Add comprehensive test coverage
   
   Closes #123"
   ```

### 4. Submitting Your Changes

```bash
# Push your feature branch
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
# Target: development branch
# Include: Description, testing notes, screenshots if applicable
```

## 📝 Commit Message Convention

We use conventional commits for clear and consistent commit messages:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples:
```bash
feat(auth): add Google OAuth integration
fix(zoom): resolve meeting creation timeout issue
docs(api): update Zoom API setup guide
test(classes): add integration tests for live classes
```

## 🧪 Testing Requirements

### Backend Testing
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database interactions
- **Coverage**: Maintain minimum 80% test coverage

```bash
# Run tests
python manage.py test

# Check coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Frontend Testing
- **Unit Tests**: Test Vue components and composables
- **Integration Tests**: Test API interactions and workflows
- **E2E Tests**: Test complete user workflows

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test tests/integration/live-class-integration.test.ts
```

## 📋 Code Standards

### Backend (Django/Python)
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Add type hints where appropriate
- Write docstrings for all functions and classes

```bash
# Format code
black .
isort .

# Check linting
flake8 .
mypy .
```

### Frontend (Vue.js/TypeScript)
- Follow **Vue.js Style Guide**
- Use **Prettier** for code formatting
- Use **ESLint** for linting
- Write TypeScript for type safety
- Use composition API for Vue 3 components

```bash
# Format code
npm run format

# Check linting
npm run lint

# Type checking
npm run type-check
```

## 🔍 Code Review Process

### Pull Request Requirements
1. **Clear Description**: Explain what the PR does and why
2. **Testing**: Include test results and coverage reports
3. **Documentation**: Update relevant documentation
4. **Screenshots**: Include UI changes screenshots
5. **Breaking Changes**: Clearly mark any breaking changes

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Accessibility requirements met

## 🚀 Release Process

### Development → Production Flow

1. **Feature Development**
   ```bash
   feature/xyz → development (via PR)
   ```

2. **Integration Testing**
   ```bash
   # Test in development environment
   # Run full test suite
   # Manual testing of new features
   ```

3. **Pre-Production**
   ```bash
   development → production (via PR)
   # Deploy to staging environment
   # User acceptance testing
   # Performance testing
   ```

4. **Production Release**
   ```bash
   production → main (via PR)
   # Deploy to production
   # Monitor for issues
   # Create release tag
   ```

### Hotfix Process
For critical bugs in production:

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug-fix

# Fix the issue and test
# Commit and push

# Create PR to main for immediate deployment
# Also merge back to development and production
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment**: OS, browser, versions
2. **Steps to Reproduce**: Clear step-by-step instructions
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Screenshots**: If applicable
6. **Logs**: Relevant error messages or logs

## 💡 Feature Requests

When requesting features:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: Your idea for solving it
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Screenshots, mockups, etc.

## 📚 Documentation

### Required Documentation Updates
- **API Changes**: Update OpenAPI/Swagger specs
- **New Features**: Add to user documentation
- **Configuration**: Update setup guides
- **Breaking Changes**: Update migration guides

### Documentation Locations
- **API Docs**: `backend/docs/api/`
- **User Guides**: `docs/user-guides/`
- **Developer Docs**: `docs/developer/`
- **Setup Guides**: Root level (README.md, ZOOM_API_SETUP.md)

## 🤝 Community Guidelines

- **Be Respectful**: Treat all contributors with respect
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Patient**: Remember that everyone is learning
- **Be Inclusive**: Welcome contributors of all backgrounds and skill levels

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Tag maintainers for review help
- **Documentation**: Check existing docs first

## 🏆 Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **Release Notes**: Feature attribution
- **GitHub**: Contributor graphs and statistics

Thank you for contributing to Edurise LMS! 🎉