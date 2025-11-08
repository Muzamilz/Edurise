# EduRise Platform Comprehensive Testing Suite

This directory contains the comprehensive testing suite for the EduRise platform, covering all aspects of functionality from unit tests to end-to-end user journeys.

## Test Structure

### 1. Unit Tests (`10.1 Unit Testing` - ✅ Completed)
- **Location**: `apps/*/tests/`
- **Purpose**: Test individual components, models, views, serializers, and services
- **Coverage**: All ViewSets, models, authentication, permissions, business logic

**Key Test Files:**
- `apps/accounts/tests/test_enhanced_views.py` - Enhanced authentication features
- `apps/payments/tests/test_views.py` - Payment processing
- `apps/payments/tests/test_models.py` - Payment models
- `apps/courses/tests/test_views.py` - Course management
- `apps/courses/tests/test_models.py` - Course models
- `apps/files/tests/test_views.py` - File management
- `apps/ai/tests/test_views.py` - AI integration

### 2. Integration Tests (`10.2 Integration Testing` - ✅ Completed)
- **Location**: `backend/tests/`
- **Purpose**: Test component interactions and complete workflows
- **Coverage**: API workflows, external services, WebSocket connections, file operations

**Key Test Files:**
- `test_complete_user_workflows.py` - Complete user registration to course completion
- `test_external_service_integrations.py` - Stripe, PayPal, Zoom, AI services, email
- `test_centralized_api_integration.py` - Centralized API endpoints and authentication
- `test_course_management_integration.py` - Course creation and management workflows
- `test_live_class_integration.py` - Live class functionality with Zoom integration

### 3. Performance Tests (`10.3 Performance Testing` - ✅ Completed)
- **Location**: `backend/tests/test_performance.py`
- **Purpose**: Test system performance under load and optimization
- **Coverage**: API response times, database queries, file operations, concurrent users

**Test Categories:**
- API response time testing
- Database query optimization
- File upload/download performance
- Concurrent user scenarios
- Memory usage optimization
- Cache performance

### 4. End-to-End Tests (`10.4 End-to-End Testing` - ✅ Completed)
- **Location**: `backend/tests/test_end_to_end.py`
- **Purpose**: Test complete user journeys from start to finish
- **Coverage**: Registration to completion, payment flows, live classes, AI features

**Test Scenarios:**
- Complete student journey (free course)
- Instructor course creation workflow
- Paid course enrollment with payment processing
- Live class creation and attendance
- AI-powered features workflow
- Admin management workflows
- Multi-tenant functionality

## Running Tests

### Quick Start

```bash
# Run all tests
python backend/tests/run_comprehensive_tests.py

# Run specific test suite
python backend/tests/run_comprehensive_tests.py --suite unit
python backend/tests/run_comprehensive_tests.py --suite integration
python backend/tests/run_comprehensive_tests.py --suite performance
python backend/tests/run_comprehensive_tests.py --suite e2e

# Run with verbose output
python backend/tests/run_comprehensive_tests.py --verbose

# Run with fail-fast (stop on first failure)
python backend/tests/run_comprehensive_tests.py --failfast

# Skip specific suites
python backend/tests/run_comprehensive_tests.py --skip performance e2e
```

### Individual Test Commands

```bash
# Unit tests
python manage.py test apps.accounts.tests.test_enhanced_views
python manage.py test apps.payments.tests.test_views
python manage.py test apps.courses.tests.test_views

# Integration tests
python manage.py test tests.test_complete_user_workflows
python manage.py test tests.test_external_service_integrations

# Performance tests
python manage.py test tests.test_performance

# End-to-end tests
python manage.py test tests.test_end_to_end
```

### Coverage Analysis

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Test Configuration

### Environment Setup

Tests require the following environment setup:

1. **Database**: SQLite for testing (configured in settings)
2. **Cache**: In-memory cache for testing
3. **File Storage**: Local file system for testing
4. **External Services**: Mocked (Stripe, PayPal, Zoom, AI services)

### Mock Services

External services are mocked in tests to ensure:
- Tests run without external dependencies
- Consistent test results
- Fast test execution
- No external API costs

**Mocked Services:**
- Stripe payment processing
- PayPal payment processing
- Zoom meeting creation
- OpenAI/Gemini AI services
- Email sending
- File storage (S3)

### Test Data

Tests use factory patterns and fixtures to create consistent test data:
- Organizations (tenants)
- Users with different roles
- Courses and modules
- Enrollments and progress
- Payments and invoices
- Live classes and attendance

## Performance Benchmarks

### API Response Time Targets

| Endpoint Type | Target Response Time |
|---------------|---------------------|
| Course List | < 2.0s |
| Course Search | < 1.5s |
| Dashboard | < 3.0s |
| Enrollment | < 2.0s |
| Analytics | < 5.0s |

### Database Query Optimization

- Use `select_related()` for foreign key relationships
- Use `prefetch_related()` for many-to-many relationships
- Implement proper indexing
- Use `only()` and `defer()` for field optimization
- Implement query result caching

### Concurrent User Handling

Tests verify the system can handle:
- 10+ concurrent API requests
- Multiple database connections
- Concurrent file operations
- Real-time WebSocket connections

## Continuous Integration

### GitHub Actions Integration

```yaml
name: Comprehensive Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run comprehensive tests
        run: |
          python backend/tests/run_comprehensive_tests.py --verbose
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up pre-commit hooks
pre-commit install

# Run tests before commit
pre-commit run --all-files
```

## Test Maintenance

### Adding New Tests

1. **Unit Tests**: Add to appropriate `apps/*/tests/` directory
2. **Integration Tests**: Add to `backend/tests/` with descriptive names
3. **Performance Tests**: Add to `test_performance.py`
4. **E2E Tests**: Add to `test_end_to_end.py`

### Test Naming Conventions

- `test_<functionality>_<scenario>()` for unit tests
- `test_<workflow>_integration()` for integration tests
- `test_<component>_performance()` for performance tests
- `test_<journey>_e2e()` for end-to-end tests

### Mock Management

- Keep mocks simple and focused
- Use `patch` decorators for external services
- Create reusable mock factories
- Document mock behavior

## Troubleshooting

### Common Issues

1. **Database Errors**: Ensure test database is properly configured
2. **Import Errors**: Check Python path and Django settings
3. **Mock Failures**: Verify mock patches match actual service interfaces
4. **Timeout Errors**: Increase timeout for performance tests
5. **Memory Issues**: Use iterators for large datasets

### Debug Mode

```bash
# Run tests with debug output
python manage.py test --debug-mode --verbosity=2

# Run specific failing test
python manage.py test tests.test_complete_user_workflows.CompleteUserRegistrationWorkflowTest.test_complete_user_registration_workflow --verbosity=2
```

### Performance Profiling

```bash
# Profile test execution
python -m cProfile -o test_profile.prof manage.py test tests.test_performance

# Analyze profile
python -c "import pstats; pstats.Stats('test_profile.prof').sort_stats('cumulative').print_stats(20)"
```

## Test Results and Reporting

### Test Output

The comprehensive test runner provides:
- ✅/❌ Status for each test suite
- Execution time for each suite
- Summary of passed/failed tests
- Detailed error output (with --verbose)

### Coverage Reports

Generate coverage reports to ensure comprehensive testing:

```bash
coverage run --source='.' manage.py test
coverage report --show-missing
coverage html --directory=htmlcov
```

Target coverage: **85%+ overall**, **90%+ for critical paths**

## Integration with Development Workflow

### Pre-deployment Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Performance tests meet benchmarks
- [ ] E2E tests cover critical user journeys
- [ ] Code coverage meets targets
- [ ] No security vulnerabilities detected

### Monitoring and Alerts

Set up monitoring for:
- Test execution time trends
- Test failure rates
- Performance regression detection
- Coverage trend analysis

This comprehensive testing suite ensures the EduRise platform maintains high quality, performance, and reliability across all features and user scenarios.