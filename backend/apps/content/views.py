from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, F
from apps.common.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .models import Testimonial, TeamMember, Announcement, FAQ, ContactInfo
from .serializers import (
    TestimonialSerializer, TestimonialCreateSerializer, TestimonialPublicSerializer,
    TeamMemberSerializer, TeamMemberPublicSerializer,
    AnnouncementSerializer, AnnouncementPublicSerializer,
    FAQSerializer, FAQPublicSerializer, FAQFeedbackSerializer,
    ContactInfoSerializer, ContactInfoPublicSerializer
)
# from .filters import TestimonialFilter, AnnouncementFilter, FAQFilter


class TestimonialViewSet(viewsets.ModelViewSet):
    """ViewSet for managing testimonials"""
    queryset = Testimonial.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = TestimonialFilter
    search_fields = ['content', 'position', 'company', 'user__username']
    ordering_fields = ['created_at', 'rating', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TestimonialCreateSerializer
        elif self.action == 'list' and not self.request.user.is_staff:
            return TestimonialPublicSerializer
        return TestimonialSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Testimonial.objects.all()
        else:
            # Public users only see published testimonials
            return Testimonial.objects.filter(status='published')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured testimonials"""
        testimonials = self.get_queryset().filter(featured=True)[:6]
        serializer = TestimonialPublicSerializer(testimonials, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a testimonial"""
        testimonial = self.get_object()
        testimonial.status = 'published'
        testimonial.approved_by = request.user
        testimonial.approved_at = timezone.now()
        testimonial.save()
        
        serializer = self.get_serializer(testimonial)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a testimonial"""
        testimonial = self.get_object()
        testimonial.status = 'rejected'
        testimonial.save()
        
        serializer = self.get_serializer(testimonial)
        return Response(serializer.data)


class TeamMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for managing team members"""
    queryset = TeamMember.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'status', 'featured']
    search_fields = ['name', 'role', 'bio']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return TeamMemberPublicSerializer
        return TeamMemberSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return TeamMember.objects.all()
        else:
            # Public users only see published team members
            return TeamMember.objects.filter(status='published')
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get team members grouped by department"""
        departments = {}
        queryset = self.get_queryset().filter(status='published')
        
        for member in queryset:
            dept = member.get_department_display()
            if dept not in departments:
                departments[dept] = []
            departments[dept].append(TeamMemberPublicSerializer(member).data)
        
        return Response(departments)


class AnnouncementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing announcements"""
    queryset = Announcement.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = AnnouncementFilter
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['publish_at', 'created_at', 'priority']
    ordering = ['-publish_at', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return AnnouncementPublicSerializer
        return AnnouncementSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Announcement.objects.all()
        else:
            # Public users only see published announcements
            now = timezone.now()
            return Announcement.objects.filter(
                status='published',
                publish_at__lte=now
            ).filter(
                Q(expire_at__isnull=True) | Q(expire_at__gt=now)
            )
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured announcements"""
        announcements = self.get_queryset().filter(featured=True)[:5]
        serializer = AnnouncementPublicSerializer(announcements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def homepage(self, request):
        """Get announcements for homepage"""
        announcements = self.get_queryset().filter(show_on_homepage=True)[:3]
        serializer = AnnouncementPublicSerializer(announcements, many=True)
        return Response(serializer.data)


class FAQViewSet(viewsets.ModelViewSet):
    """ViewSet for managing FAQs"""
    queryset = FAQ.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = FAQFilter
    search_fields = ['question', 'answer', 'keywords']
    ordering_fields = ['display_order', 'view_count', 'helpful_count', 'created_at']
    ordering = ['category', 'display_order', 'question']
    
    def get_serializer_class(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return FAQPublicSerializer
        return FAQSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['feedback']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return FAQ.objects.all()
        else:
            # Public users only see published FAQs
            return FAQ.objects.filter(status='published')
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment view count"""
        instance = self.get_object()
        # Increment view count for public users
        if not request.user.is_staff:
            FAQ.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
            instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured FAQs"""
        faqs = self.get_queryset().filter(featured=True)[:10]
        serializer = FAQPublicSerializer(faqs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get FAQs grouped by category"""
        categories = {}
        queryset = self.get_queryset().filter(status='published')
        
        for faq in queryset:
            category = faq.get_category_display()
            if category not in categories:
                categories[category] = []
            categories[category].append(FAQPublicSerializer(faq).data)
        
        return Response(categories)
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """Submit feedback for an FAQ"""
        faq = self.get_object()
        serializer = FAQFeedbackSerializer(data=request.data)
        
        if serializer.is_valid():
            if serializer.validated_data['helpful']:
                FAQ.objects.filter(pk=faq.pk).update(helpful_count=F('helpful_count') + 1)
            else:
                FAQ.objects.filter(pk=faq.pk).update(not_helpful_count=F('not_helpful_count') + 1)
            
            return Response({'message': 'Feedback recorded successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactInfoViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contact information"""
    queryset = ContactInfo.objects.all()
    ordering = ['-is_active', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return ContactInfoPublicSerializer
        return ContactInfoSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ContactInfo.objects.all()
        else:
            # Public users only see active contact info
            return ContactInfo.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the active contact information"""
        contact_info = ContactInfo.get_active()
        if contact_info:
            serializer = ContactInfoPublicSerializer(contact_info)
            return Response(serializer.data)
        return Response({'message': 'No active contact information found'}, 
                       status=status.HTTP_404_NOT_FOUND)