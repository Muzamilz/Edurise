from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import ClassAttendance
from .services import ZoomService, AttendanceService
from apps.courses.models import LiveClass


class ClassAttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for ClassAttendance model"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter attendance by tenant"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return ClassAttendance.objects.filter(
                live_class__course__tenant=self.request.tenant
            )
        return ClassAttendance.objects.none()
    
    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        """Mark attendance for a live class"""
        live_class_id = request.data.get('live_class_id')
        student_id = request.data.get('student_id')
        status = request.data.get('status', 'present')
        
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check permissions
            if (live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            student = User.objects.get(id=student_id)
            
            attendance = AttendanceService.mark_attendance(
                live_class=live_class,
                student=student,
                status=status
            )
            
            return Response({
                'message': 'Attendance marked successfully',
                'attendance_id': attendance.id
            })
            
        except (LiveClass.DoesNotExist, User.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def class_report(self, request):
        """Get attendance report for a live class"""
        live_class_id = request.query_params.get('live_class_id')
        
        if not live_class_id:
            return Response(
                {'error': 'live_class_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check permissions
            if (live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get engagement metrics
            metrics = AttendanceService.calculate_engagement_metrics(live_class)
            
            # Get individual attendance records
            attendances = live_class.attendances.all()
            attendance_data = []
            
            for attendance in attendances:
                attendance_data.append({
                    'student_name': attendance.student.get_full_name(),
                    'student_email': attendance.student.email,
                    'status': attendance.status,
                    'join_time': attendance.join_time,
                    'leave_time': attendance.leave_time,
                    'duration_minutes': attendance.duration_minutes,
                    'attendance_percentage': attendance.attendance_percentage,
                    'participation_score': attendance.participation_score
                })
            
            return Response({
                'live_class': {
                    'id': live_class.id,
                    'title': live_class.title,
                    'scheduled_at': live_class.scheduled_at,
                    'duration_minutes': live_class.duration_minutes
                },
                'metrics': metrics,
                'attendances': attendance_data
            })
            
        except LiveClass.DoesNotExist:
            return Response(
                {'error': 'Live class not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update attendance records"""
        live_class_id = request.data.get('live_class_id')
        attendance_data = request.data.get('attendance_data', [])
        
        if not live_class_id:
            return Response(
                {'error': 'live_class_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            live_class = LiveClass.objects.get(id=live_class_id)
            
            # Check permissions
            if (live_class.course.instructor != request.user and 
                not request.user.is_staff):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            updated_attendances = []
            
            for data in attendance_data:
                student_id = data.get('student')
                if not student_id:
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
                    updated_attendances.append(attendance)
                    
                except User.DoesNotExist:
                    continue
            
            return Response({
                'message': f'Updated {len(updated_attendances)} attendance records',
                'updated_count': len(updated_attendances)
            })
            
        except LiveClass.DoesNotExist:
            return Response(
                {'error': 'Live class not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class ZoomWebhookView(APIView):
    """Handle Zoom webhooks for attendance tracking"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Process Zoom webhook events"""
        try:
            webhook_data = json.loads(request.body)
            
            # Verify webhook (in production, verify the signature)
            event_type = webhook_data.get('event')
            
            if event_type in [
                'meeting.participant_joined',
                'meeting.participant_left',
                'meeting.ended'
            ]:
                AttendanceService.process_zoom_webhook(webhook_data)
            
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