import django_filters
from django.db.models import Q
from .models import Testimonial, Announcement, FAQ


class TestimonialFilter(django_filters.FilterSet):
    """Filter for testimonials"""
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    course = django_filters.CharFilter(field_name='course__slug', lookup_expr='iexact')
    featured = django_filters.BooleanFilter(field_name='featured')
    status = django_filters.ChoiceFilter(choices=Testimonial.STATUS_CHOICES)
    
    class Meta:
        model = Testimonial
        fields = ['rating_min', 'rating_max', 'course', 'featured', 'status']


class AnnouncementFilter(django_filters.FilterSet):
    """Filter for announcements"""
    category = django_filters.ChoiceFilter(choices=Announcement.CATEGORY_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Announcement.PRIORITY_CHOICES)
    status = django_filters.ChoiceFilter(choices=Announcement.STATUS_CHOICES)
    featured = django_filters.BooleanFilter(field_name='featured')
    show_on_homepage = django_filters.BooleanFilter(field_name='show_on_homepage')
    date_from = django_filters.DateTimeFilter(field_name='publish_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='publish_at', lookup_expr='lte')
    
    class Meta:
        model = Announcement
        fields = ['category', 'priority', 'status', 'featured', 'show_on_homepage', 'date_from', 'date_to']


class FAQFilter(django_filters.FilterSet):
    """Filter for FAQs"""
    category = django_filters.ChoiceFilter(choices=FAQ.CATEGORY_CHOICES)
    status = django_filters.ChoiceFilter(choices=FAQ.STATUS_CHOICES)
    featured = django_filters.BooleanFilter(field_name='featured')
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = FAQ
        fields = ['category', 'status', 'featured', 'search']
    
    def filter_search(self, queryset, name, value):
        """Custom search filter for question and answer"""
        return queryset.filter(
            Q(question__icontains=value) | 
            Q(answer__icontains=value) |
            Q(keywords__icontains=value)
        )