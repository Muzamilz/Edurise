import os
import requests
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Test Zoom API connection and functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-meeting',
            action='store_true',
            help='Create a test meeting',
        )
        parser.add_argument(
            '--list-meetings',
            action='store_true',
            help='List user meetings',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Zoom API connection...'))
        
        # Check if environment variables are set
        required_vars = ['ZOOM_ACCOUNT_ID', 'ZOOM_CLIENT_ID', 'ZOOM_CLIENT_SECRET']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise CommandError(
                f'Missing required environment variables: {", ".join(missing_vars)}\n'
                'Please check your .env file and ensure all Zoom API credentials are set.'
            )

        try:
            # Get access token
            access_token = self.get_access_token()
            self.stdout.write(self.style.SUCCESS('✓ Successfully authenticated with Zoom API'))
            
            if options['create_meeting']:
                self.create_test_meeting(access_token)
            
            if options['list_meetings']:
                self.list_meetings(access_token)
                
            if not options['create_meeting'] and not options['list_meetings']:
                self.stdout.write(
                    self.style.WARNING(
                        'Connection test completed. Use --create-meeting or --list-meetings for more tests.'
                    )
                )
                
        except Exception as e:
            raise CommandError(f'Zoom API test failed: {str(e)}')

    def get_access_token(self):
        """Get OAuth access token from Zoom"""
        account_id = os.getenv('ZOOM_ACCOUNT_ID')
        client_id = os.getenv('ZOOM_CLIENT_ID')
        client_secret = os.getenv('ZOOM_CLIENT_SECRET')
        
        url = 'https://zoom.us/oauth/token'
        
        headers = {
            'Authorization': f'Basic {self.encode_credentials(client_id, client_secret)}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'account_credentials',
            'account_id': account_id
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code != 200:
            raise Exception(f'Failed to get access token: {response.text}')
        
        return response.json()['access_token']

    def encode_credentials(self, client_id, client_secret):
        """Encode client credentials for Basic auth"""
        import base64
        credentials = f'{client_id}:{client_secret}'
        return base64.b64encode(credentials.encode()).decode()

    def create_test_meeting(self, access_token):
        """Create a test meeting"""
        self.stdout.write('Creating test meeting...')
        
        url = 'https://api.zoom.us/v2/users/me/meetings'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Schedule meeting for 1 hour from now
        start_time = datetime.now() + timedelta(hours=1)
        
        meeting_data = {
            'topic': 'Edurise LMS Test Meeting',
            'type': 2,  # Scheduled meeting
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'duration': 60,
            'timezone': 'UTC',
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': True,
                'watermark': False,
                'use_pmi': False,
                'approval_type': 0,  # Automatically approve
                'audio': 'both',
                'auto_recording': 'none'
            }
        }
        
        response = requests.post(url, headers=headers, json=meeting_data)
        
        if response.status_code == 201:
            meeting = response.json()
            self.stdout.write(self.style.SUCCESS('✓ Test meeting created successfully!'))
            self.stdout.write(f'  Meeting ID: {meeting["id"]}')
            self.stdout.write(f'  Topic: {meeting["topic"]}')
            self.stdout.write(f'  Start Time: {meeting["start_time"]}')
            self.stdout.write(f'  Join URL: {meeting["join_url"]}')
            self.stdout.write(f'  Start URL: {meeting["start_url"]}')
            self.stdout.write(f'  Password: {meeting.get("password", "None")}')
        else:
            raise Exception(f'Failed to create meeting: {response.text}')

    def list_meetings(self, access_token):
        """List user meetings"""
        self.stdout.write('Fetching user meetings...')
        
        url = 'https://api.zoom.us/v2/users/me/meetings'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'type': 'scheduled',
            'page_size': 10
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            meetings = data.get('meetings', [])
            
            if meetings:
                self.stdout.write(self.style.SUCCESS(f'✓ Found {len(meetings)} scheduled meetings:'))
                for meeting in meetings:
                    self.stdout.write(f'  - {meeting["topic"]} (ID: {meeting["id"]})')
                    self.stdout.write(f'    Start: {meeting.get("start_time", "N/A")}')
                    self.stdout.write(f'    Duration: {meeting.get("duration", "N/A")} minutes')
                    self.stdout.write('')
            else:
                self.stdout.write(self.style.WARNING('No scheduled meetings found.'))
        else:
            raise Exception(f'Failed to list meetings: {response.text}')