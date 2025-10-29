"""
Django management command for GDPR data export.
"""

import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.security.services import ComplianceService

User = get_user_model()


class Command(BaseCommand):
    help = 'Export user data for GDPR compliance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address of the user to export data for',
            required=True
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (default: user_data_export_<timestamp>.json)',
            required=False
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv'],
            default='json',
            help='Export format (default: json)'
        )
    
    def handle(self, *args, **options):
        email = options['email']
        output_path = options.get('output')
        export_format = options['format']
        
        try:
            # Find the user
            user = User.objects.get(email=email)
            self.stdout.write(f"Found user: {user.email}")
            
            # Export user data
            self.stdout.write("Exporting user data...")
            user_data = ComplianceService.export_user_data(user)
            
            # Generate output filename if not provided
            if not output_path:
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                output_path = f"user_data_export_{timestamp}.{export_format}"
            
            # Export data based on format
            if export_format == 'json':
                self._export_json(user_data, output_path)
            elif export_format == 'csv':
                self._export_csv(user_data, output_path)
            
            self.stdout.write(
                self.style.SUCCESS(f"User data exported successfully to: {output_path}")
            )
            
        except User.DoesNotExist:
            raise CommandError(f"User with email '{email}' not found")
        
        except Exception as e:
            raise CommandError(f"Error exporting user data: {str(e)}")
    
    def _export_json(self, user_data, output_path):
        """Export data as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _export_csv(self, user_data, output_path):
        """Export data as CSV (simplified format)"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Category', 'Field', 'Value'])
            
            # Write personal info
            for key, value in user_data['personal_info'].items():
                writer.writerow(['Personal Info', key, value])
            
            # Write profile info
            for key, value in user_data['profile'].items():
                writer.writerow(['Profile', key, value])
            
            # Write courses
            for i, course in enumerate(user_data['courses']):
                for key, value in course.items():
                    writer.writerow([f'Course {i+1}', key, value])
            
            # Write payments
            for i, payment in enumerate(user_data['payments']):
                for key, value in payment.items():
                    writer.writerow([f'Payment {i+1}', key, value])
            
            # Write audit logs (limited)
            for i, log in enumerate(user_data['audit_logs'][:10]):  # First 10 logs
                for key, value in log.items():
                    writer.writerow([f'Audit Log {i+1}', key, value])