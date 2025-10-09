# Edurise LMS Platform

A hybrid SaaS Learning Management System that combines the scalability of a public marketplace with the customization of private institutional portals. Built with Django REST Framework and Vue.js, featuring real-time teaching powered by Zoom integration and AI-driven learning assistance via Gemini API.

## 🚀 Features

### Core Functionality
- **Multi-Tenant Architecture** - Support for both public marketplace and private institutional portals
- **Real-Time Live Classes** - Zoom integration for live teaching sessions
- **AI-Powered Learning** - Gemini API integration for tutoring, summaries, and quiz generation
- **Comprehensive Course Management** - Full course lifecycle management
- **Advanced Analytics** - Detailed attendance tracking and engagement metrics
- **Flexible Payment System** - Support for Stripe, PayPal, and bank transfers
- **Multi-Language Support** - English, Arabic (RTL), and Somali

### Technical Features
- **Modern Frontend** - Vue.js 3 with Vite, Animation.js, and Three.js
- **Robust Backend** - Django REST Framework with multi-tenant support
- **Real-Time Communication** - WebSocket integration for live updates
- **Secure Authentication** - JWT tokens with Google OAuth support
- **Scalable Architecture** - Redis caching, Celery background tasks
- **Cloud Storage** - AWS S3/MinIO integration for recordings and files

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Vue.js)      │◄──►│   (Django)      │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • Vue 3 + Vite  │    │ • REST API      │    │ • Zoom API      │
│ • Animation.js  │    │ • Multi-tenant  │    │ • Gemini AI     │
│ • Three.js      │    │ • WebSockets    │    │ • Stripe/PayPal │
│ • Pinia Store   │    │ • Celery Tasks  │    │ • AWS S3/MinIO  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Backend**: Python 3.11+, Django 4.2+, PostgreSQL/SQLite
- **Frontend**: Node.js 18+, npm/yarn
- **External Services**: Zoom API, Google OAuth, Gemini API
- **Optional**: Redis, Celery, AWS S3/MinIO

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Muzamilz/Edurise.git
cd Edurise
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env.development

# Configure your environment variables in .env.development
# See ZOOM_API_SETUP.md for detailed configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.development

# Configure your environment variables in .env.development

# Start development server
npm run dev
```

### 4. Test Zoom API Integration

```bash
cd backend

# Test Zoom API connection
python manage.py test_zoom_api

# Create a test meeting
python manage.py test_zoom_api --create-meeting
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env.development)
```bash
# Django Configuration
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Zoom API
ZOOM_ACCOUNT_ID=your-zoom-account-id
ZOOM_CLIENT_ID=your-zoom-client-id
ZOOM_CLIENT_SECRET=your-zoom-client-secret

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Payment Processing
STRIPE_SECRET_KEY=sk_test_your-stripe-secret
PAYPAL_CLIENT_ID=your-paypal-client-id
```

#### Frontend (.env.development)
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Zoom SDK
VITE_ZOOM_SDK_KEY=your-zoom-sdk-key

# Payment Processing
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
```

See `ZOOM_API_SETUP.md` for detailed Zoom API configuration.

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
python manage.py test

# Run specific test suite
python manage.py test tests.test_simple_live_class

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Run specific test file
npm test tests/integration/live-class-integration.test.ts

# Run with coverage
npm run test:coverage
```

## 🌿 Branching Strategy

We follow a Git Flow branching model:

- **`main`** - Production-ready code
- **`production`** - Pre-production staging
- **`development`** - Integration branch for features
- **`feature/*`** - Individual feature branches

### Workflow:
1. Create feature branch from `development`
2. Develop and test feature
3. Create PR to `development`
4. After testing, merge to `production`
5. After validation, merge to `main`

## 📚 API Documentation

The API documentation is available at:
- Development: `http://localhost:8000/api/docs/`
- Swagger UI: `http://localhost:8000/api/swagger/`

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
1. Set up production environment variables
2. Configure PostgreSQL database
3. Set up Redis for caching and WebSockets
4. Configure Nginx for static files and reverse proxy
5. Set up SSL certificates
6. Configure monitoring and logging

## 📊 Monitoring

- **Application Monitoring**: Sentry integration
- **Performance Monitoring**: Django Debug Toolbar (development)
- **Logging**: Structured logging with rotation
- **Health Checks**: Built-in health check endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- **Backend**: Follow PEP 8, use Black for formatting
- **Frontend**: Follow Vue.js style guide, use Prettier for formatting
- **Testing**: Maintain test coverage above 80%
- **Documentation**: Update docs for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Create an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

## 🙏 Acknowledgments

- **Django REST Framework** - Powerful API framework
- **Vue.js** - Progressive JavaScript framework
- **Zoom API** - Video conferencing integration
- **Google Gemini** - AI-powered features
- **Three.js** - 3D visualizations
- **Animation.js** - Smooth animations

## 📈 Roadmap

- [ ] Mobile app development (React Native)
- [ ] Advanced AI features (personalized learning paths)
- [ ] Integration with more video platforms
- [ ] Advanced analytics and reporting
- [ ] Blockchain-based certificates
- [ ] VR/AR learning experiences

---

**Built with ❤️ for the future of education**