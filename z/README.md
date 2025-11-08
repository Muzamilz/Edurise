# Edurise - Educational Platform

A comprehensive educational platform built with Django (backend) and Vue.js (frontend), featuring course management, live classes, user authentication, and advanced analytics.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd edurise

# Setup backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Setup frontend (in new terminal)
cd frontend
pnpm install
pnpm run dev
```

## 📁 Project Structure

```
edurise/
├── 📂 backend/              # Django REST API backend
│   ├── apps/               # Django applications
│   ├── config/             # Django configuration
│   ├── templates/          # HTML templates
│   └── tests/              # Backend tests
├── 📂 frontend/            # Vue.js frontend application
│   ├── src/                # Source code
│   ├── tests/              # Frontend tests
│   └── dist/               # Build output
├── 📂 docs/                # 📚 All documentation
│   ├── backend/            # Backend-specific docs
│   └── frontend/           # Frontend-specific docs
├── 📂 scripts/             # 🔧 Utility and setup scripts
│   ├── backend/            # Backend test scripts
│   └── frontend/           # Frontend utility scripts
├── 📂 archive/             # 🗄️ Archived/unused files
└── 📂 .kiro/               # Kiro IDE configuration
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.x + Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Cache**: Redis
- **Authentication**: JWT tokens
- **API Integration**: Zoom API for live classes

### Frontend
- **Framework**: Vue.js 3 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Testing**: Vitest + Playwright
- **3D Graphics**: Three.js
- **Animations**: Custom animation library

## 📚 Documentation

All documentation is organized in the `docs/` directory:

- **[Setup Guide](docs/REPOSITORY_SETUP.md)** - Initial project setup
- **[Data Setup](docs/DATA_SETUP_README.md)** - Database configuration
- **[Redis Setup](docs/REDIS_SETUP.md)** - Redis configuration
- **[Zoom Integration](docs/ZOOM_API_SETUP.md)** - Zoom API setup
- **[Contributing](docs/CONTRIBUTING.md)** - Contribution guidelines

### Backend Documentation
- **[API Summary](docs/backend/CENTRALIZED_API_SUMMARY.md)** - API endpoints overview
- **[Recommendation System](docs/backend/RECOMMENDATION_SYSTEM_SUMMARY.md)** - AI recommendations
- **[Wishlist Implementation](docs/backend/WISHLIST_IMPLEMENTATION_SUMMARY.md)** - Wishlist features

### Frontend Documentation
- **[Integration Status](docs/frontend/INTEGRATION_STATUS.md)** - Current integration status
- **[API Integration](docs/frontend/FRONTEND_API_INTEGRATION_STATUS.md)** - Frontend API usage
- **[Troubleshooting](docs/frontend/TROUBLESHOOTING.md)** - Common issues and solutions

## 🔧 Scripts & Utilities

All scripts are organized in the `scripts/` directory:

### Setup Scripts
```bash
# Setup Redis (Windows)
powershell scripts/setup_redis.ps1

# Setup test data
python scripts/setup_test_data.py
```

### Test Scripts
```bash
# Backend tests
python scripts/backend/test_auth_endpoints.py
python scripts/backend/test_wishlist_api.py

# Frontend tests
node scripts/frontend/run_ai_tests.js
```

### Utility Scripts
```bash
# Fix API endpoints
python scripts/fix_api_endpoints.py

# Clear frontend cache
node scripts/frontend/clear-cache.js
```

## 🌟 Key Features

- **👥 User Management**: Multi-role authentication (Students, Teachers, Admins)
- **📚 Course Management**: Create, manage, and enroll in courses
- **🎥 Live Classes**: Zoom integration for virtual classrooms
- **📊 Analytics**: Comprehensive analytics and reporting
- **💝 Wishlist System**: Course wishlist with analytics
- **🤖 AI Recommendations**: Intelligent course recommendations
- **📱 Responsive Design**: Mobile-first responsive interface
- **🎨 Modern UI**: Beautiful interface with 3D animations
- **🔒 Security**: JWT authentication with refresh tokens
- **⚡ Performance**: Optimized for speed and scalability

## 🚀 Development

### Backend Development
```bash
cd backend
python manage.py runserver
```

### Frontend Development
```bash
cd frontend
pnpm run dev
```

### Building for Production
```bash
# Backend
cd backend
python manage.py collectstatic

# Frontend
cd frontend
pnpm run build
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
pytest
```

### Frontend Tests
```bash
cd frontend
pnpm run test
pnpm run test:e2e
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](docs/LICENSE) file for details.

## 🤝 Contributing

Please read our [Contributing Guide](docs/CONTRIBUTING.md) before submitting pull requests.

## 📞 Support

For support and questions, please check our [Troubleshooting Guide](docs/frontend/TROUBLESHOOTING.md) or contact the development team.

---

**Built with ❤️ by the Edurise Team**