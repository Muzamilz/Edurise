"""
Input validation and sanitization utilities for security.
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from django.utils.html import strip_tags
from django.conf import settings
import logging

# Try to import bleach, fallback to basic sanitization if not available
try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False

logger = logging.getLogger(__name__)


class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)",
        r"(\bxp_\w+|\bsp_\w+)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
        r"..%2f",
        r"..%5c",
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$(){}[\]<>]",
        r"\b(cat|ls|dir|type|copy|move|del|rm|mkdir|rmdir|chmod|chown)\b",
        r"\b(wget|curl|nc|netcat|telnet|ssh|ftp)\b",
        r"\b(python|perl|php|ruby|bash|sh|cmd|powershell)\b",
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = None, allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        
        if allow_html and BLEACH_AVAILABLE:
            # Use bleach to sanitize HTML
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
            allowed_attributes = {'a': ['href', 'title'], '*': ['class']}
            value = bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        else:
            # Strip all HTML tags
            value = strip_tags(value)
            # HTML escape remaining content
            value = html.escape(value)
        
        # Truncate if max_length specified
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @classmethod
    def validate_sql_injection(cls, value: str) -> bool:
        """Check for SQL injection patterns"""
        if not isinstance(value, str):
            return True
        
        value_lower = value.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def validate_xss(cls, value: str) -> bool:
        """Check for XSS patterns"""
        if not isinstance(value, str):
            return True
        
        value_lower = value.lower()
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"XSS pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def validate_path_traversal(cls, value: str) -> bool:
        """Check for path traversal patterns"""
        if not isinstance(value, str):
            return True
        
        value_lower = value.lower()
        
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"Path traversal pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def validate_command_injection(cls, value: str) -> bool:
        """Check for command injection patterns"""
        if not isinstance(value, str):
            return True
        
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Command injection pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def validate_email_address(cls, email: str) -> bool:
        """Validate email address format"""
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL format"""
        try:
            validator = URLValidator()
            validator(url)
            return True
        except ValidationError:
            return False
    
    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """Validate filename for security"""
        if not isinstance(filename, str):
            return False
        
        # Check for path traversal
        if not cls.validate_path_traversal(filename):
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
        if any(char in filename for char in dangerous_chars):
            return False
        
        # Check for reserved names (Windows)
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], max_string_length: int = 1000) -> Dict[str, Any]:
        """Recursively sanitize dictionary data"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            clean_key = cls.sanitize_string(str(key), max_length=100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                clean_value = cls.sanitize_string(value, max_length=max_string_length)
            elif isinstance(value, dict):
                clean_value = cls.sanitize_dict(value, max_string_length)
            elif isinstance(value, list):
                clean_value = cls.sanitize_list(value, max_string_length)
            else:
                clean_value = value
            
            sanitized[clean_key] = clean_value
        
        return sanitized
    
    @classmethod
    def sanitize_list(cls, data: List[Any], max_string_length: int = 1000) -> List[Any]:
        """Recursively sanitize list data"""
        if not isinstance(data, list):
            return data
        
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                clean_item = cls.sanitize_string(item, max_length=max_string_length)
            elif isinstance(item, dict):
                clean_item = cls.sanitize_dict(item, max_string_length)
            elif isinstance(item, list):
                clean_item = cls.sanitize_list(item, max_string_length)
            else:
                clean_item = item
            
            sanitized.append(clean_item)
        
        return sanitized
    
    @classmethod
    def validate_input_security(cls, value: str) -> Dict[str, bool]:
        """Comprehensive security validation"""
        if not isinstance(value, str):
            return {'valid': True, 'sql_safe': True, 'xss_safe': True, 'path_safe': True, 'command_safe': True}
        
        results = {
            'sql_safe': cls.validate_sql_injection(value),
            'xss_safe': cls.validate_xss(value),
            'path_safe': cls.validate_path_traversal(value),
            'command_safe': cls.validate_command_injection(value),
        }
        
        results['valid'] = all(results.values())
        
        return results


class FileValidator:
    """File upload security validation"""
    
    DANGEROUS_EXTENSIONS = getattr(settings, 'BLOCKED_FILE_EXTENSIONS', [
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
        'php', 'asp', 'aspx', 'jsp', 'py', 'pl', 'sh', 'ps1'
    ])
    
    ALLOWED_EXTENSIONS = getattr(settings, 'ALLOWED_FILE_EXTENSIONS', [
        'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
        'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm',
        'mp3', 'wav', 'ogg', 'aac', 'm4a',
        'zip', 'rar', '7z', 'tar', 'gz'
    ])
    
    MAX_FILE_SIZE = getattr(settings, 'MAX_FILE_SIZE_MB', 100) * 1024 * 1024  # Convert to bytes
    
    # File signature patterns (magic numbers)
    FILE_SIGNATURES = {
        'pdf': [b'%PDF'],
        'jpg': [b'\xff\xd8\xff'],
        'jpeg': [b'\xff\xd8\xff'],
        'png': [b'\x89PNG\r\n\x1a\n'],
        'gif': [b'GIF87a', b'GIF89a'],
        'zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'],
        'doc': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],
        'docx': [b'PK\x03\x04'],
        'mp4': [b'ftyp'],
        'mp3': [b'ID3', b'\xff\xfb'],
    }
    
    @classmethod
    def validate_file_extension(cls, filename: str) -> bool:
        """Validate file extension"""
        if not filename:
            return False
        
        extension = filename.lower().split('.')[-1]
        
        # Check if extension is blocked
        if extension in cls.DANGEROUS_EXTENSIONS:
            logger.warning(f"Blocked file extension detected: {extension}")
            return False
        
        # Check if extension is allowed (if whitelist is configured)
        if cls.ALLOWED_EXTENSIONS and extension not in cls.ALLOWED_EXTENSIONS:
            logger.warning(f"File extension not in whitelist: {extension}")
            return False
        
        return True
    
    @classmethod
    def validate_file_size(cls, file_size: int) -> bool:
        """Validate file size"""
        return file_size <= cls.MAX_FILE_SIZE
    
    @classmethod
    def validate_file_signature(cls, file_content: bytes, filename: str) -> bool:
        """Validate file signature matches extension"""
        if not file_content or len(file_content) < 10:
            return True  # Skip validation for very small files
        
        extension = filename.lower().split('.')[-1]
        
        if extension not in cls.FILE_SIGNATURES:
            return True  # No signature check available
        
        signatures = cls.FILE_SIGNATURES[extension]
        
        for signature in signatures:
            if file_content.startswith(signature):
                return True
            # For some formats, check at different offsets
            if extension == 'mp4' and signature in file_content[:100]:
                return True
        
        logger.warning(f"File signature mismatch for {filename} (extension: {extension})")
        return False
    
    @classmethod
    def scan_file_content(cls, file_content: bytes) -> Dict[str, Any]:
        """Basic file content scanning"""
        results = {
            'safe': True,
            'threats': [],
            'suspicious_patterns': []
        }
        
        # Check for embedded scripts
        script_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'<?php',
            b'<%',
            b'#!/bin/sh',
            b'#!/bin/bash',
            b'powershell',
        ]
        
        for pattern in script_patterns:
            if pattern in file_content.lower():
                results['threats'].append(f"Embedded script detected: {pattern.decode('utf-8', errors='ignore')}")
                results['safe'] = False
        
        # Check for suspicious strings
        suspicious_patterns = [
            b'eval(',
            b'exec(',
            b'system(',
            b'shell_exec(',
            b'passthru(',
            b'base64_decode(',
            b'gzinflate(',
            b'str_rot13(',
        ]
        
        for pattern in suspicious_patterns:
            if pattern in file_content.lower():
                results['suspicious_patterns'].append(f"Suspicious pattern: {pattern.decode('utf-8', errors='ignore')}")
        
        return results
    
    @classmethod
    def validate_file(cls, file, filename: str = None) -> Dict[str, Any]:
        """Comprehensive file validation"""
        if not filename:
            filename = getattr(file, 'name', 'unknown')
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate filename
        if not InputValidator.validate_filename(filename):
            results['valid'] = False
            results['errors'].append("Invalid filename")
        
        # Validate extension
        if not cls.validate_file_extension(filename):
            results['valid'] = False
            results['errors'].append("File extension not allowed")
        
        # Validate size
        file_size = getattr(file, 'size', 0)
        if not cls.validate_file_size(file_size):
            results['valid'] = False
            results['errors'].append(f"File size exceeds maximum allowed size ({cls.MAX_FILE_SIZE // (1024*1024)}MB)")
        
        # Read file content for signature validation
        try:
            file.seek(0)
            file_content = file.read(1024)  # Read first 1KB for signature check
            file.seek(0)  # Reset file pointer
            
            # Validate file signature
            if not cls.validate_file_signature(file_content, filename):
                results['warnings'].append("File signature doesn't match extension")
            
            # Scan file content
            scan_results = cls.scan_file_content(file_content)
            if not scan_results['safe']:
                results['valid'] = False
                results['errors'].extend(scan_results['threats'])
            
            if scan_results['suspicious_patterns']:
                results['warnings'].extend(scan_results['suspicious_patterns'])
        
        except Exception as e:
            logger.error(f"Error validating file content: {str(e)}")
            results['warnings'].append("Could not validate file content")
        
        return results


class SecurityValidator:
    """Main security validation interface"""
    
    @staticmethod
    def validate_request_data(data: Union[Dict, List, str]) -> Dict[str, Any]:
        """Validate request data for security threats"""
        results = {
            'valid': True,
            'sanitized_data': data,
            'security_issues': []
        }
        
        try:
            if isinstance(data, str):
                # Validate string input
                validation_results = InputValidator.validate_input_security(data)
                if not validation_results['valid']:
                    results['valid'] = False
                    results['security_issues'].append("Security threat detected in input")
                
                results['sanitized_data'] = InputValidator.sanitize_string(data)
            
            elif isinstance(data, dict):
                # Validate and sanitize dictionary
                results['sanitized_data'] = InputValidator.sanitize_dict(data)
                
                # Check each string value for security issues
                for key, value in data.items():
                    if isinstance(value, str):
                        validation_results = InputValidator.validate_input_security(value)
                        if not validation_results['valid']:
                            results['valid'] = False
                            results['security_issues'].append(f"Security threat detected in field: {key}")
            
            elif isinstance(data, list):
                # Validate and sanitize list
                results['sanitized_data'] = InputValidator.sanitize_list(data)
                
                # Check each string item for security issues
                for i, item in enumerate(data):
                    if isinstance(item, str):
                        validation_results = InputValidator.validate_input_security(item)
                        if not validation_results['valid']:
                            results['valid'] = False
                            results['security_issues'].append(f"Security threat detected in list item {i}")
        
        except Exception as e:
            logger.error(f"Error validating request data: {str(e)}")
            results['valid'] = False
            results['security_issues'].append("Validation error occurred")
        
        return results
    
    @staticmethod
    def validate_file_upload(file, filename: str = None) -> Dict[str, Any]:
        """Validate file upload for security"""
        return FileValidator.validate_file(file, filename)