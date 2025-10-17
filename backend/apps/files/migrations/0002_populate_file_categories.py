from django.db import migrations


def create_file_categories(apps, schema_editor):
    """Create initial file categories"""
    FileCategory = apps.get_model('files', 'FileCategory')
    
    categories = [
        {
            'name': 'course_material',
            'display_name': 'Course Material',
            'allowed_extensions': ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md'],
            'max_file_size_mb': 50,
            'description': 'Course materials like slides, documents, and reading materials'
        },
        {
            'name': 'assignment_submission',
            'display_name': 'Assignment Submission',
            'allowed_extensions': ['pdf', 'doc', 'docx', 'txt', 'py', 'js', 'java', 'cpp', 'zip'],
            'max_file_size_mb': 25,
            'description': 'Student assignment submissions and project files'
        },
        {
            'name': 'certificate',
            'display_name': 'Certificate',
            'allowed_extensions': ['pdf'],
            'max_file_size_mb': 5,
            'description': 'Course completion certificates'
        },
        {
            'name': 'user_avatar',
            'display_name': 'User Avatar',
            'allowed_extensions': ['jpg', 'jpeg', 'png', 'gif'],
            'max_file_size_mb': 2,
            'description': 'User profile pictures and avatars'
        },
        {
            'name': 'course_thumbnail',
            'display_name': 'Course Thumbnail',
            'allowed_extensions': ['jpg', 'jpeg', 'png'],
            'max_file_size_mb': 5,
            'description': 'Course cover images and thumbnails'
        },
        {
            'name': 'recording',
            'display_name': 'Class Recording',
            'allowed_extensions': ['mp4', 'avi', 'mov', 'wmv', 'mp3', 'wav'],
            'max_file_size_mb': 500,
            'description': 'Class recordings and audio files'
        },
        {
            'name': 'document',
            'display_name': 'Document',
            'allowed_extensions': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
            'max_file_size_mb': 20,
            'description': 'General documents and text files'
        },
        {
            'name': 'image',
            'display_name': 'Image',
            'allowed_extensions': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'],
            'max_file_size_mb': 10,
            'description': 'Images and graphics'
        },
        {
            'name': 'video',
            'display_name': 'Video',
            'allowed_extensions': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
            'max_file_size_mb': 200,
            'description': 'Video files and multimedia content'
        },
        {
            'name': 'audio',
            'display_name': 'Audio',
            'allowed_extensions': ['mp3', 'wav', 'ogg', 'aac', 'm4a'],
            'max_file_size_mb': 50,
            'description': 'Audio files and recordings'
        },
        {
            'name': 'other',
            'display_name': 'Other',
            'allowed_extensions': [],  # Allow all types
            'max_file_size_mb': 10,
            'description': 'Other file types'
        }
    ]
    
    for category_data in categories:
        FileCategory.objects.get_or_create(
            name=category_data['name'],
            defaults=category_data
        )


def reverse_create_file_categories(apps, schema_editor):
    """Remove file categories"""
    FileCategory = apps.get_model('files', 'FileCategory')
    FileCategory.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_file_categories,
            reverse_create_file_categories
        ),
    ]