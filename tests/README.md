# EduRise Test Suite

This directory contains comprehensive tests for the EduRise platform, organized by functionality.

## Directory Structure

```
tests/
├── ai/                     # AI System Tests
│   ├── test_ai_endpoints.py           # Test AI endpoint accessibility
│   ├── test_ai_authentication.py     # Test AI with authentication
│   ├── test_ai_messaging.py          # Test AI conversation messaging
│   ├── test_ai_api_basic.py          # Basic AI API tests
│   ├── test_gemini_direct.py         # Direct Gemini API tests
│   ├── test_gemini_models.py         # Gemini model availability tests
│   └── test_ai_simple.py             # Simple AI functionality tests
├── integration/            # Integration Tests
│   └── test_ai_system_complete.py    # Complete AI system test
└── README.md              # This file
```

## Running Tests

### Prerequisites
1. Django server must be running: `cd backend && python manage.py runserver`
2. Ensure proper environment variables are set in `backend/.env.development`
3. Admin user must exist with credentials: admin@edurise.com / admin123456

### Individual Test Categories

#### AI System Tests
```bash
# Test AI endpoints accessibility
python tests/ai/test_ai_endpoints.py

# Test AI authentication
python tests/ai/test_ai_authentication.py

# Test AI messaging functionality
python tests/ai/test_ai_messaging.py

# Test basic AI API functionality
python tests/ai/test_ai_api_basic.py

# Test Gemini API directly
python tests/ai/test_gemini_direct.py

# Test Gemini model availability
python tests/ai/test_gemini_models.py
```

#### Integration Tests
```bash
# Complete AI system test (recommended)
python tests/integration/test_ai_system_complete.py
```

### Quick Test Commands

#### Full AI System Verification
```bash
# Run the complete system test (tests everything)
python tests/integration/test_ai_system_complete.py
```

#### AI Endpoint Health Check
```bash
# Quick check if AI endpoints are accessible
python tests/ai/test_ai_endpoints.py
```

#### AI Messaging Test
```bash
# Test AI conversation and messaging
python tests/ai/test_ai_messaging.py
```

## Test Descriptions

### AI System Tests

- **test_ai_endpoints.py**: Verifies all AI endpoints are accessible and return proper authentication requirements
- **test_ai_authentication.py**: Tests authentication flow and AI operations with proper JWT tokens
- **test_ai_messaging.py**: Tests creating conversations and sending messages to AI
- **test_ai_api_basic.py**: Basic API functionality tests without authentication
- **test_gemini_direct.py**: Direct tests of Gemini API integration
- **test_gemini_models.py**: Tests availability of Gemini models

### Integration Tests

- **test_ai_system_complete.py**: Comprehensive end-to-end test of the entire AI system including:
  - Authentication
  - Conversation creation
  - AI messaging with Gemini
  - Usage statistics
  - Conversation management

## Expected Results

All tests should pass with ✅ indicators. If any test fails:

1. **Authentication errors**: Check admin credentials and JWT token handling
2. **Server errors**: Ensure Django server is running and database is accessible
3. **AI errors**: Verify Gemini API key is valid and has quota remaining
4. **Tenant errors**: Ensure proper tenant headers are being sent

## Configuration

Tests use the following configuration:
- **Base URL**: http://127.0.0.1:8000/api/v1
- **Admin User**: admin@edurise.com / admin123456
- **Tenant ID**: 81cbaac8-7f8a-4fd1-b3da-c1ee97945ea3 (Main organization)
- **Gemini API Key**: Set in backend/.env.development

## Troubleshooting

### Common Issues

1. **"Django server not running"**
   - Start server: `cd backend && python manage.py runserver`

2. **"Authentication failed"**
   - Verify admin user exists and password is correct
   - Check if JWT tokens are being generated properly

3. **"Tenant must be set before saving"**
   - Ensure X-Tenant-ID header is being sent with requests
   - Verify tenant middleware is working

4. **"API Key not found"**
   - Check Gemini API key in backend/.env.development
   - Restart Django server after changing environment variables

5. **"Quota exceeded"**
   - Wait for quota reset or use a different API key
   - Check Gemini API console for quota status