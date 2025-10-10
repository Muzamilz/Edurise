#!/usr/bin/env python3
"""
Script to fix API endpoints in the integration test file
"""

import re

def fix_api_endpoints():
    file_path = "backend/tests/integration/test_ai_features.py"
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace all /api/ai/ with /api/v1/ai/
    content = content.replace('/api/ai/', '/api/v1/ai/')
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed API endpoints in test file")

if __name__ == '__main__':
    fix_api_endpoints()