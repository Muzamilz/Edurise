# 📊 Comprehensive Test Data Setup for Edurise LMS Platform

This directory contains scripts to create comprehensive test data for the Edurise LMS platform, including users, organizations, courses, payments, AI data, and more.

## 🚀 Quick Setup

### Option 1: PowerShell (Windows - Recommended)
```powershell
.\setup_test_data.ps1
```

### Option 2: Python Script (Cross-platform)
```bash
python setup_test_data.py
```

### Option 3: Direct Django Command
```bash
cd backend
python manage.py setup_comprehensive_data --clean --organizations 5 --users-per-org 25 --courses-per-teacher 3
```

## 📋 What Gets Created

### 🏢 Organizations (5 total)
1. **Edurise Platform** (`main`) - Enterprise plan
2. **Tech University** (`techuni`) - Pro plan
3. **Business Academy** (`bizacademy`) - Pro plan
4. **Creative Institute** (`creative`) - Basic plan
5. **Medical College** (`medcollege`) - Enterprise plan

### 👥 Users (125+ total)
- **1 Super Admin** - Platform owner with global access
- **5 Organization Admins** - One per organization
- **30+ Teachers** - Mix of approved and pending approval
- **90+ Students** - Distributed across organizations

### 📚 Courses (45+ total)
- **Course Categories**: Technology, Business, Design, Marketing
- **Course Types**: Public marketplace courses and private organizational courses
- **Course Content**: Modules, live classes, materials
- **Pricing**: Mix of paid and free courses

### 💰 Financial Data
- **Subscriptions** - Organization subscription plans
- **Payments** - Course payments and subscription payments
- **Invoices** - Generated invoices with line items
- **Revenue Tracking** - Realistic financial data

### 🤖 AI Features
- **AI Conversations** - Student-AI tutor interactions
- **Content Summaries** - AI-generated course summaries
- **Usage Quotas** - AI usage tracking per user
- **Rate Limiting** - AI API rate limit data

### 📊 Learning Analytics
- **Enrollments** - Student course enrollments with progress
- **Live Classes** - Scheduled and completed live sessions
- **Attendance** - Class attendance records with engagement metrics
- **Reviews** - Course reviews and ratings

### 🔔 Notifications
- **System Notifications** - Various notification types
- **User Preferences** - Notification delivery settings

## 🔑 Test Accounts

### Super Admin
- **Email**: `admin@edurise.com`
- **Password**: `admin123456`
- **Access**: Global platform management

### Organization Admins
- **Tech University**: `admin@techuni.com` / `admin123456`
- **Business Academy**: `admin@bizacademy.com` / `admin123456`
- **Creative Institute**: `admin@creative.com` / `admin123456`
- **Medical College**: `admin@medcollege.com` / `admin123456`

### Teachers
- **Pattern**: `teacher[1-8]@[subdomain].com` / `teacher123456`
- **Examples**: 
  - `teacher1@techuni.com` / `teacher123456`
  - `teacher2@bizacademy.com` / `teacher123456`

### Students
- **Pattern**: `student[1-20]@[subdomain].com` / `student123456`
- **Examples**:
  - `student1@techuni.com` / `student123456`
  - `student5@bizacademy.com` / `student123456`

## 🌐 Multi-Tenant Access

### Main Platform
- **URL**: `http://localhost:3000`
- **Subdomain**: `main`
- **Type**: Marketplace platform

### Organization Portals
- **Tech University**: `http://techuni.localhost:3000`
- **Business Academy**: `http://bizacademy.localhost:3000`
- **Creative Institute**: `http://creative.localhost:3000`
- **Medical College**: `http://medcollege.localhost:3000`

## 🧪 Testing Scenarios

### 1. Super Admin Workflow
1. Login as `admin@edurise.com`
2. View platform-wide statistics
3. Manage all organizations
4. Approve pending teachers
5. Monitor system health

### 2. Organization Admin Workflow
1. Login as `admin@techuni.com`
2. Manage Tech University users
3. Oversee organization courses
4. Review financial reports
5. Configure organization settings

### 3. Teacher Workflow
1. Login as approved teacher (e.g., `teacher1@techuni.com`)
2. Create and manage courses
3. Schedule live classes
4. Track student progress
5. View earnings and analytics

### 4. Student Workflow
1. Login as student (e.g., `student1@techuni.com`)
2. Browse and enroll in courses
3. Attend live classes
4. Track learning progress
5. Use AI tutor features

### 5. Payment Testing
1. Enroll in paid courses
2. Process payments via different methods
3. View invoices and payment history
4. Test subscription management

### 6. AI Features Testing
1. Chat with AI tutor
2. Generate content summaries
3. Create AI quizzes
4. Monitor usage quotas

## 🔧 Customization Options

### Command Line Arguments
```bash
python manage.py setup_comprehensive_data \
  --clean \                    # Clean existing data
  --organizations 10 \         # Number of organizations
  --users-per-org 50 \        # Users per organization
  --courses-per-teacher 5     # Courses per teacher
```

### Environment Variables
Set these in your `.env` file for realistic data:
```env
# Payment settings
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# AI settings
GEMINI_API_KEY=your_gemini_key

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@gmail.com
```

## 📈 Data Statistics

After running the setup, you'll have approximately:
- **125+ Users** across all roles
- **45+ Courses** with full content
- **200+ Enrollments** with realistic progress
- **100+ Payments** and invoices
- **150+ AI Conversations** and summaries
- **300+ Notifications** across all users
- **50+ Live Classes** with attendance data

## 🔄 Resetting Data

To clean and recreate all data:
```bash
python manage.py setup_comprehensive_data --clean
```

To add more data without cleaning:
```bash
python manage.py setup_comprehensive_data --organizations 3 --users-per-org 15
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL/SQLite is running
   - Check database settings in `settings.py`

2. **Permission Errors**
   - Run migrations first: `python manage.py migrate`
   - Ensure proper file permissions

3. **Memory Issues**
   - Reduce the number of organizations or users
   - Run setup in smaller batches

### Getting Help

If you encounter issues:
1. Check the Django logs
2. Verify database connectivity
3. Ensure all dependencies are installed
4. Run migrations before setup

## 🎯 Next Steps

After setting up the data:
1. Start the Django backend: `python manage.py runserver`
2. Start the Vue.js frontend: `npm run dev`
3. Test different user roles and workflows
4. Explore the comprehensive dashboard system
5. Test multi-tenant functionality

## 📝 Notes

- All passwords are set to simple values for testing
- Email addresses follow predictable patterns
- Financial data uses test amounts
- AI data includes realistic conversation flows
- All timestamps are relative to current time

**⚠️ Important**: This is test data only. Do not use in production!