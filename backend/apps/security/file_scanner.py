"""
Advanced file upload security scanning service.
"""

import os
import hashlib
import mimetypes
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class VirusScanner:
    """Virus scanning service for uploaded files"""
    
    def __init__(self):
        self.enabled = getattr(settings, 'VIRUS_SCAN_ENABLED', True)
        self.quarantine_enabled = getattr(settings, 'FILE_QUARANTINE_ENABLED', True)
        self.quarantine_path = getattr(settings, 'QUARANTINE_PATH', '/tmp/quarantine/')
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scan file for viruses using ClamAV or similar"""
        if not self.enabled:
            return {
                'clean': True,
                'threats': [],
                'scanner': 'disabled',
                'scan_time': timezone.now().isoformat()
            }
        
        try:
            # Try ClamAV first
            result = self._scan_with_clamav(file_path)
            if result:
                return result
            
            # Fallback to basic pattern scanning
            return self._basic_malware_scan(file_path)
        
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {str(e)}")
            return {
                'clean': False,
                'threats': ['Scan error occurred'],
                'scanner': 'error',
                'scan_time': timezone.now().isoformat(),
                'error': str(e)
            }
    
    def _scan_with_clamav(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Scan file with ClamAV antivirus"""
        try:
            # Check if ClamAV is available
            result = subprocess.run(['which', 'clamscan'], capture_output=True, text=True)
            if result.returncode != 0:
                return None
            
            # Run ClamAV scan
            cmd = ['clamscan', '--no-summary', '--infected', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            scan_result = {
                'scanner': 'clamav',
                'scan_time': timezone.now().isoformat(),
                'clean': result.returncode == 0,
                'threats': []
            }
            
            if result.returncode != 0:
                # Parse ClamAV output for threats
                for line in result.stdout.split('\n'):
                    if 'FOUND' in line:
                        threat = line.split(':')[1].strip() if ':' in line else line.strip()
                        scan_result['threats'].append(threat)
            
            return scan_result
        
        except subprocess.TimeoutExpired:
            logger.warning(f"ClamAV scan timeout for {file_path}")
            return {
                'clean': False,
                'threats': ['Scan timeout'],
                'scanner': 'clamav',
                'scan_time': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"ClamAV scan error: {str(e)}")
            return None
    
    def _basic_malware_scan(self, file_path: str) -> Dict[str, Any]:
        """Basic malware pattern scanning"""
        threats = []
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024 * 1024)  # Read first 1MB
            
            # Check for common malware signatures
            malware_patterns = [
                b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*',  # EICAR test
                b'TVqQAAMAAAAEAAAA//8AALgAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAA',  # PE header
                b'MZ',  # DOS header
                b'#!/bin/sh',
                b'#!/bin/bash',
                b'powershell',
                b'cmd.exe',
                b'<script',
                b'javascript:',
                b'vbscript:',
            ]
            
            content_lower = content.lower()
            for pattern in malware_patterns:
                if pattern.lower() in content_lower:
                    threats.append(f"Suspicious pattern detected: {pattern.decode('utf-8', errors='ignore')}")
            
            return {
                'clean': len(threats) == 0,
                'threats': threats,
                'scanner': 'basic',
                'scan_time': timezone.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Basic scan error: {str(e)}")
            return {
                'clean': False,
                'threats': ['Scan error'],
                'scanner': 'basic',
                'scan_time': timezone.now().isoformat(),
                'error': str(e)
            }
    
    def quarantine_file(self, file_path: str, threat_info: Dict[str, Any]) -> str:
        """Move infected file to quarantine"""
        if not self.quarantine_enabled:
            return file_path
        
        try:
            # Create quarantine directory if it doesn't exist
            os.makedirs(self.quarantine_path, exist_ok=True)
            
            # Generate quarantine filename
            filename = os.path.basename(file_path)
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            quarantine_filename = f"{timestamp}_{filename}.quarantine"
            quarantine_file_path = os.path.join(self.quarantine_path, quarantine_filename)
            
            # Move file to quarantine
            os.rename(file_path, quarantine_file_path)
            
            # Create metadata file
            metadata = {
                'original_path': file_path,
                'quarantine_time': timezone.now().isoformat(),
                'threat_info': threat_info,
                'file_hash': self._calculate_file_hash(quarantine_file_path)
            }
            
            metadata_path = quarantine_file_path + '.meta'
            with open(metadata_path, 'w') as f:
                import json
                json.dump(metadata, f, indent=2)
            
            logger.warning(f"File quarantined: {file_path} -> {quarantine_file_path}")
            return quarantine_file_path
        
        except Exception as e:
            logger.error(f"Error quarantining file {file_path}: {str(e)}")
            return file_path
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ''


class FileContentAnalyzer:
    """Advanced file content analysis"""
    
    def __init__(self):
        self.max_analysis_size = 10 * 1024 * 1024  # 10MB
    
    def analyze_file(self, file_path: str, mime_type: str = None) -> Dict[str, Any]:
        """Comprehensive file analysis"""
        try:
            file_size = os.path.getsize(file_path)
            
            analysis = {
                'file_size': file_size,
                'mime_type': mime_type or mimetypes.guess_type(file_path)[0],
                'file_hash': self._calculate_hash(file_path),
                'entropy': self._calculate_entropy(file_path),
                'suspicious_strings': self._find_suspicious_strings(file_path),
                'embedded_files': self._detect_embedded_files(file_path),
                'metadata': self._extract_metadata(file_path),
                'risk_score': 0
            }
            
            # Calculate risk score
            analysis['risk_score'] = self._calculate_risk_score(analysis)
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {'error': str(e), 'risk_score': 100}
    
    def _calculate_hash(self, file_path: str) -> Dict[str, str]:
        """Calculate multiple hashes of the file"""
        hashes = {}
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            hashes['md5'] = hashlib.md5(content).hexdigest()
            hashes['sha1'] = hashlib.sha1(content).hexdigest()
            hashes['sha256'] = hashlib.sha256(content).hexdigest()
        
        except Exception as e:
            logger.error(f"Error calculating hash: {str(e)}")
        
        return hashes
    
    def _calculate_entropy(self, file_path: str) -> float:
        """Calculate file entropy (measure of randomness)"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read(min(self.max_analysis_size, os.path.getsize(file_path)))
            
            if not content:
                return 0.0
            
            # Calculate byte frequency
            byte_counts = [0] * 256
            for byte in content:
                byte_counts[byte] += 1
            
            # Calculate entropy
            entropy = 0.0
            content_length = len(content)
            
            for count in byte_counts:
                if count > 0:
                    probability = count / content_length
                    entropy -= probability * (probability.bit_length() - 1)
            
            return entropy
        
        except Exception as e:
            logger.error(f"Error calculating entropy: {str(e)}")
            return 0.0
    
    def _find_suspicious_strings(self, file_path: str) -> List[str]:
        """Find suspicious strings in file content"""
        suspicious_patterns = [
            # Network activity
            b'http://', b'https://', b'ftp://', b'tcp://', b'udp://',
            # System commands
            b'cmd.exe', b'powershell', b'/bin/sh', b'/bin/bash',
            # Registry operations
            b'HKEY_', b'RegOpenKey', b'RegSetValue',
            # File operations
            b'CreateFile', b'WriteFile', b'DeleteFile',
            # Crypto operations
            b'CryptAcquireContext', b'CryptGenKey',
            # Suspicious APIs
            b'VirtualAlloc', b'LoadLibrary', b'GetProcAddress',
            # Encoding/Obfuscation
            b'base64', b'eval(', b'exec(', b'decode(',
        ]
        
        suspicious_strings = []
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read(min(self.max_analysis_size, os.path.getsize(file_path)))
            
            content_lower = content.lower()
            
            for pattern in suspicious_patterns:
                if pattern in content_lower:
                    suspicious_strings.append(pattern.decode('utf-8', errors='ignore'))
        
        except Exception as e:
            logger.error(f"Error finding suspicious strings: {str(e)}")
        
        return suspicious_strings
    
    def _detect_embedded_files(self, file_path: str) -> List[Dict[str, Any]]:
        """Detect embedded files within the main file"""
        embedded_files = []
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read(min(self.max_analysis_size, os.path.getsize(file_path)))
            
            # Look for common file signatures
            signatures = {
                'PE': b'MZ',
                'PDF': b'%PDF',
                'ZIP': b'PK\x03\x04',
                'RAR': b'Rar!',
                'JPEG': b'\xff\xd8\xff',
                'PNG': b'\x89PNG',
                'GIF': b'GIF8',
                'ELF': b'\x7fELF',
            }
            
            for file_type, signature in signatures.items():
                offset = 0
                while True:
                    pos = content.find(signature, offset)
                    if pos == -1:
                        break
                    
                    embedded_files.append({
                        'type': file_type,
                        'offset': pos,
                        'signature': signature.hex()
                    })
                    
                    offset = pos + 1
        
        except Exception as e:
            logger.error(f"Error detecting embedded files: {str(e)}")
        
        return embedded_files
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract file metadata"""
        metadata = {}
        
        try:
            stat = os.stat(file_path)
            metadata.update({
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'permissions': oct(stat.st_mode)[-3:],
            })
            
            # Try to extract additional metadata based on file type
            mime_type = mimetypes.guess_type(file_path)[0]
            
            if mime_type and mime_type.startswith('image/'):
                metadata.update(self._extract_image_metadata(file_path))
            elif mime_type == 'application/pdf':
                metadata.update(self._extract_pdf_metadata(file_path))
        
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
        
        return metadata
    
    def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image metadata using PIL"""
        metadata = {}
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            with Image.open(file_path) as img:
                metadata['format'] = img.format
                metadata['mode'] = img.mode
                metadata['size'] = img.size
                
                # Extract EXIF data
                exif_data = img.getexif()
                if exif_data:
                    exif = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif[tag] = str(value)[:100]  # Limit length
                    metadata['exif'] = exif
        
        except Exception as e:
            logger.error(f"Error extracting image metadata: {str(e)}")
        
        return metadata
    
    def _extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = {}
        
        try:
            # Basic PDF header check
            with open(file_path, 'rb') as f:
                header = f.read(1024)
                if b'%PDF' in header:
                    metadata['pdf_version'] = header[header.find(b'%PDF'):header.find(b'%PDF') + 8].decode('utf-8', errors='ignore')
        
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {str(e)}")
        
        return metadata
    
    def _calculate_risk_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate risk score based on analysis results"""
        risk_score = 0
        
        # High entropy indicates possible encryption/packing
        entropy = analysis.get('entropy', 0)
        if entropy > 7.5:
            risk_score += 30
        elif entropy > 6.5:
            risk_score += 15
        
        # Suspicious strings
        suspicious_count = len(analysis.get('suspicious_strings', []))
        risk_score += min(suspicious_count * 10, 40)
        
        # Embedded files
        embedded_count = len(analysis.get('embedded_files', []))
        risk_score += min(embedded_count * 5, 20)
        
        # Large files are potentially more risky
        file_size = analysis.get('file_size', 0)
        if file_size > 100 * 1024 * 1024:  # 100MB
            risk_score += 10
        
        return min(risk_score, 100)


class FileUploadSecurityScanner:
    """Main file upload security scanner"""
    
    def __init__(self):
        self.virus_scanner = VirusScanner()
        self.content_analyzer = FileContentAnalyzer()
    
    def scan_uploaded_file(self, uploaded_file: UploadedFile) -> Dict[str, Any]:
        """Comprehensive security scan of uploaded file"""
        scan_results = {
            'safe': True,
            'threats': [],
            'warnings': [],
            'analysis': {},
            'scan_time': timezone.now().isoformat(),
            'file_info': {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'content_type': uploaded_file.content_type,
            }
        }
        
        # Create temporary file for scanning
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                # Write uploaded file to temporary location
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()
                
                temp_path = temp_file.name
                
                # Perform virus scan
                virus_results = self.virus_scanner.scan_file(temp_path)
                scan_results['virus_scan'] = virus_results
                
                if not virus_results['clean']:
                    scan_results['safe'] = False
                    scan_results['threats'].extend(virus_results['threats'])
                    
                    # Quarantine if threats found
                    if self.virus_scanner.quarantine_enabled:
                        quarantine_path = self.virus_scanner.quarantine_file(temp_path, virus_results)
                        scan_results['quarantined'] = quarantine_path
                
                # Perform content analysis
                if scan_results['safe']:  # Only analyze if no viruses found
                    analysis_results = self.content_analyzer.analyze_file(temp_path, uploaded_file.content_type)
                    scan_results['analysis'] = analysis_results
                    
                    # Check risk score
                    risk_score = analysis_results.get('risk_score', 0)
                    if risk_score > 70:
                        scan_results['safe'] = False
                        scan_results['threats'].append(f"High risk score: {risk_score}")
                    elif risk_score > 40:
                        scan_results['warnings'].append(f"Medium risk score: {risk_score}")
                
            except Exception as e:
                logger.error(f"Error scanning uploaded file: {str(e)}")
                scan_results['safe'] = False
                scan_results['threats'].append(f"Scan error: {str(e)}")
            
            finally:
                # Clean up temporary file (unless quarantined)
                if not scan_results.get('quarantined') and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        logger.error(f"Error cleaning up temp file: {str(e)}")
        
        return scan_results
    
    def get_scan_summary(self, scan_results: Dict[str, Any]) -> str:
        """Generate human-readable scan summary"""
        if scan_results['safe']:
            return "File passed security scan"
        
        threats = scan_results.get('threats', [])
        if threats:
            return f"Security threats detected: {', '.join(threats[:3])}"
        
        return "File failed security scan"