#!/usr/bin/env python
"""
Quick script to populate test data for the courses page
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    print("🚀 Creating test data for courses page...")
    try:
        call_command('create_superuser_test_data')
        print("✅ Test data created successfully!")
        print("📚 You can now visit http://localhost:3000/courses to see the courses")
        print("🔑 Superuser login: superadmin@edurise.com / superadmin123")
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        sys.exit(1)