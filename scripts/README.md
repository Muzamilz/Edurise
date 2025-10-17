# Edurise Platform Scripts

This directory contains all utility scripts, setup scripts, and test scripts for the Edurise platform.

## Directory Structure

```
scripts/
├── README.md                          # This file - scripts overview
├── fix_api_endpoints.py              # API endpoint fixing utility
├── run_ai_integration_tests.py       # AI integration test runner
├── setup_redis.ps1                   # Redis setup PowerShell script
├── setup_test_data.ps1               # Test data setup PowerShell script
├── setup_test_data.py                # Test data setup Python script
├── backend/                          # Backend-specific scripts
│   ├── test_auth_endpoints.py        # Authentication endpoint tests
│   ├── test_token_refresh.py         # Token refresh functionality tests
│   ├── test_wishlist_analytics.py    # Wishlist analytics tests
│   └── test_wishlist_api.py          # Wishlist API tests
└── frontend/                         # Frontend-specific scripts
    ├── clear-cache.js                # Cache clearing utility
    ├── run_ai_tests.js               # AI tests runner
    ├── test-integration.js           # Integration test script
    ├── verify-imports.js             # Import verification utility
    └── test_wishlist_integration.html # Wishlist integration test page
```

## Setup Scripts

### PowerShell Scripts (Windows)
- `setup_redis.ps1` - Sets up Redis server on Windows
- `setup_test_data.ps1` - Populates database with test data

### Python Scripts (Cross-platform)
- `setup_test_data.py` - Alternative test data setup script
- `fix_api_endpoints.py` - Fixes API endpoint configurations

## Test Scripts

### Backend Tests
- `backend/test_auth_endpoints.py` - Tests authentication endpoints
- `backend/test_token_refresh.py` - Tests token refresh functionality
- `backend/test_wishlist_analytics.py` - Tests wishlist analytics
- `backend/test_wishlist_api.py` - Tests wishlist API endpoints

### Frontend Tests
- `frontend/run_ai_tests.js` - Runs AI-related frontend tests
- `frontend/test-integration.js` - Integration testing script
- `frontend/test_wishlist_integration.html` - Wishlist integration test page

## Utility Scripts

### Frontend Utilities
- `frontend/clear-cache.js` - Clears application cache
- `frontend/verify-imports.js` - Verifies import statements

### Backend Utilities
- `run_ai_integration_tests.py` - Comprehensive AI integration testing

## Usage

### Running Setup Scripts

```bash
# Setup Redis (Windows)
powershell -ExecutionPolicy Bypass -File scripts/setup_redis.ps1

# Setup test data (Windows)
powershell -ExecutionPolicy Bypass -File scripts/setup_test_data.ps1

# Setup test data (Cross-platform)
python scripts/setup_test_data.py
```

### Running Test Scripts

```bash
# Backend tests
python scripts/backend/test_auth_endpoints.py
python scripts/backend/test_wishlist_api.py

# Frontend tests
node scripts/frontend/run_ai_tests.js
node scripts/frontend/test-integration.js
```

### Running Utility Scripts

```bash
# Fix API endpoints
python scripts/fix_api_endpoints.py

# Clear frontend cache
node scripts/frontend/clear-cache.js

# Verify imports
node scripts/frontend/verify-imports.js
```

## Notes

- Ensure you have the required dependencies installed before running scripts
- Some scripts may require environment variables to be set
- Check individual script files for specific usage instructions
- PowerShell scripts are designed for Windows environments