import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.common.models import TenantAwareModel

User = get_user_model()


class SecurityEvent(TenantAwareModel):
    """Security events and incidents tracking"""
    
    EVENT_TYPES = [
        ('login_failed', 'Failed Login Attempt'),
        ('login_success', 'Successful Login'),
        ('logout', 'User Logout'),
        ('password_change', 'Password Changed'),
        ('account_locked', 'Account Locked'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('data_access', 'Sensitive Data Access'),
        ('permission_denied', 'Permission Denied'),
        ('api_abuse', 'API Rate Limit Exceeded'),
        ('malware_detected', 'Malware Detection'),
        ('intrusion_attempt', 'Intrusion Attempt'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='low')
    
    # Event details
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_events')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    endpoint = models.CharField(max_length=200, blank=True)
    method = models.CharField(max_length=10, blank=True)
    
    # Event metadata
    description = models.TextField()
    additional_data = models.JSONField(default=dict, blank=True)
    
    # Status tracking
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_security_events'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['severity', 'is_resolved']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.severity} - {self.created_at}"
    
    def resolve(self, resolved_by, notes=""):
        """Mark security event as resolved"""
        self.is_resolved = True
        self.resolved_by = resolved_by
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()


class SecurityAlert(TenantAwareModel):
    """Security alerts for administrators"""
    
    ALERT_TYPES = [
        ('multiple_failed_logins', 'Multiple Failed Login Attempts'),
        ('suspicious_ip', 'Suspicious IP Activity'),
        ('account_compromise', 'Potential Account Compromise'),
        ('data_breach', 'Data Breach Detected'),
        ('system_intrusion', 'System Intrusion Attempt'),
        ('malware', 'Malware Detection'),
        ('ddos', 'DDoS Attack'),
        ('privilege_escalation', 'Privilege Escalation Attempt'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SecurityEvent.SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Related events
    related_events = models.ManyToManyField(SecurityEvent, blank=True)
    
    # Assignment and resolution
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_security_alerts'
    )
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_security_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.severity}"


# AuditLog is defined in admin_tools app to avoid conflicts


class SecurityPolicy(TenantAwareModel):
    """Security policies and configurations"""
    
    POLICY_TYPES = [
        ('password', 'Password Policy'),
        ('session', 'Session Management'),
        ('access_control', 'Access Control'),
        ('data_retention', 'Data Retention'),
        ('encryption', 'Encryption Policy'),
        ('backup', 'Backup Policy'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES)
    description = models.TextField()
    
    # Policy configuration
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    is_enforced = models.BooleanField(default=False)
    
    # Compliance
    compliance_frameworks = models.JSONField(default=list, blank=True)  # e.g., ['GDPR', 'SOC2']
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_policies'
        unique_together = ['tenant', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.policy_type}"


class ThreatIntelligence(models.Model):
    """Threat intelligence data for security monitoring"""
    
    THREAT_TYPES = [
        ('malicious_ip', 'Malicious IP Address'),
        ('malware_hash', 'Malware Hash'),
        ('suspicious_domain', 'Suspicious Domain'),
        ('attack_pattern', 'Attack Pattern'),
        ('vulnerability', 'Known Vulnerability'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPES)
    indicator = models.CharField(max_length=500)  # IP, hash, domain, etc.
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SecurityEvent.SEVERITY_LEVELS)
    
    # Threat metadata
    source = models.CharField(max_length=100, blank=True)  # Source of intelligence
    confidence_score = models.PositiveIntegerField(default=50)  # 0-100
    tags = models.JSONField(default=list, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'threat_intelligence'
        unique_together = ['threat_type', 'indicator']
        indexes = [
            models.Index(fields=['threat_type', 'indicator']),
            models.Index(fields=['severity', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.threat_type} - {self.indicator}"