from rest_framework import serializers
from .models import Course, LiveClass, CourseModule, CourseReview, CourseLicense, Enrollment, Wishlist, CourseCategory


class CourseCategorySerializer(serializers.ModelSerializer):
    """Serializer for CourseCategory model"""
    
    subcategories = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = CourseCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'parent', 'parent_name', 'sort_order', 'is_active',
            'full_path', 'subcategories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_path', 'created_at', 'updated_at']
    
    def get_subcategories(self, obj):
        """Get subcategories if this is a parent category"""
        if obj.subcategories.exists():
            return CourseCategorySerializer(
                obj.subcategories.filter(is_active=True).order_by('sort_order', 'name'),
                many=True,
                context=self.context
            ).data
        return []


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    organization_name = serializers.CharField(source='tenant.name', read_only=True)
    category_details = CourseCategorySerializer(source='category', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_enrollments = serializers.ReadOnlyField()
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor', 'instructor_name',
            'organization_name', 'category', 'category_details', 'category_name',
            'tags', 'thumbnail', 'price', 'is_public',
            'max_students', 'duration_weeks', 'difficulty_level',
            'average_rating', 'total_enrollments', 'enrollment_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'instructor', 'created_at', 'updated_at']
    
    def get_enrollment_count(self, obj):
        """Get the enrollment count for the course"""
        return obj.enrollments.count() if hasattr(obj, 'enrollments') else 0
    
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


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_price = serializers.DecimalField(source='course.price', max_digits=10, decimal_places=2, read_only=True)
    course_instructor = serializers.CharField(source='course.instructor.get_full_name', read_only=True)
    course_category = serializers.CharField(source='course.category.name', read_only=True)
    course_difficulty = serializers.CharField(source='course.difficulty_level', read_only=True)
    course_thumbnail = serializers.ImageField(source='course.thumbnail', read_only=True)
    course_average_rating = serializers.ReadOnlyField(source='course.average_rating')
    course_total_enrollments = serializers.ReadOnlyField(source='course.total_enrollments')
    is_course_available = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()
    price_change_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'course', 'course_title', 'course_price', 'course_instructor',
            'course_category', 'course_difficulty', 'course_thumbnail', 'course_average_rating',
            'course_total_enrollments', 'priority', 'notes', 'notify_price_change',
            'notify_course_updates', 'notify_enrollment_opening', 'is_course_available',
            'is_enrolled', 'price_change_percentage', 'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'added_at', 'updated_at']
    
    def get_is_enrolled(self, obj):
        """Check if user is enrolled in the course"""
        return obj.is_enrolled()
    
    def get_price_change_percentage(self, obj):
        """Calculate price change percentage since addition to wishlist"""
        # For now, return 0 as we don't have price history tracking
        # This can be enhanced later with a price history model
        return 0
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)


class CourseDetailSerializer(CourseSerializer):
    """Detailed serializer for Course with related data"""
    
    modules = CourseModuleSerializer(many=True, read_only=True)
    live_classes = LiveClassSerializer(many=True, read_only=True)
    reviews = CourseReviewSerializer(many=True, read_only=True)
    license = CourseLicenseSerializer(read_only=True)
    is_in_wishlist = serializers.SerializerMethodField()
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + [
            'modules', 'live_classes', 'reviews', 'license', 'is_in_wishlist'
        ]
    
    def get_is_in_wishlist(self, obj):
        """Check if course is in user's wishlist"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(
                user=request.user,
                course=obj,
                tenant=getattr(request, 'tenant', None)
            ).exists()
        return False