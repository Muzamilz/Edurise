from django.core.management.base import BaseCommand, CommandError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


class Command(BaseCommand):
    help = 'Test WebSocket functionality for live classes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing WebSocket setup...'))
        
        # Test 1: Check if channel layer is available
        try:
            channel_layer = get_channel_layer()
            if channel_layer is None:
                raise CommandError('Channel layer is not configured')
            
            self.stdout.write(self.style.SUCCESS('✓ Channel layer is configured'))
            
            # Test 2: Test basic group functionality
            test_group = "test_live_class_123"
            test_channel = "test_channel"
            
            # Add to group
            async_to_sync(channel_layer.group_add)(test_group, test_channel)
            self.stdout.write(self.style.SUCCESS('✓ Group add functionality works'))
            
            # Test message sending
            test_message = {
                'type': 'test_message',
                'data': {
                    'message': 'Hello WebSocket!',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
            
            async_to_sync(channel_layer.group_send)(test_group, test_message)
            self.stdout.write(self.style.SUCCESS('✓ Group send functionality works'))
            
            # Remove from group
            async_to_sync(channel_layer.group_discard)(test_group, test_channel)
            self.stdout.write(self.style.SUCCESS('✓ Group discard functionality works'))
            
            # Test 3: Test WebSocket service
            from apps.classes.websocket_service import websocket_service
            
            # Test broadcasting (won't actually send since no real connections)
            websocket_service.broadcast_class_status_update(
                'test-class-id', 
                'live', 
                {'test': True}
            )
            self.stdout.write(self.style.SUCCESS('✓ WebSocket service broadcasting works'))
            
            self.stdout.write(
                self.style.SUCCESS(
                    '\n🎉 All WebSocket tests passed!\n'
                    'Your WebSocket setup is ready for live classes.\n'
                    '\nNext steps:\n'
                    '1. Make sure Redis is running\n'
                    '2. Start Django server: python manage.py runserver\n'
                    '3. Test real WebSocket connections in the frontend'
                )
            )
            
        except Exception as e:
            raise CommandError(f'WebSocket test failed: {str(e)}')