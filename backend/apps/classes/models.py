import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.courses.models import LiveClass

User = get_user_model()


class ClassAttendance(models.Model):
    """Track attendance for live classes"""
    
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('partial', 'Partial'),
        ('late', 'Late'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_attendances')
    
    status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='absent')
    join_time = models.DateTimeField(null=True, blank=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    
    # Engagement metrics
    participation_score = models.PositiveIntegerField(default=0)  # 0-100
    questions_asked = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'class_attendances'
        unique_together = ['live_class', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.live_class.title} ({self.status})"
    
    @property
    def attendance_percentage(self):
        """Calculate attendance percentage based on duration"""
        if self.live_class.duration_minutes > 0:
            return min(100, (self.duration_minutes / self.live_class.duration_minutes) * 100)
        return 0