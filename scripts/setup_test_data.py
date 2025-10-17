#!/usr/bin/env python
"""
Quick script to set up comprehensive test data for Edurise LMS Platform
"""

import os
import sys
import subprocess

def main():
    print("🚀 Setting up comprehensive test data for Edurise LMS Platform...")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        return
    
    os.chdir(backend_dir)
    
    # Run the management command
    try:
        print("📊 Creating comprehensive test data...")
        result = subprocess.run([
            sys.executable, 'manage.py', 'setup_comprehensive_data',
            '--clean',  # Clean existing data
            '--organizations', '5',  # Create 5 organizations
            '--users-per-org', '25',  # 25 users per organization
            '--courses-per-teacher', '3'  # 3 courses per teacher
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        
        print("\n🎉 Test data setup completed successfully!")
        print("\n🔑 LOGIN CREDENTIALS:")
        print("Super Admin: admin@edurise.com / admin123456")
        print("Org Admins: admin@[subdomain].com / admin123456")
        print("Teachers: teacher[N]@[subdomain].com / teacher123456")
        print("Students: student[N]@[subdomain].com / student123456")
        
        print("\n🏢 ORGANIZATIONS CREATED:")
        print("- Edurise Platform (main) - Enterprise")
        print("- Tech University (techuni) - Pro")
        print("- Business Academy (bizacademy) - Pro")
        print("- Creative Institute (creative) - Basic")
        print("- Medical College (medcollege) - Enterprise")
        
        print("\n🌐 ACCESS URLs:")
        print("- Main Platform: http://localhost:3000")
        print("- Tech University: http://techuni.localhost:3000")
        print("- Business Academy: http://bizacademy.localhost:3000")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running setup command: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return

if __name__ == '__main__':
    main()