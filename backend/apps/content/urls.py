from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TestimonialViewSet, TeamMemberViewSet, AnnouncementViewSet,
    FAQViewSet, ContactInfoViewSet
)

router = DefaultRouter()
router.register(r'testimonials', TestimonialViewSet)
router.register(r'team-members', TeamMemberViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'contact-info', ContactInfoViewSet)

app_name = 'content'

urlpatterns = [
    path('', include(router.urls)),
]