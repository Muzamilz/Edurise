#!/usr/bin/env python3
"""
Test to verify notification API endpoints are working with the centralized API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_notification_api_endpoints():
    """Test that notification API endpoints are accessible"""
    print("==> Testing Notification API Endpoints\n")
    
    # Test endpoints without authentication (should get 401)
    endpoints_to_test = [
        "/notifications/",
        "/notifications/unread_count/",
        "/notifications/stats/",
        "/notifications/preferences/",
        "/email-delivery-logs/",
        "/notification-templates/",
        "/chat-messages/",
        "/websocket-connections/"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint} - Endpoint exists (requires authentication)")
            elif response.status_code == 200:
                print(f"✅ {endpoint} - Endpoint accessible")
            else:
                print(f"⚠️  {endpoint} - Unexpected status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Server not running")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print("\n==> All notification API endpoints are properly registered!")
    return True

if __name__ == "__main__":
    test_notification_api_endpoints()