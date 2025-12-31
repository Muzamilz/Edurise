# Node.js Backend Migration Design Document

## Overview

This document outlines the technical design for migrating the existing Django-based EduRise LMS backend to a modern, well-organized Node.js architecture using TypeScript. The migration will preserve all existing functionality while improving code organization, maintainability, and developer experience.

The new architecture will be built using Express.js with TypeScript, implementing clean architecture principles with clear separation of concerns. All existing APIs will maintain backward compatibility to ensure seamless frontend integration.

## Architecture

### High-Level Architecture

The new Node.js backend will follow a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│  (Express.js + Middleware + Route Handlers)                │
├─────────────────────────────────────────────────────────────┤
│                   Application Layer                         │
│     (Services + Use Cases + Business Logic)                 │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                             │
│        (Entities + Domain Services + Interfaces)           │
├─────────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                        │
│  (Database + External APIs + File Storage + WebSockets)    │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Runtime**: Node.js 18+ with TypeScript
- **Web Framework**: Express.js with TypeScript
- **Database ORM**: Prisma (for PostgreSQL compatibility)
- **Authentication**: JWT with passport.js
- **WebSockets**: Socket.io for real-time features
- **File Upload**: Multer with cloud storage integration
- **Validation**: Joi or Zod for request validation
- **Testing**: Jest + Supertest for API testing
- **Documentation**: Swagger/OpenAPI 3.0
- **Process Management**: PM2 for production
- **Monitoring**: Winston for logging

### Directory Structure

```
src/
├── api/                    # API layer (routes, controllers, middleware)
│   ├── controllers/        # Request handlers
│   ├── middleware/         # Custom middleware
│   ├── routes/            # Route definitions
│   └── validators/        # Request validation schemas
├── application/           # Application layer (services, use cases)
│   ├── services/          # Business logic services
│   ├── use-cases/         # Application use cases
│   └── interfaces/        # Service interfaces
├── domain/               # Domain layer (entities, domain services)
│   ├── entities/         # Domain entities
│   ├── repositories/     # Repository interfaces
│   └── services/         # Domain services
├── infrastructure/       # Infrastructure layer
│   ├── database/         # Database configuration and repositories
│   ├── external/         # External service integrations
│   ├── storage/          # File storage implementations
│   └── websockets/       # WebSocket implementations
├── shared/               # Shared utilities and types
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   └── constants/        # Application constants
└── config/               # Configuration files
    ├── database.ts       # Database configuration
    ├── auth.ts           # Authentication configuration
    └── app.ts            # Application configuration
```

## Components and Interfaces

### Core Services

#### 1. Authentication Service
```typescript
interface IAuthenticationService {
  login(credentials: LoginCredentials): Promise<AuthResult>;
  register(userData: RegisterData): Promise<User>;
  refreshToken(token: string): Promise<AuthResult>;
  validateToken(token: string): Promise<User>;
  logout(userId: string): Promise<void>;
}
```

#### 2. User Management Service
```typescript
interface IUserService {
  createUser(userData: CreateUserData): Promise<User>;
  getUserById(id: string): Promise<User>;
  updateUser(id: string, updates: UpdateUserData): Promise<User>;
  getUserProfiles(userId: string): Promise<UserProfile[]>;
  assignRole(userId: string, tenantId: string, role: UserRole): Promise<void>;
}
```

#### 3. Course Management Service
```typescript
interface ICourseService {
  createCourse(courseData: CreateCourseData): Promise<Course>;
  getCourses(filters: CourseFilters): Promise<PaginatedResult<Course>>;
  enrollStudent(courseId: string, studentId: string): Promise<Enrollment>;
  updateProgress(enrollmentId: string, progress: number): Promise<void>;
  getCourseAnalytics(courseId: string): Promise<CourseAnalytics>;
}
```

#### 4. Payment Service
```typescript
interface IPaymentService {
  processPayment(paymentData: PaymentData): Promise<Payment>;
  createSubscription(subscriptionData: SubscriptionData): Promise<Subscription>;
  handleWebhook(provider: PaymentProvider, payload: any): Promise<void>;
  generateInvoice(paymentId: string): Promise<Invoice>;
  refundPayment(paymentId: string, amount?: number): Promise<Refund>;
}
```

#### 5. Notification Service
```typescript
interface INotificationService {
  sendNotification(notification: NotificationData): Promise<void>;
  sendEmail(emailData: EmailData): Promise<void>;
  broadcastToTenant(tenantId: string, message: BroadcastMessage): Promise<void>;
  markAsRead(notificationId: string, userId: string): Promise<void>;
  getUnreadCount(userId: string): Promise<number>;
}
```

### Repository Interfaces

#### 1. User Repository
```typescript
interface IUserRepository {
  create(user: CreateUserData): Promise<User>;
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  update(id: string, updates: Partial<User>): Promise<User>;
  delete(id: string): Promise<void>;
  findByTenant(tenantId: string): Promise<User[]>;
}
```

#### 2. Course Repository
```typescript
interface ICourseRepository {
  create(course: CreateCourseData): Promise<Course>;
  findById(id: string): Promise<Course | null>;
  findByInstructor(instructorId: string): Promise<Course[]>;
  findByCategory(categoryId: string): Promise<Course[]>;
  update(id: string, updates: Partial<Course>): Promise<Course>;
  delete(id: string): Promise<void>;
  search(query: SearchQuery): Promise<PaginatedResult<Course>>;
}
```

## Data Models

### Core Entities

#### User Entity
```typescript
interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  profiles: UserProfile[];
}

interface UserProfile {
  id: string;
  userId: string;
  tenantId: string;
  role: UserRole;
  avatar?: string;
  bio?: string;
  phoneNumber?: string;
  dateOfBirth?: Date;
  timezone: string;
  language: string;
  isApprovedTeacher: boolean;
  notificationPreferences: NotificationPreferences;
  isOnline: boolean;
  lastSeen?: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

#### Course Entity
```typescript
interface Course {
  id: string;
  title: string;
  description: string;
  instructorId: string;
  categoryId: string;
  tenantId: string;
  tags: string[];
  thumbnailUrl?: string;
  price?: number;
  isPublic: boolean;
  maxStudents?: number;
  durationWeeks: number;
  difficultyLevel: DifficultyLevel;
  createdAt: Date;
  updatedAt: Date;
  modules: CourseModule[];
  enrollments: Enrollment[];
  reviews: CourseReview[];
}
```

#### Payment Entity
```typescript
interface Payment {
  id: string;
  userId: string;
  tenantId: string;
  paymentType: PaymentType;
  courseId?: string;
  subscriptionId?: string;
  amount: number;
  currency: string;
  paymentMethod: PaymentMethod;
  status: PaymentStatus;
  stripePaymentIntentId?: string;
  paypalOrderId?: string;
  description?: string;
  metadata: Record<string, any>;
  createdAt: Date;
  completedAt?: Date;
  failedAt?: Date;
}
```

### Database Schema Migration

The migration will use Prisma to define the database schema, maintaining compatibility with the existing PostgreSQL database:

```prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  firstName String   @map("first_name")
  lastName  String   @map("last_name")
  isActive  Boolean  @default(true) @map("is_active")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  
  profiles    UserProfile[]
  enrollments Enrollment[]
  payments    Payment[]
  
  @@map("accounts_user")
}

model Organization {
  id             String  @id @default(uuid())
  name           String
  subdomain      String  @unique
  logo           String?
  primaryColor   String  @default("#3B82F6") @map("primary_color")
  secondaryColor String  @default("#1E40AF") @map("secondary_color")
  isActive       Boolean @default(true) @map("is_active")
  createdAt      DateTime @default(now()) @map("created_at")
  updatedAt      DateTime @updatedAt @map("updated_at")
  
  userProfiles UserProfile[]
  courses      Course[]
  subscription Subscription?
  
  @@map("organizations")
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, the following correctness properties must be maintained during and after the migration:

### Property 1: API Response Consistency
*For any* valid API request, the Node.js system should return responses that are structurally and semantically identical to the Django system responses
**Validates: Requirements 1.1, 1.2**

### Property 2: Database Connection Integrity
*For any* database operation, the Node.js system should maintain all existing data relationships and constraints without data loss
**Validates: Requirements 1.3, 11.1, 11.2, 11.3, 11.4, 11.5**

### Property 3: Error Response Format Consistency
*For any* error condition, the Node.js system should return error responses in the same format and structure as the Django system
**Validates: Requirements 1.5**

### Property 4: Authentication Token Compatibility
*For any* valid JWT token, the Node.js authentication service should decode and validate tokens identically to the Django system
**Validates: Requirements 3.1, 3.2**

### Property 5: Authorization Rule Enforcement
*For any* user and resource combination, the Node.js system should make identical access control decisions as the Django system
**Validates: Requirements 3.3, 3.5**

### Property 6: Password Reset Flow Consistency
*For any* password reset request, the Node.js system should follow the identical workflow and use the same email templates as the Django system
**Validates: Requirements 3.4**

### Property 7: Course Data Structure Preservation
*For any* course-related operation, the Node.js system should maintain identical data structures, relationships, and business logic as the Django system
**Validates: Requirements 4.1, 4.2, 4.4**

### Property 8: File Upload and Processing Consistency
*For any* file upload operation, the Node.js system should handle storage, validation, and processing identically to the Django system
**Validates: Requirements 4.3, 7.1, 7.3**

### Property 9: Certificate Generation Consistency
*For any* certificate generation request, the Node.js system should produce identical certificate formats, QR codes, and PDFs as the Django system
**Validates: Requirements 4.5, 7.4**

### Property 10: Payment Processing Consistency
*For any* payment operation, the Node.js system should integrate with payment providers and process transactions identically to the Django system
**Validates: Requirements 5.1, 5.2, 5.4, 5.5**

### Property 11: Invoice Generation Consistency
*For any* invoice generation request, the Node.js system should produce invoices with identical format, content, and calculations as the Django system
**Validates: Requirements 5.3**

### Property 12: Notification Delivery Consistency
*For any* notification trigger, the Node.js system should deliver notifications via the same channels with identical content as the Django system
**Validates: Requirements 6.1, 6.4, 6.5**

### Property 13: WebSocket Functionality Preservation
*For any* WebSocket connection and real-time operation, the Node.js system should maintain identical behavior, authentication, and event handling as the Django system
**Validates: Requirements 6.2, 6.3, 12.1, 12.2, 12.3, 12.4, 12.5**

### Property 14: File Access Control Consistency
*For any* file access request, the Node.js system should enforce identical access control rules and serve files with the same headers as the Django system
**Validates: Requirements 7.2, 7.5**

### Property 15: AI Service Integration Consistency
*For any* AI service request, the Node.js system should integrate with AI providers and process requests identically to the Django system
**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

### Property 16: Logging Format Consistency
*For any* system operation, the Node.js system should generate logs with identical structure, content, and detail level as the Django system
**Validates: Requirements 9.1, 9.2, 9.4**

### Property 17: Third-Party Integration Consistency
*For any* third-party service integration (Zoom, Stripe, PayPal, Google AI, Email), the Node.js system should maintain identical API usage, webhook handling, and response processing as the Django system
**Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**

### Property 18: RESTful API Convention Compliance
*For any* API endpoint, the Node.js system should follow RESTful conventions and provide consistent error handling patterns
**Validates: Requirements 14.4**

### Property 19: Middleware Functionality Preservation
*For any* request processing, the Node.js system should provide identical authentication, authorization, logging, and security middleware functionality as the Django system
**Validates: Requirements 14.5**

## Error Handling

### Error Response Format
All errors will follow a consistent JSON structure:

```typescript
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    requestId: string;
  };
}
```

### Error Categories
1. **Validation Errors** (400): Input validation failures
2. **Authentication Errors** (401): Invalid or missing authentication
3. **Authorization Errors** (403): Insufficient permissions
4. **Not Found Errors** (404): Resource not found
5. **Conflict Errors** (409): Business rule violations
6. **Server Errors** (500): Internal system errors

### Error Handling Strategy
- Global error middleware to catch and format all errors
- Structured logging for all errors with context
- Error tracking and monitoring integration
- Graceful degradation for non-critical failures
- Circuit breaker pattern for external service failures

## Testing Strategy

### Dual Testing Approach

The migration will implement both unit testing and property-based testing to ensure comprehensive coverage and correctness validation.

#### Unit Testing
- **Framework**: Jest with TypeScript support
- **Coverage**: All service methods, controllers, and utilities
- **Mocking**: Use dependency injection for easy mocking
- **Database Testing**: In-memory database for isolated tests
- **API Testing**: Supertest for HTTP endpoint testing

Unit tests will cover:
- Individual function behavior
- Edge cases and error conditions
- Integration points between components
- Specific business logic scenarios

#### Property-Based Testing
- **Framework**: fast-check for JavaScript/TypeScript
- **Configuration**: Minimum 100 iterations per property test
- **Tagging**: Each property test tagged with format: `**Feature: nodejs-backend-migration, Property {number}: {property_text}**`
- **Scope**: Universal properties that should hold across all inputs

Property-based tests will verify:
- API response consistency between Django and Node.js systems
- Data integrity during migration and operations
- Authentication and authorization correctness
- Business rule enforcement across all scenarios
- Error handling consistency

#### Integration Testing
- **Database Integration**: Real PostgreSQL database testing
- **External Services**: Mock external APIs (Stripe, Zoom, etc.)
- **WebSocket Testing**: Real-time feature validation
- **End-to-End Workflows**: Complete user journey testing

#### Migration Testing
- **Data Migration Validation**: Compare database state before/after
- **API Compatibility Testing**: Automated comparison of API responses
- **Performance Benchmarking**: Response time comparison
- **Load Testing**: Concurrent user simulation

### Test Environment Setup
- **Development**: Local PostgreSQL with test data
- **CI/CD**: Automated test execution on pull requests
- **Staging**: Production-like environment for integration testing
- **Performance**: Dedicated environment for load testing

### Quality Gates
- **Code Coverage**: Minimum 80% line coverage
- **Property Tests**: All properties must pass 100 iterations
- **Integration Tests**: All critical user workflows must pass
- **Performance**: Response times must be equal or better than Django
- **Security**: All security tests must pass

The testing strategy ensures that the migrated Node.js system maintains identical functionality while providing confidence in the migration process through comprehensive validation.

## Implementation Phases

### Phase 1: Foundation Setup
- Project structure and configuration
- Database schema migration with Prisma
- Core middleware and authentication
- Basic API framework

### Phase 2: Core Services Migration
- User management and authentication
- Course management
- Payment processing
- File handling

### Phase 3: Real-time Features
- WebSocket implementation
- Notification system
- Live class functionality
- Chat system

### Phase 4: Advanced Features
- AI service integration
- Analytics and reporting
- Admin tools
- Security features

### Phase 5: Testing and Optimization
- Comprehensive testing
- Performance optimization
- Documentation
- Deployment preparation

## Security Considerations

### Authentication & Authorization
- JWT token validation with same secret keys
- Role-based access control (RBAC)
- Multi-tenant data isolation
- Session management

### Data Protection
- Input validation and sanitization
- SQL injection prevention via ORM
- XSS protection
- CSRF protection

### API Security
- Rate limiting
- Request size limits
- CORS configuration
- Security headers

### Infrastructure Security
- Environment variable management
- Secrets management
- Logging security (no sensitive data)
- Error message sanitization

## Performance Considerations

### Database Optimization
- Connection pooling
- Query optimization
- Indexing strategy
- Caching layer (Redis)

### API Performance
- Response compression
- Pagination
- Lazy loading
- Caching strategies

### Real-time Performance
- WebSocket connection management
- Event broadcasting optimization
- Memory management
- Connection pooling

## Monitoring and Observability

### Logging
- Structured logging with Winston
- Request/response logging
- Error tracking
- Performance metrics

### Monitoring
- Health check endpoints
- Metrics collection
- Alerting system
- Performance monitoring

### Debugging
- Request tracing
- Error context
- Debug logging levels
- Development tools

## Deployment Strategy

### Containerization
- Docker containers for consistent deployment
- Multi-stage builds for optimization
- Environment-specific configurations
- Health checks

### Process Management
- PM2 for production process management
- Graceful shutdowns
- Auto-restart on failures
- Load balancing

### Database Migration
- Zero-downtime migration strategy
- Rollback procedures
- Data validation
- Performance monitoring during migration

This design provides a comprehensive blueprint for migrating the Django backend to Node.js while maintaining full compatibility and improving the overall architecture.