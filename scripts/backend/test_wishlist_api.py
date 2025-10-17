#!/usr/bin/env python
"""
Simple test script to verify wishlist API functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Organization
from apps.courses.models import Course, Wishlist
from apps.courses.serializers import WishlistSerializer
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

User = get_user_model()

def test_wishlist_functionality():
    """Test basic wishlist functionality"""
    print("Testing Wishlist API functionality...")
    
    # Create test tenant
    tenant, created = Organization.objects.get_or_create(
        subdomain='test-tenant',
        defaults={
            'name': 'Test Organization',
            'subscription_plan': 'basic'
        }
    )
    print(f"✓ Tenant created/found: {tenant.name}")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'username': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    print(f"✓ User created/found: {user.email}")
    
    # Create test course
    instructor, created = User.objects.get_or_create(
        email='instructor@example.com',
        defaults={
            'username': 'instructor@example.com',
            'first_name': 'Test',
            'last_name': 'Instructor',
            'is_teacher': True,
            'is_active': True
        }
    )
    
    course, created = Course.objects.get_or_create(
        title='Test Course for Wishlist',
        tenant=tenant,
        defaults={
            'description': 'A test course for wishlist functionality',
            'instructor': instructor,
            'category': 'technology',
            'price': 99.99,
            'is_public': True,
            'difficulty_level': 'beginner'
        }
    )
    print(f"✓ Course created/found: {course.title}")
    
    # Test creating wishlist item
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=user,
        course=course,
        tenant=tenant,
        defaults={
            'priority': 2,
            'notes': 'Test wishlist item',
            'notify_price_change': True
        }
    )
    print(f"✓ Wishlist item created/found: {wishlist_item}")
    
    # Test serializer
    factory = APIRequestFactory()
    request = factory.get('/api/v1/wishlist/')
    request.user = user
    request.tenant = tenant
    
    serializer = WishlistSerializer(wishlist_item, context={'request': request})
    data = serializer.data
    
    print(f"✓ Serializer data: {data['course_title']}")
    print(f"✓ Course price: ${data['course_price']}")
    print(f"✓ Priority: {data['priority']}")
    print(f"✓ Is enrolled: {data['is_enrolled']}")
    
    # Test model methods
    print(f"✓ Course available: {wishlist_item.is_course_available}")
    print(f"✓ User enrolled: {wishlist_item.is_enrolled()}")
    
    # Clean up
    print("\nCleaning up test data...")
    wishlist_item.delete()
    print("✓ Wishlist item deleted")
    
    print("\n🎉 All wishlist tests passed!")
    
    return True

if __name__ == '__main__':
    try:
        test_wishlist_functionality()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)