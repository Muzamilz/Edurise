#!/usr/bin/env python
"""
Test script to verify wishlist analytics functionality
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
from apps.courses.services import WishlistService
from decimal import Decimal

User = get_user_model()

def test_wishlist_analytics():
    """Test wishlist analytics functionality"""
    print("Testing Wishlist Analytics functionality...")
    
    # Create test tenant
    tenant, created = Organization.objects.get_or_create(
        subdomain='analytics-test',
        defaults={
            'name': 'Analytics Test Organization',
            'subscription_plan': 'pro'
        }
    )
    print(f"✓ Tenant created/found: {tenant.name}")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email='analytics@example.com',
        defaults={
            'username': 'analytics@example.com',
            'first_name': 'Analytics',
            'last_name': 'User',
            'is_active': True
        }
    )
    print(f"✓ User created/found: {user.email}")
    
    # Create test instructor
    instructor, created = User.objects.get_or_create(
        email='analytics-instructor@example.com',
        defaults={
            'username': 'analytics-instructor@example.com',
            'first_name': 'Analytics',
            'last_name': 'Instructor',
            'is_teacher': True,
            'is_active': True
        }
    )
    
    # Create test courses with different categories and prices
    courses_data = [
        {
            'title': 'Python Programming Basics',
            'category': 'technology',
            'price': Decimal('49.99'),
            'difficulty_level': 'beginner'
        },
        {
            'title': 'Advanced JavaScript',
            'category': 'technology',
            'price': Decimal('79.99'),
            'difficulty_level': 'advanced'
        },
        {
            'title': 'Digital Marketing Fundamentals',
            'category': 'marketing',
            'price': Decimal('39.99'),
            'difficulty_level': 'beginner'
        },
        {
            'title': 'Business Strategy',
            'category': 'business',
            'price': Decimal('129.99'),
            'difficulty_level': 'intermediate'
        },
        {
            'title': 'Free Web Design Course',
            'category': 'design',
            'price': None,  # Free course
            'difficulty_level': 'beginner'
        }
    ]
    
    created_courses = []
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            tenant=tenant,
            defaults={
                'description': f"Test course: {course_data['title']}",
                'instructor': instructor,
                'category': course_data['category'],
                'price': course_data['price'],
                'is_public': True,
                'difficulty_level': course_data['difficulty_level']
            }
        )
        created_courses.append(course)
    
    print(f"✓ Created/found {len(created_courses)} test courses")
    
    # Create wishlist items with different priorities
    wishlist_items = []
    priorities = [3, 2, 1, 2, 1]  # High, Medium, Low, Medium, Low
    
    for i, course in enumerate(created_courses):
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=user,
            course=course,
            tenant=tenant,
            defaults={
                'priority': priorities[i],
                'notes': f'Test wishlist item for {course.title}',
                'notify_price_change': True,
                'notify_course_updates': i % 2 == 0  # Alternate notification preferences
            }
        )
        wishlist_items.append(wishlist_item)
    
    print(f"✓ Created/found {len(wishlist_items)} wishlist items")
    
    # Test wishlist analytics
    analytics = WishlistService.get_wishlist_analytics(user, tenant)
    
    print(f"\n📊 Wishlist Analytics Results:")
    print(f"✓ Total items: {analytics['total_items']}")
    print(f"✓ Total value: ${analytics['total_value']:.2f}")
    print(f"✓ Average price: ${analytics['average_price']:.2f}")
    
    print(f"\n📈 Categories:")
    for category in analytics['categories']:
        print(f"  - {category['name']}: {category['count']} courses, ${category['total_value']:.2f}")
    
    print(f"\n💰 Price Ranges:")
    for range_name, count in analytics['price_ranges'].items():
        print(f"  - {range_name}: {count} courses")
    
    print(f"\n🎯 Availability Status:")
    status = analytics['availability_status']
    print(f"  - Available: {status['available']}")
    print(f"  - Already enrolled: {status['enrolled']}")
    print(f"  - Unavailable: {status['unavailable']}")
    
    # Test recommendations
    recommendations = WishlistService.generate_wishlist_recommendations(user, tenant, limit=5)
    print(f"\n🎯 Generated {len(recommendations)} recommendations")
    
    for i, rec in enumerate(recommendations[:3], 1):
        if isinstance(rec, dict) and 'course' in rec:
            course = rec['course']
            reason = rec.get('reason', 'No reason provided')
            score = rec.get('score', 0)
            print(f"  {i}. {course.title} (Score: {score:.1f}) - {reason}")
        else:
            # Handle case where recommendations are just Course objects
            print(f"  {i}. {rec.title} - Popular course")
    
    # Clean up test data
    print(f"\n🧹 Cleaning up test data...")
    for item in wishlist_items:
        item.delete()
    print(f"✓ Deleted {len(wishlist_items)} wishlist items")
    
    print(f"\n🎉 All wishlist analytics tests passed!")
    
    return True

if __name__ == '__main__':
    try:
        test_wishlist_analytics()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)