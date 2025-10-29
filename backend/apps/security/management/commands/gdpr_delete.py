"""
Django management command for GDPR data deletion.
"""

import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.security.services import ComplianceService

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete user data for GDPR compliance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address of the user to delete data for',
            required=True
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the deletion (required to prevent accidental deletions)',
            required=True
        )
        parser.add_argument(
            '--export-first',
            action='store_true',
            help='Export user data before deletion',
            required=False
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for export (if --export-first is used)',
            required=False
        )
    
    def handle(self, *args, **options):
        email = options['email']
        confirm = options['confirm']
        export_first = options['export_first']
        output_path = options.get('output')
        
        if not confirm:
            raise CommandError("You must use --confirm to proceed with data deletion")
        
        try:
            # Find the user
            user = User.objects.get(email=email)
            self.stdout.write(f"Found user: {user.email}")
            
            # Prevent deletion of superuser accounts
            if user.is_superuser:
                raise CommandError("Cannot delete superuser accounts for safety reasons")
            
            # Export data first if requested
            if export_first:
                self.stdout.write("Exporting user data before deletion...")
                user_data = ComplianceService.export_user_data(user)
                
                if not output_path:
                    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                    output_path = f"user_data_export_before_deletion_{timestamp}.json"
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, indent=2, ensure_ascii=False, default=str)
                
                self.stdout.write(f"Data exported to: {output_path}")
            
            # Confirm deletion
            self.stdout.write(
                self.style.WARNING(
                    f"WARNING: This will permanently delete all data for user '{email}'"
                )
            )
            
            confirm_input = input("Type 'DELETE' to confirm: ")
            if confirm_input != 'DELETE':
                self.stdout.write("Deletion cancelled")
                return
            
            # Delete user data
            self.stdout.write("Deleting user data...")
            deletion_summary = ComplianceService.delete_user_data(user)
            
            # Save deletion summary
            summary_filename = f"deletion_summary_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                json.dump(deletion_summary, f, indent=2, ensure_ascii=False, default=str)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"User data deleted successfully. Summary saved to: {summary_filename}"
                )
            )
            
        except User.DoesNotExist:
            raise CommandError(f"User with email '{email}' not found")
        
        except Exception as e:
            raise CommandError(f"Error deleting user data: {str(e)}")