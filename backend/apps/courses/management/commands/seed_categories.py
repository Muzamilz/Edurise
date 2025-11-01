from django.core.management.base import BaseCommand
from apps.courses.models import CourseCategory


class Command(BaseCommand):
    help = 'Seed default course categories'

    def handle(self, *args, **options):
        """Create default global course categories"""
        
        default_categories = [
            {
                'name': 'Technology',
                'slug': 'technology',
                'description': 'Programming, software development, and IT courses',
                'icon': 'fas fa-laptop-code',
                'color': '#3B82F6',
                'sort_order': 1,
                'subcategories': [
                    {'name': 'Web Development', 'slug': 'web-development', 'icon': 'fas fa-globe'},
                    {'name': 'Mobile Development', 'slug': 'mobile-development', 'icon': 'fas fa-mobile-alt'},
                    {'name': 'Data Science', 'slug': 'data-science', 'icon': 'fas fa-chart-bar'},
                    {'name': 'Artificial Intelligence', 'slug': 'artificial-intelligence', 'icon': 'fas fa-robot'},
                    {'name': 'Cybersecurity', 'slug': 'cybersecurity', 'icon': 'fas fa-shield-alt'},
                ]
            },
            {
                'name': 'Business',
                'slug': 'business',
                'description': 'Business management, entrepreneurship, and strategy',
                'icon': 'fas fa-briefcase',
                'color': '#10B981',
                'sort_order': 2,
                'subcategories': [
                    {'name': 'Marketing', 'slug': 'marketing', 'icon': 'fas fa-bullhorn'},
                    {'name': 'Finance', 'slug': 'finance', 'icon': 'fas fa-dollar-sign'},
                    {'name': 'Project Management', 'slug': 'project-management', 'icon': 'fas fa-tasks'},
                    {'name': 'Leadership', 'slug': 'leadership', 'icon': 'fas fa-users'},
                ]
            },
            {
                'name': 'Design',
                'slug': 'design',
                'description': 'Graphic design, UI/UX, and creative arts',
                'icon': 'fas fa-palette',
                'color': '#F59E0B',
                'sort_order': 3,
                'subcategories': [
                    {'name': 'Graphic Design', 'slug': 'graphic-design', 'icon': 'fas fa-paint-brush'},
                    {'name': 'UI/UX Design', 'slug': 'ui-ux-design', 'icon': 'fas fa-desktop'},
                    {'name': 'Photography', 'slug': 'photography', 'icon': 'fas fa-camera'},
                    {'name': 'Video Editing', 'slug': 'video-editing', 'icon': 'fas fa-video'},
                ]
            },
            {
                'name': 'Language',
                'slug': 'language',
                'description': 'Language learning and communication skills',
                'icon': 'fas fa-language',
                'color': '#EF4444',
                'sort_order': 4,
                'subcategories': [
                    {'name': 'English', 'slug': 'english', 'icon': 'fas fa-flag-usa'},
                    {'name': 'Spanish', 'slug': 'spanish', 'icon': 'fas fa-flag'},
                    {'name': 'French', 'slug': 'french', 'icon': 'fas fa-flag'},
                    {'name': 'Mandarin', 'slug': 'mandarin', 'icon': 'fas fa-flag'},
                ]
            },
            {
                'name': 'Science',
                'slug': 'science',
                'description': 'Natural sciences, mathematics, and research',
                'icon': 'fas fa-flask',
                'color': '#8B5CF6',
                'sort_order': 5,
                'subcategories': [
                    {'name': 'Mathematics', 'slug': 'mathematics', 'icon': 'fas fa-calculator'},
                    {'name': 'Physics', 'slug': 'physics', 'icon': 'fas fa-atom'},
                    {'name': 'Chemistry', 'slug': 'chemistry', 'icon': 'fas fa-vial'},
                    {'name': 'Biology', 'slug': 'biology', 'icon': 'fas fa-dna'},
                ]
            },
            {
                'name': 'Health & Wellness',
                'slug': 'health-wellness',
                'description': 'Health, fitness, and personal development',
                'icon': 'fas fa-heartbeat',
                'color': '#06B6D4',
                'sort_order': 6,
                'subcategories': [
                    {'name': 'Fitness', 'slug': 'fitness', 'icon': 'fas fa-dumbbell'},
                    {'name': 'Nutrition', 'slug': 'nutrition', 'icon': 'fas fa-apple-alt'},
                    {'name': 'Mental Health', 'slug': 'mental-health', 'icon': 'fas fa-brain'},
                    {'name': 'Yoga & Meditation', 'slug': 'yoga-meditation', 'icon': 'fas fa-om'},
                ]
            }
        ]

        for category_data in default_categories:
            # Create parent category
            subcategories_data = category_data.pop('subcategories', [])
            
            parent_category, created = CourseCategory.objects.get_or_create(
                slug=category_data['slug'],
                tenant=None,  # Global category
                defaults=category_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {parent_category.name}')
                )
            
            # Create subcategories
            for sub_data in subcategories_data:
                sub_data['parent'] = parent_category
                sub_data['tenant'] = None  # Global category
                sub_data['color'] = parent_category.color  # Inherit parent color
                
                subcategory, sub_created = CourseCategory.objects.get_or_create(
                    slug=sub_data['slug'],
                    tenant=None,
                    defaults=sub_data
                )
                
                if sub_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created subcategory: {subcategory.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded course categories!')
        )