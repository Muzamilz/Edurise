from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Testimonial, TeamMember, Announcement, FAQ, ContactInfo

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for public display"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'first_name', 'last_name']


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonials"""
    user = UserBasicSerializer(read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'user', 'content', 'rating', 'status', 'featured',
            'position', 'company', 'course_title', 'submitted_at',
            'approved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'approved_at', 'created_at', 'updated_at']


class TestimonialCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating testimonials"""
    
    class Meta:
        model = Testimonial
        fields = ['content', 'rating', 'position', 'company', 'course']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TestimonialPublicSerializer(serializers.ModelSerializer):
    """Public serializer for testimonials (limited fields)"""
    user_name = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'user_name', 'content', 'rating', 'position', 
            'company', 'course_title', 'created_at'
        ]
    
    def get_user_name(self, obj):
        """Get user's display name"""
        return obj.user.get_full_name() or obj.user.username


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team members"""
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'name', 'role', 'department', 'bio', 'profile_image',
            'email', 'linkedin_url', 'twitter_url', 'status', 'display_order',
            'featured', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeamMemberPublicSerializer(serializers.ModelSerializer):
    """Public serializer for team members (limited fields)"""
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'name', 'role', 'department', 'bio', 'profile_image',
            'linkedin_url', 'twitter_url'
        ]


class AnnouncementSerializer(serializers.ModelSerializer):
    """Serializer for announcements"""
    author = UserBasicSerializer(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'category', 'priority', 'status',
            'publish_at', 'expire_at', 'featured', 'show_on_homepage',
            'send_notification', 'author', 'tags', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_published', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class AnnouncementPublicSerializer(serializers.ModelSerializer):
    """Public serializer for announcements"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'category', 'priority',
            'publish_at', 'expire_at', 'featured', 'author_name',
            'tags', 'created_at'
        ]


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQs"""
    author = UserBasicSerializer(read_only=True)
    helpfulness_ratio = serializers.FloatField(read_only=True)
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'category', 'status', 'display_order',
            'featured', 'view_count', 'helpful_count', 'not_helpful_count',
            'helpfulness_ratio', 'author', 'keywords', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'view_count', 'helpful_count', 'not_helpful_count',
            'helpfulness_ratio', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class FAQPublicSerializer(serializers.ModelSerializer):
    """Public serializer for FAQs"""
    helpfulness_ratio = serializers.FloatField(read_only=True)
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'category', 'view_count',
            'helpful_count', 'not_helpful_count', 'helpfulness_ratio'
        ]


class FAQFeedbackSerializer(serializers.Serializer):
    """Serializer for FAQ feedback"""
    helpful = serializers.BooleanField()


class ContactInfoSerializer(serializers.ModelSerializer):
    """Serializer for contact information"""
    
    class Meta:
        model = ContactInfo
        fields = [
            'id', 'company_name', 'tagline', 'description', 'email', 'phone',
            'address', 'business_hours', 'facebook_url', 'twitter_url',
            'linkedin_url', 'instagram_url', 'youtube_url', 'blog_url',
            'support_url', 'privacy_policy_url', 'terms_of_service_url',
            'emergency_contact', 'version', 'updated_at'
        ]
        read_only_fields = ['id', 'version', 'updated_at']


class ContactInfoPublicSerializer(serializers.ModelSerializer):
    """Public serializer for contact information"""
    
    class Meta:
        model = ContactInfo
        fields = [
            'company_name', 'tagline', 'description', 'email', 'phone',
            'address', 'business_hours', 'facebook_url', 'twitter_url',
            'linkedin_url', 'instagram_url', 'youtube_url', 'blog_url',
            'support_url', 'privacy_policy_url', 'terms_of_service_url'
        ]