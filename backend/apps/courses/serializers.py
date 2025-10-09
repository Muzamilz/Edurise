from rest_framework import serializers
from .models import Course, LiveClass, CourseModule, CourseReview, CourseLicense, Enrollment


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_enrollments = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor', 'instructor_name',
            'category', 'tags', 'thumbnail', 'price', 'is_public',
            'max_students', 'duration_weeks', 'difficulty_level',
            'average_rating', 'total_enrollments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'instructor', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set instructor to current user
        validated_data['instructor'] = self.context['request'].user
        # Set tenant from request
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)


class LiveClassSerializer(serializers.ModelSerializer):
    """Serializer for LiveClass model"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = LiveClass
        fields = [
            'id', 'course', 'course_title', 'title', 'description',
            'scheduled_at', 'duration_minutes', 'status',
            'zoom_meeting_id', 'join_url', 'start_url', 'password',
            'recording_url', 'recording_password', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'zoom_meeting_id', 'join_url', 'start_url', 
            'recording_url', 'created_at', 'updated_at'
        ]


class CourseModuleSerializer(serializers.ModelSerializer):
    """Serializer for CourseModule model"""
    
    class Meta:
        model = CourseModule
        fields = [
            'id', 'course', 'title', 'description', 'content',
            'order', 'is_published', 'video_url', 'materials',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseReviewSerializer(serializers.ModelSerializer):
    """Serializer for CourseReview model"""
    
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = CourseReview
        fields = [
            'id', 'course', 'student', 'student_name', 'rating',
            'comment', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student', 'is_approved', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class CourseLicenseSerializer(serializers.ModelSerializer):
    """Serializer for CourseLicense model"""
    
    class Meta:
        model = CourseLicense
        fields = [
            'id', 'course', 'license_type', 'terms', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'course', 'course_title',
            'status', 'progress_percentage', 'enrolled_at', 'completed_at',
            'last_accessed'
        ]
        read_only_fields = [
            'id', 'student', 'enrolled_at', 'completed_at', 'last_accessed'
        ]
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)


class CourseDetailSerializer(CourseSerializer):
    """Detailed serializer for Course with related data"""
    
    modules = CourseModuleSerializer(many=True, read_only=True)
    live_classes = LiveClassSerializer(many=True, read_only=True)
    reviews = CourseReviewSerializer(many=True, read_only=True)
    license = CourseLicenseSerializer(read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + [
            'modules', 'live_classes', 'reviews', 'license'
        ]