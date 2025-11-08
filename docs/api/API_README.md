# EduRise LMS API Documentation

## Overview

The EduRise LMS API provides a comprehensive, standardized interface for all frontend applications. It centralizes all endpoints from different Django apps and provides consistent response formats, authentication, and error handling.

## 🏗️ Architecture

```
Frontend Applications
        ↓
    API Gateway (apps/api)
        ↓
┌─────────────────────────────────┐
│  Centralized API Management     │
│  - Standardized Responses       │
│  - Authentication & Permissions │
│  - Rate Limiting & CORS         │
│  - Request/Response Logging     │
│  - Error Handling               │
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│  Individual App ViewSets        │
│  - accounts, courses, classes   │
│  - payments, ai, notifications  │
│  - admin_tools                  │
└─────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Base URL
```
Development: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

### 2. Authentication
```javascript
// Login
POST /api/v1/accounts/auth/login/
{
  "email": "user@example.com",
  "password": "password"
}

// Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Required Headers
```javascript
{
  "Authorization": "Bearer <access_token>",
  "X-Tenant": "<organization_subdomain>",
  "Content-Type": "application/json"
}
```

## 📊 Dashboard Endpoints

### Student Dashboard
```javascript
GET /api/v1/dashboard/student/
```
Returns:
- Enrollment statistics
- Courses in progress
- Recent enrollments
- Upcoming live classes
- Course recommendations
- Recent notifications

### Teacher Dashboard
```javascript
GET /api/v1/dashboard/teacher/
```
Returns:
- Course performance metrics
- Student analytics
- Revenue statistics
- Recent enrollments
- Upcoming classes
- Enrollment trends

### Admin Dashboard
```javascript
GET /api/v1/dashboard/admin/
```
Returns:
- Organizational metrics
- User statistics
- Course statistics
- Revenue analytics
- System health
- Recent activity

## 📚 Core Endpoints

### Courses
```javascript
// List courses
GET /api/v1/courses/

// Get course details
GET /api/v1/courses/{id}/

// Marketplace with filters
GET /api/v1/courses/marketplace_enhanced/?category=technology&difficulty=beginner

// Course recommendations
GET /api/v1/courses/recommendations/?limit=10

// Enroll in course
POST /api/v1/courses/{id}/enroll/

// Course analytics
GET /api/v1/courses/{id}/analytics/

// Dashboard statistics
GET /api/v1/courses/dashboard_stats/
```

### Enrollments
```javascript
// List enrollments
GET /api/v1/enrollments/

// Update progress
PATCH /api/v1/enrollments/{id}/update_progress/
{
  "progress_percentage": 75
}

// Student dashboard data
GET /api/v1/enrollments/dashboard/
```

### Live Classes
```javascript
// List live classes
GET /api/v1/live-classes/

// Upcoming classes
GET /api/v1/live-classes/upcoming/

// Join information
GET /api/v1/live-classes/{id}/join_info/

// Start class (instructors only)
POST /api/v1/live-classes/{id}/start_class/
```

### Notifications
```javascript
// List notifications
GET /api/v1/notifications/

// Mark as read
POST /api/v1/notifications/{id}/mark_read/
```

## 🤖 AI Features
```javascript
// AI conversations
GET /api/v1/ai-conversations/
POST /api/v1/ai-conversations/

// Content summaries
GET /api/v1/ai-content-summaries/

// AI-generated quizzes
GET /api/v1/ai-quizzes/

// Usage statistics
GET /api/v1/ai-usage/
```

## 💳 Payments
```javascript
// Payments
GET /api/v1/payments/
POST /api/v1/payments/

// Subscriptions
GET /api/v1/subscriptions/

// Invoices
GET /api/v1/invoices/
```

## 📋 Response Format

All API responses follow this standardized format:

### Success Response
```javascript
{
  "success": true,
  "data": {
    // Response data here
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z",
  "meta": {
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "page_size": 20,
      "total_count": 100
    }
  }
}
```

### Error Response
```javascript
{
  "success": false,
  "message": "Error description",
  "errors": {
    "field_name": ["Field error message"]
  },
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔍 Filtering & Search

### Query Parameters
```javascript
// Pagination
?page=1&page_size=20

// Search
?search=python

// Filtering
?category=technology&difficulty=beginner&status=active

// Ordering
?ordering=-created_at  // Descending
?ordering=title        // Ascending
```

### Course Marketplace Filters
```javascript
GET /api/v1/courses/marketplace_enhanced/?
  category=technology&
  difficulty=beginner&
  min_price=0&
  max_price=100&
  min_rating=4.0&
  sort_by=rating&
  sort_order=desc
```

## 🛠️ Frontend Integration

### JavaScript/TypeScript Client
See `frontend_client_example.js` for a complete implementation.

### React Example
```javascript
import EduRiseAPIClient from './api-client';

function CourseList() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const apiClient = new EduRiseAPIClient(
    'http://localhost:8000/api',
    'your-tenant'
  );

  useEffect(() => {
    async function fetchCourses() {
      const response = await apiClient.getCourses();
      if (response.success) {
        setCourses(response.data.data);
      }
      setLoading(false);
    }
    
    fetchCourses();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {courses.map(course => (
        <div key={course.id}>
          <h3>{course.title}</h3>
          <p>{course.description}</p>
        </div>
      ))}
    </div>
  );
}
```

### Vue Example
```javascript
<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <div v-for="course in courses" :key="course.id">
        <h3>{{ course.title }}</h3>
        <p>{{ course.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import EduRiseAPIClient from './api-client';

const courses = ref([]);
const loading = ref(true);

const apiClient = new EduRiseAPIClient(
  'http://localhost:8000/api',
  'your-tenant'
);

onMounted(async () => {
  const response = await apiClient.getCourses();
  if (response.success) {
    courses.value = response.data.data;
  }
  loading.value = false;
});
</script>
```

## 🔐 Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request data validation failed |
| `PERMISSION_DENIED` | User lacks required permissions |
| `NOT_FOUND` | Requested resource not found |
| `UNAUTHORIZED` | Authentication required |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVER_ERROR` | Internal server error |

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/api/health/
```

### API Documentation
```bash
curl http://localhost:8000/api/docs/
```

### Management Commands
```bash
# Test API endpoints
python manage.py audit_api_endpoints --test-endpoints --check-serializers

# Test response format
python manage.py test_api_responses

# Test frontend connectivity
python manage.py test_frontend_connectivity --create-test-data
```

## 🚀 Deployment

### Environment Variables
```bash
# API Configuration
API_VERSION=1.0.0
API_RATE_LIMIT_PER_MINUTE=100

# CORS Configuration
API_ALLOWED_ORIGINS=https://your-frontend.com,https://admin.your-frontend.com

# Logging
API_LOG_REQUESTS=true
API_LOG_RESPONSES=true
```

### Production Settings
```python
# In production.py
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.com",
    "https://admin.your-frontend.com",
]

API_RATE_LIMIT_PER_MINUTE = 60  # Lower for production
```

## 📈 Monitoring

### API Logs
```bash
# View API logs
tail -f logs/api.log

# Filter by endpoint
grep "POST /api/v1/courses" logs/api.log
```

### Health Monitoring
```bash
# Check API health
curl -f http://localhost:8000/api/health/ || echo "API is down"
```

## 🤝 Contributing

1. All new endpoints should use `StandardViewSetMixin`
2. Follow the standardized response format
3. Add proper error handling
4. Include comprehensive tests
5. Update this documentation

## 📞 Support

For API support and questions:
- Check the API documentation: `/api/docs/`
- Run health check: `/api/health/`
- Review logs in `logs/api.log`
- Test connectivity with management commands