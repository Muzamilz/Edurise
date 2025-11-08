# ✅ IMPLEMENTATION TODO LIST
## Based on Requirements Gap Analysis

**Priority**: 🔴 Critical | 🟡 High | 🟢 Medium | ⚪ Low  
**Effort**: S (< 4h) | M (1-2 days) | L (3-5 days) | XL (> 1 week)

---

## 🔴 CRITICAL (DO NOW - Week 1)

### 1. Fix Payment-Enrollment Auto-Creation
**Priority**: 🔴 CRITICAL  
**Effort**: S (2 hours)  
**Requirement**: #3 - Public Marketplace  
**Impact**: Students paying for courses but not getting access

**File**: `backend/apps/payments/services.py`  
**Line**: 733 (in `confirm_payment` method)

```python
# ADD THIS CODE:
if payment.payment_type == 'course' and payment.course:
    from apps.courses.models import Enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        student=payment.user,
        course=payment.course,
        tenant=payment.tenant,
        defaults={
            'status': 'active',
            'progress_percentage': 0
        }
    )
    
    if created:
        # Send enrollment confirmation email
        from apps.notifications.services import NotificationService
        NotificationService.send_enrollment_confirmation(enrollment)
        
    logger.info(f"Auto-enrolled {payment.user.email} in {payment.course.title}")
```

**Testing**:
```bash
cd backend
python manage.py test apps.payments.tests.test_payment_enrollment
```

---

### 2. Add Stripe Webhook Handler
**Priority**: 🔴 CRITICAL  
**Effort**: M (4 hours)  
**Requirement**: #7 - Payment System  
**Impact**: Unreliable payment confirmations

**Create**: `backend/apps/payments/webhooks.py`

```python
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import Payment
from .services import PaymentService
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid Stripe webhook payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe webhook signature")
        return HttpResponse(status=400)
    
    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent.id
            )
            PaymentService.confirm_payment(payment.id)
            logger.info(f"Payment {payment.id} confirmed via webhook")
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for intent {payment_intent.id}")
    
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent.id
            )
            payment.mark_failed('Payment failed via webhook')
            logger.warning(f"Payment {payment.id} failed via webhook")
        except Payment.DoesNotExist:
            pass
    
    return HttpResponse(status=200)
```

**Add to URLs**: `backend/apps/payments/urls.py`
```python
from .webhooks import stripe_webhook

urlpatterns = [
    # ... existing patterns
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
]
```

**Add to Environment**: `.env.development` and `.env.production`
```
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
```

**Register in Stripe Dashboard**:
1. Go to: https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://yourdomain.com/api/v1/payments/webhooks/stripe/`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy webhook secret to environment

---

### 3. Security Configuration Hardening
**Priority**: 🔴 CRITICAL  
**Effort**: S (1 hour)  
**Requirement**: #10 - Security  
**Impact**: Production security vulnerabilities

#### a) Remove Hardcoded SECRET_KEY
**File**: `backend/config/settings/base.py`  
**Line**: 20

```python
# CHANGE FROM:
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# CHANGE TO:
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY environment variable is required")
```

#### b) Disable CORS_ALLOW_ALL_ORIGINS
**File**: `backend/config/settings/development.py`  
**Line**: 27

```python
# DELETE THIS LINE:
CORS_ALLOW_ALL_ORIGINS = True

# Keep only specific origins:
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:8000',
]
```

#### c) Add Environment Variable Validation
**Create**: `backend/apps/common/env_validator.py`

```python
import os
from django.core.exceptions import ImproperlyConfigured

REQUIRED_ENV_VARS = {
    'development': [
        'SECRET_KEY',
        'DATABASE_URL',
    ],
    'production': [
        'SECRET_KEY',
        'DATABASE_URL',
        'STRIPE_SECRET_KEY',
        'STRIPE_PUBLISHABLE_KEY',
        'STRIPE_WEBHOOK_SECRET',
        'PAYPAL_CLIENT_ID',
        'PAYPAL_CLIENT_SECRET',
        'SENTRY_DSN',
        'REDIS_URL',
    ],
}

def validate_environment():
    """Validate required environment variables"""
    env = os.environ.get('ENVIRONMENT', 'development')
    required = REQUIRED_ENV_VARS.get(env, REQUIRED_ENV_VARS['development'])
    
    missing = [var for var in required if not os.environ.get(var)]
    
    if missing:
        raise ImproperlyConfigured(
            f"Missing required environment variables for {env}: {', '.join(missing)}"
        )
```

**Call in**: `backend/config/settings/base.py` (after imports)
```python
from apps.common.env_validator import validate_environment
validate_environment()
```

---

### 4. Add Database Indexes
**Priority**: 🔴 CRITICAL  
**Effort**: S (1 hour)  
**Requirement**: Performance (not explicit requirement but critical)  
**Impact**: Slow queries at scale

**Create migration**:
```bash
cd backend
python manage.py makemigrations --empty courses -n add_performance_indexes
```

**Edit migration file**:
```python
operations = [
    migrations.AddIndex(
        model_name='enrollment',
        index=models.Index(
            fields=['student', 'status'],
            name='enroll_student_status_idx'
        ),
    ),
    migrations.AddIndex(
        model_name='enrollment',
        index=models.Index(
            fields=['course', 'status'],
            name='enroll_course_status_idx'
        ),
    ),
    migrations.AddIndex(
        model_name='enrollment',
        index=models.Index(
            fields=['enrolled_at'],
            name='enroll_date_idx'
        ),
    ),
    migrations.AddIndex(
        model_name='course',
        index=models.Index(
            fields=['is_public', 'is_active'],
            name='course_public_active_idx'
        ),
    ),
]
```

**Run migration**:
```bash
python manage.py migrate
```

---

## 🟡 HIGH PRIORITY (Week 2-3)

### 5. Implement Internationalization (i18n)
**Priority**: 🟡 HIGH  
**Effort**: M (2 days)  
**Requirement**: #11 - Accessibility and Internationalization  
**Impact**: Limited to English-speaking markets

#### a) Install Dependencies
```bash
cd frontend
pnpm add vue-i18n@9
pnpm add -D @intlify/unplugin-vue-i18n
```

#### b) Create Locale Files
**Create**: `frontend/src/locales/en.json`
```json
{
  "nav": {
    "home": "Home",
    "courses": "Courses",
    "dashboard": "Dashboard",
    "logout": "Logout"
  },
  "course": {
    "enroll": "Enroll Now",
    "price": "Price",
    "instructor": "Instructor"
  }
}
```

**Create**: `frontend/src/locales/ar.json`
```json
{
  "nav": {
    "home": "الرئيسية",
    "courses": "الدورات",
    "dashboard": "لوحة التحكم",
    "logout": "تسجيل الخروج"
  },
  "course": {
    "enroll": "سجل الآن",
    "price": "السعر",
    "instructor": "المدرس"
  }
}
```

**Create**: `frontend/src/locales/so.json`
```json
{
  "nav": {
    "home": "Guriga",
    "courses": "Koorsada",
    "dashboard": "Dashboard-ka",
    "logout": "Ka bax"
  }
}
```

#### c) Configure i18n
**Create**: `frontend/src/i18n.ts`
```typescript
import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import ar from './locales/ar.json'
import so from './locales/so.json'

export const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'en',
  fallbackLocale: 'en',
  messages: { en, ar, so }
})
```

**Update**: `frontend/src/main.ts`
```typescript
import { i18n } from './i18n'

app.use(i18n)
```

#### d) Add RTL Support
**Update**: `frontend/index.html`
```html
<html :lang="locale" :dir="locale === 'ar' ? 'rtl' : 'ltr'">
```

**Add to**: `frontend/tailwind.config.js`
```javascript
module.exports = {
  plugins: [
    require('@tailwindcss/dir')
  ]
}
```

---

### 6. Add PWA Support
**Priority**: 🟡 HIGH  
**Effort**: S (4 hours)  
**Requirement**: #11 - Accessibility  
**Impact**: No offline support

#### a) Install Plugin
```bash
cd frontend
pnpm add -D vite-plugin-pwa
```

#### b) Configure Vite
**Update**: `frontend/vite.config.ts`
```typescript
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Edurise LMS',
        short_name: 'Edurise',
        description: 'Modern Learning Management System',
        theme_color: '#3b82f6',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ]
})
```

---

### 7. Implement Frontend Animations
**Priority**: 🟡 HIGH  
**Effort**: L (3-5 days)  
**Requirement**: #12 - Frontend UX and Animations  
**Impact**: Less engaging user experience

#### a) Create Animation Composable
**Create**: `frontend/src/composables/useAnimations.ts`
```typescript
import anime from 'animejs'

export function useAnimations() {
  const fadeIn = (target: string | HTMLElement) => {
    anime({
      targets: target,
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 600,
      easing: 'easeOutQuad'
    })
  }
  
  const slideIn = (target: string | HTMLElement, direction: 'left' | 'right' = 'left') => {
    anime({
      targets: target,
      translateX: direction === 'left' ? [-100, 0] : [100, 0],
      opacity: [0, 1],
      duration: 800,
      easing: 'easeOutCubic'
    })
  }
  
  const scaleIn = (target: string | HTMLElement) => {
    anime({
      targets: target,
      scale: [0.9, 1],
      opacity: [0, 1],
      duration: 500,
      easing: 'easeOutElastic(1, .8)'
    })
  }
  
  return { fadeIn, slideIn, scaleIn }
}
```

#### b) Add Page Transitions
**Update**: `frontend/src/App.vue`
```vue
<template>
  <RouterView v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
```

#### c) Add Loading Animations
**Create**: `frontend/src/components/LoadingSpinner.vue`
```vue
<template>
  <div class="loading-spinner" ref="spinner">
    <div class="spinner-ring"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import anime from 'animejs'

const spinner = ref<HTMLElement>()

onMounted(() => {
  anime({
    targets: spinner.value?.querySelector('.spinner-ring'),
    rotate: '360deg',
    duration: 1000,
    easing: 'linear',
    loop: true
  })
})
</script>

<style scoped>
.spinner-ring {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top-color: #3b82f6;
  border-radius: 50%;
}
</style>
```

---

## 🟢 MEDIUM PRIORITY (Month 2)

### 8. Add 3D Course Visualizations
**Priority**: 🟢 MEDIUM  
**Effort**: XL (1-2 weeks)  
**Requirement**: #12 - Frontend UX  
**Impact**: Enhanced visual experience

**Create**: `frontend/src/components/3d/CourseGlobe.vue`
```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import * as THREE from 'three'

const canvas = ref<HTMLCanvasElement>()

onMounted(() => {
  if (!canvas.value) return
  
  // Setup scene
  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
  const renderer = new THREE.WebGLRenderer({ canvas: canvas.value, alpha: true })
  
  renderer.setSize(400, 400)
  
  // Create globe
  const geometry = new THREE.SphereGeometry(1, 32, 32)
  const material = new THREE.MeshBasicMaterial({
    color: 0x3b82f6,
    wireframe: true
  })
  const sphere = new THREE.Mesh(geometry, material)
  scene.add(sphere)
  
  camera.position.z = 3
  
  // Animation loop
  function animate() {
    requestAnimationFrame(animate)
    sphere.rotation.x += 0.01
    sphere.rotation.y += 0.01
    renderer.render(scene, camera)
  }
  
  animate()
})
</script>

<template>
  <canvas ref="canvas"></canvas>
</template>
```

---

### 9. Bulk User Import via CSV
**Priority**: 🟢 MEDIUM  
**Effort**: S (4 hours)  
**Requirement**: #4 - Institutional Portals  
**Impact**: Manual user creation is tedious

**Create**: `backend/apps/accounts/views.py` (add action)
```python
@action(detail=False, methods=['post'])
def bulk_import(self, request):
    """Bulk import users from CSV file"""
    if not request.FILES.get('file'):
        return StandardAPIResponse.validation_error(
            errors={'file': ['CSV file is required']},
            message="Please upload a CSV file"
        )
    
    import csv
    import io
    
    file = request.FILES['file']
    decoded_file = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded_file))
    
    results = {
        'created': 0,
        'updated': 0,
        'errors': []
    }
    
    for row in reader:
        try:
            email = row.get('email')
            if not email:
                results['errors'].append({'row': row, 'error': 'Email required'})
                continue
            
            user, created = User.objects.update_or_create(
                email=email,
                defaults={
                    'first_name': row.get('first_name', ''),
                    'last_name': row.get('last_name', ''),
                    'role': row.get('role', 'student'),
                }
            )
            
            if created:
                results['created'] += 1
            else:
                results['updated'] += 1
                
        except Exception as e:
            results['errors'].append({'row': row, 'error': str(e)})
    
    return StandardAPIResponse.success(
        data=results,
        message=f"Imported {results['created']} users, updated {results['updated']}"
    )
```

---

### 10. WCAG 2.1 AA Accessibility Audit
**Priority**: 🟢 MEDIUM  
**Effort**: M (2 days)  
**Requirement**: #11 - Accessibility  
**Impact**: Inaccessible to users with disabilities

**Tools to use**:
```bash
# Install accessibility testing tools
pnpm add -D @axe-core/vue
pnpm add -D eslint-plugin-vuejs-accessibility
```

**Checklist**:
- [ ] All images have alt text
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Color contrast ratios meet AA standards
- [ ] Keyboard navigation works for all interactions
- [ ] Form labels properly associated
- [ ] Focus indicators visible
- [ ] ARIA labels where needed
- [ ] Skip to main content link

---

## ⚪ LOW PRIORITY (Backlog)

### 11. Reduced Motion Support
**Priority**: ⚪ LOW  
**Effort**: S (1 day)

```typescript
// frontend/src/composables/useReducedMotion.ts
export function useReducedMotion() {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  
  return {
    prefersReducedMotion,
    duration: prefersReducedMotion ? 0 : 300
  }
}
```

---

## SUMMARY CHECKLIST

### Critical (Week 1):
- [ ] Fix payment-enrollment auto-creation
- [ ] Add Stripe webhook handler
- [ ] Remove hardcoded SECRET_KEY
- [ ] Disable CORS_ALLOW_ALL_ORIGINS
- [ ] Add environment validation
- [ ] Add database indexes

### High Priority (Weeks 2-3):
- [ ] Implement vue-i18n
- [ ] Create locale files (en, ar, so)
- [ ] Add RTL support for Arabic
- [ ] Configure PWA manifest
- [ ] Implement page animations
- [ ] Add loading animations

### Medium Priority (Month 2):
- [ ] Create 3D course visualizations
- [ ] Bulk user CSV import
- [ ] WCAG 2.1 AA audit
- [ ] Keyboard navigation enhancements

### Low Priority (Backlog):
- [ ] Reduced motion support
- [ ] Advanced 3D interactions
- [ ] Offline sync capabilities

---

**Estimated Total Effort**: 3-4 weeks for all critical + high priority items
