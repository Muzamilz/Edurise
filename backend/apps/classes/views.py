from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
from .models import ClassAttendance
from .services import ZoomService, AttendanceService
from apps.courses.models import LiveClass, ClassRecording
from apps.api.mixins import StandardViewSetMixin


class ClassAttendanceViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for ClassAttendance model with centralized API integration"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    # Query optimization fields
    select_related_fields = ['live_class', 'live_class__course', 'student']
    prefetch_related_fields = []
    
    def get_queryset(self):
        """Filter attendance by tenant with optimized queries"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return ClassAttendance.objects.filter(
                live_class__course__tenant=self.request.tenant
            ).select_related(
                'live_class', 'live_class__course', 'student'
            )
        return ClassAttendance.objects.none()
    
    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        """Mark attendance for a live class"""
        live_class_id = request.data.get('live_class_id')
        student_id = request.data.get('student_id')
        attendance_status = request.data.get('status', 'present')
        
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check permissions
            if (live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return self.error_response(
                    message='Permission denied',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            student = User.objects.get(id=student_id)
            
            attendance = AttendanceService.mark_attendance(
                live_class=live_class,
                student=student,
                status=attendance_status
            )
            
            # Broadcast attendance update via WebSocket
            from apps.classes.websocket_service import broadcast_attendance_update
            broadcast_attendance_update(
                str(live_class.id),
                {
                    'student_id': str(student.id),
                    'student_name': student.get_full_name(),
                    'status': attendance_status,
                    'attendance_id': str(attendance.id)
                }
            )
            
            return self.success_response(
                data={
                    'attendance_id': str(attendance.id),
                    'live_class_id': str(live_class.id),
                    'student_id': str(student.id),
                    'status': attendance_status,
                    'join_time': attendance.join_time,
                    'duration_minutes': attendance.duration_minutes
                },
                message='Attendance marked successfully'
            )
            
        except (LiveClass.DoesNotExist, User.DoesNotExist) as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def class_report(self, request):
        """Get attendance report for a live class"""
        live_class_id = request.query_params.get('live_class_id')
        
        if not live_class_id:
            return self.error_response(
                message='live_class_id parameter required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check permissions
            if (live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return self.error_response(
                    message='Permission denied',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Get engagement metrics
            metrics = AttendanceService.calculate_engagement_metrics(live_class)
            
            # Get individual attendance records
            attendances = live_class.attendances.all()
            attendance_data = []
            
            for attendance in attendances:
                attendance_data.append({
                    'attendance_id': str(attendance.id),
                    'student_id': str(attendance.student.id),
                    'student_name': attendance.student.get_full_name(),
                    'student_email': attendance.student.email,
                    'status': attendance.status,
                    'join_time': attendance.join_time,
                    'leave_time': attendance.leave_time,
                    'duration_minutes': attendance.duration_minutes,
                    'attendance_percentage': attendance.attendance_percentage,
                    'participation_score': attendance.participation_score,
                    'questions_asked': attendance.questions_asked
                })
            
            return self.success_response(
                data={
                    'live_class': {
                        'id': str(live_class.id),
                        'title': live_class.title,
                        'course_title': live_class.course.title,
                        'instructor_name': live_class.course.instructor.get_full_name(),
                        'scheduled_at': live_class.scheduled_at,
                        'duration_minutes': live_class.duration_minutes,
                        'status': live_class.status,
                        'zoom_meeting_id': live_class.zoom_meeting_id
                    },
                    'metrics': metrics,
                    'attendances': attendance_data
                },
                message='Attendance report retrieved successfully'
            )
            
        except LiveClass.DoesNotExist:
            return self.error_response(
                message='Live class not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update attendance records"""
        live_class_id = request.data.get('live_class_id')
        attendance_data = request.data.get('attendance_data', [])
        
        if not live_class_id:
            return self.error_response(
                message='live_class_id is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check permissions
            if (live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return self.error_response(
                    message='Permission denied',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            updated_attendances = []
            errors = []
            
            for data in attendance_data:
                student_id = data.get('student')
                if not student_id:
                    errors.append({'student': 'Student ID is required'})
                    continue
                
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    student = User.objects.get(id=student_id)
                    
                    attendance = AttendanceService.mark_attendance(
                        live_class=live_class,
                        student=student,
                        status=data.get('status', 'present'),
                        join_time=data.get('join_time'),
                        leave_time=data.get('leave_time')
                    )
                    
                    # Update additional fields
                    if 'participation_score' in data:
                        attendance.participation_score = data['participation_score']
                    if 'questions_asked' in data:
                        attendance.questions_asked = data['questions_asked']
                    
                    attendance.save()
                    updated_attendances.append({
                        'attendance_id': str(attendance.id),
                        'student_id': str(student.id),
                        'student_name': student.get_full_name(),
                        'status': attendance.status
                    })
                    
                except User.DoesNotExist:
                    errors.append({'student': f'Student with ID {student_id} not found'})
                    continue
            
            # Broadcast bulk attendance update via WebSocket
            if updated_attendances:
                from apps.classes.websocket_service import broadcast_attendance_update
                broadcast_attendance_update(
                    str(live_class.id),
                    {
                        'bulk_update': True,
                        'updated_count': len(updated_attendances),
                        'attendances': updated_attendances
                    }
                )
            
            return self.success_response(
                data={
                    'updated_count': len(updated_attendances),
                    'updated_attendances': updated_attendances,
                    'errors': errors,
                    'live_class_id': str(live_class.id)
                },
                message=f'Updated {len(updated_attendances)} attendance records'
            )
            
        except LiveClass.DoesNotExist:
            return self.error_response(
                message='Live class not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def live_status(self, request):
        """Get real-time status of live classes"""
        live_class_id = request.query_params.get('live_class_id')
        
        if not live_class_id:
            return self.error_response(
                message='live_class_id parameter required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check if user has access to this class
            from apps.courses.models import Enrollment
            has_access = (
                live_class.course.instructor == request.user or
                request.user.is_staff or
                Enrollment.objects.filter(
                    student=request.user,
                    course=live_class.course,
                    status='active'
                ).exists()
            )
            
            if not has_access:
                return self.error_response(
                    message='Permission denied',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Get current participants
            current_attendances = live_class.attendances.filter(
                status__in=['present', 'partial', 'late'],
                leave_time__isnull=True
            ).select_related('student')
            
            participants = []
            for attendance in current_attendances:
                participants.append({
                    'student_id': str(attendance.student.id),
                    'student_name': attendance.student.get_full_name(),
                    'student_email': attendance.student.email,
                    'join_time': attendance.join_time,
                    'duration_minutes': attendance.duration_minutes,
                    'status': attendance.status
                })
            
            # Get engagement metrics
            metrics = AttendanceService.calculate_engagement_metrics(live_class)
            
            return self.success_response(
                data={
                    'live_class': {
                        'id': str(live_class.id),
                        'title': live_class.title,
                        'status': live_class.status,
                        'scheduled_at': live_class.scheduled_at,
                        'duration_minutes': live_class.duration_minutes,
                        'zoom_meeting_id': live_class.zoom_meeting_id
                    },
                    'current_participants': participants,
                    'participant_count': len(participants),
                    'engagement_metrics': metrics,
                    'is_instructor': live_class.course.instructor == request.user
                },
                message='Live class status retrieved successfully'
            )
            
        except LiveClass.DoesNotExist:
            return self.error_response(
                message='Live class not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def attendance_analytics(self, request):
        """Get comprehensive attendance analytics for instructor"""
        if not request.user.is_teacher and not request.user.is_staff:
            return self.error_response(
                message='Only instructors can access attendance analytics',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Get date range from query params
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get live classes for the instructor
        live_classes = LiveClass.objects.filter(
            course__instructor=request.user,
            scheduled_at__gte=start_date,
            scheduled_at__lte=end_date
        ).select_related('course')
        
        analytics_data = []
        total_classes = 0
        total_students = 0
        total_attendance_rate = 0
        
        for live_class in live_classes:
            metrics = AttendanceService.calculate_engagement_metrics(live_class)
            analytics_data.append({
                'live_class_id': str(live_class.id),
                'class_title': live_class.title,
                'course_title': live_class.course.title,
                'scheduled_at': live_class.scheduled_at,
                'status': live_class.status,
                'metrics': metrics
            })
            
            total_classes += 1
            total_students += metrics['total_students']
            total_attendance_rate += metrics['attendance_rate']
        
        # Calculate overall statistics
        avg_attendance_rate = total_attendance_rate / total_classes if total_classes > 0 else 0
        avg_students_per_class = total_students / total_classes if total_classes > 0 else 0
        
        return self.success_response(
            data={
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days
                },
                'summary': {
                    'total_classes': total_classes,
                    'total_students': total_students,
                    'average_attendance_rate': round(avg_attendance_rate, 2),
                    'average_students_per_class': round(avg_students_per_class, 2)
                },
                'class_analytics': analytics_data
            },
            message='Attendance analytics retrieved successfully'
        )
    
    @action(detail=False, methods=['post'])
    def update_participation(self, request):
        """Update participation score and questions asked for a student"""
        attendance_id = request.data.get('attendance_id')
        participation_score = request.data.get('participation_score')
        questions_asked = request.data.get('questions_asked')
        
        if not attendance_id:
            return self.error_response(
                message='attendance_id is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            attendance = ClassAttendance.objects.get(id=attendance_id)
            
            # Check permissions
            if (attendance.live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return self.error_response(
                    message='Permission denied',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Update participation data
            if participation_score is not None:
                attendance.participation_score = max(0, min(100, int(participation_score)))
            
            if questions_asked is not None:
                attendance.questions_asked = max(0, int(questions_asked))
            
            attendance.save()
            
            # Broadcast participation update via WebSocket
            from apps.classes.websocket_service import broadcast_engagement_update
            metrics = AttendanceService.calculate_engagement_metrics(attendance.live_class)
            broadcast_engagement_update(
                str(attendance.live_class.id),
                metrics
            )
            
            return self.success_response(
                data={
                    'attendance_id': str(attendance.id),
                    'student_name': attendance.student.get_full_name(),
                    'participation_score': attendance.participation_score,
                    'questions_asked': attendance.questions_asked,
                    'updated_metrics': metrics
                },
                message='Participation data updated successfully'
            )
            
        except ClassAttendance.DoesNotExist:
            return self.error_response(
                message='Attendance record not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return self.error_response(
                message=f'Invalid data: {str(e)}',
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ClassRecordingViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for ClassRecording model with centralized API integration"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    # Query optimization fields
    select_related_fields = ['live_class', 'live_class__course', 'live_class__course__instructor']
    prefetch_related_fields = []
    
    def get_queryset(self):
        """Filter recordings by tenant and user access"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = ClassRecording.objects.filter(
                live_class__course__tenant=self.request.tenant
            ).select_related(
                'live_class', 'live_class__course', 'live_class__course__instructor'
            )
            
            # Filter by user access
            accessible_recordings = []
            for recording in queryset:
                if recording.can_access(self.request.user):
                    accessible_recordings.append(recording.id)
            
            return queryset.filter(id__in=accessible_recordings)
        
        return ClassRecording.objects.none()
    
    @action(detail=True, methods=['post'])
    def access_recording(self, request, pk=None):
        """Get secure access to a recording file"""
        recording = self.get_object()
        
        # Check access permissions
        if not recording.can_access(request.user):
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Check password if required
        if recording.password_protected:
            provided_password = request.data.get('password')
            if not provided_password or provided_password != recording.access_password:
                return self.error_response(
                    message='Invalid password',
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
        
        # Increment view count
        recording.increment_view_count()
        
        # Generate secure access URL (implement based on your storage backend)
        # For now, return the direct URL
        access_url = recording.file_url
        
        return self.success_response(
            data={
                'recording_id': str(recording.id),
                'access_url': access_url,
                'title': recording.title,
                'duration_minutes': recording.duration_minutes,
                'file_format': recording.file_format,
                'thumbnail_url': recording.thumbnail_url,
                'expires_at': timezone.now() + timezone.timedelta(hours=2)  # 2-hour access
            },
            message='Recording access granted'
        )
    
    @action(detail=True, methods=['post'])
    def download_recording(self, request, pk=None):
        """Get download link for a recording"""
        recording = self.get_object()
        
        # Check access permissions
        if not recording.can_access(request.user):
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Check if downloads are allowed for this access level
        if recording.access_level == 'public' and not request.user.is_authenticated:
            return self.error_response(
                message='Authentication required for downloads',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Increment download count
        recording.increment_download_count()
        
        # Generate secure download URL
        download_url = recording.file_url  # Implement secure URL generation
        
        return self.success_response(
            data={
                'recording_id': str(recording.id),
                'download_url': download_url,
                'filename': f"{recording.title}.{recording.file_format}",
                'file_size_mb': recording.file_size_mb,
                'expires_at': timezone.now() + timezone.timedelta(hours=1)  # 1-hour download link
            },
            message='Download link generated'
        )
    
    @action(detail=False, methods=['get'])
    def my_recordings(self, request):
        """Get recordings accessible to the current user"""
        # Get recordings from enrolled courses or taught courses
        if request.user.is_teacher:
            # For instructors, get recordings from their courses
            recordings = self.get_queryset().filter(
                live_class__course__instructor=request.user
            ).order_by('-recorded_at')[:20]
        else:
            # For students, get recordings from enrolled courses
            from apps.courses.models import Enrollment
            enrolled_courses = Enrollment.objects.filter(
                student=request.user,
                status='active'
            ).values_list('course_id', flat=True)
            
            recordings = self.get_queryset().filter(
                live_class__course_id__in=enrolled_courses
            ).order_by('-recorded_at')[:20]
        
        recording_data = []
        for recording in recordings:
            recording_data.append({
                'id': str(recording.id),
                'title': recording.title,
                'live_class_title': recording.live_class.title,
                'course_title': recording.live_class.course.title,
                'instructor_name': recording.live_class.course.instructor.get_full_name(),
                'duration_minutes': recording.duration_minutes,
                'file_format': recording.file_format,
                'file_size_mb': recording.file_size_mb,
                'thumbnail_url': recording.thumbnail_url,
                'recorded_at': recording.recorded_at,
                'view_count': recording.view_count,
                'access_level': recording.access_level,
                'password_protected': recording.password_protected
            })
        
        return self.success_response(
            data={
                'recordings': recording_data,
                'total_count': len(recording_data),
                'user_type': 'instructor' if request.user.is_teacher else 'student'
            },
            message='User recordings retrieved successfully'
        )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get recording analytics for instructors"""
        if not request.user.is_teacher and not request.user.is_staff:
            return self.error_response(
                message='Only instructors can access recording analytics',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Get recordings from instructor's courses
        recordings = self.get_queryset().filter(
            live_class__course__instructor=request.user
        )
        
        # Calculate analytics
        total_recordings = recordings.count()
        total_views = sum(recording.view_count for recording in recordings)
        total_downloads = sum(recording.download_count for recording in recordings)
        total_duration = sum(recording.duration_minutes for recording in recordings)
        total_size_gb = sum(recording.file_size_mb for recording in recordings) / 1024
        
        # Most viewed recordings
        most_viewed = recordings.order_by('-view_count')[:5]
        most_viewed_data = []
        for recording in most_viewed:
            most_viewed_data.append({
                'id': str(recording.id),
                'title': recording.title,
                'live_class_title': recording.live_class.title,
                'view_count': recording.view_count,
                'download_count': recording.download_count,
                'recorded_at': recording.recorded_at
            })
        
        return self.success_response(
            data={
                'summary': {
                    'total_recordings': total_recordings,
                    'total_views': total_views,
                    'total_downloads': total_downloads,
                    'total_duration_hours': round(total_duration / 60, 2),
                    'total_size_gb': round(total_size_gb, 2),
                    'average_views_per_recording': round(total_views / total_recordings, 2) if total_recordings > 0 else 0
                },
                'most_viewed_recordings': most_viewed_data
            },
            message='Recording analytics retrieved successfully'
        )


@method_decorator(csrf_exempt, name='dispatch')
class ZoomWebhookView(APIView):
    """Handle Zoom webhooks for attendance tracking"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Process Zoom webhook events with enhanced real-time updates"""
        try:
            webhook_data = json.loads(request.body)
            
            # Verify webhook (in production, verify the signature)
            event_type = webhook_data.get('event')
            
            if event_type in [
                'meeting.participant_joined',
                'meeting.participant_left',
                'meeting.ended',
                'meeting.started'
            ]:
                # Process the webhook
                AttendanceService.process_zoom_webhook(webhook_data)
                
                # Additional real-time processing for enhanced features
                if event_type == 'meeting.started':
                    meeting_id = str(webhook_data['payload']['object']['id'])
                    try:
                        live_class = LiveClass.objects.get(zoom_meeting_id=meeting_id)
                        live_class.status = 'live'
                        live_class.save()
                        
                        # Broadcast meeting started
                        from apps.classes.websocket_service import broadcast_class_status_update
                        broadcast_class_status_update(
                            str(live_class.id),
                            'live',
                            {
                                'meeting_started': True,
                                'start_time': timezone.now().isoformat()
                            }
                        )
                    except LiveClass.DoesNotExist:
                        pass
            
            return HttpResponse(status=200)
            
        except Exception as e:
            return HttpResponse(status=400)


class ZoomMeetingView(APIView):
    """Manage Zoom meetings for live classes"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, live_class_id):
        """Create Zoom meeting for live class"""
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check permissions
            if (live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            zoom_service = ZoomService()
            meeting_info = zoom_service.create_meeting(live_class)
            
            return Response({
                'message': 'Zoom meeting created successfully',
                'meeting_info': meeting_info
            })
            
        except LiveClass.DoesNotExist:
            return Response(
                {'error': 'Live class not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, live_class_id):
        """Update Zoom meeting for live class"""
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check permissions
            if (live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            zoom_service = ZoomService()
            zoom_service.update_meeting(live_class)
            
            return Response({'message': 'Zoom meeting updated successfully'})
            
        except LiveClass.DoesNotExist:
            return Response(
                {'error': 'Live class not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )