from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FileCategory, FileUpload, FileAccessLog, FileProcessingJob

User = get_user_model()


class FileCategorySerializer(serializers.ModelSerializer):
    """Serializer for file categories"""
    
    class Meta:
        model = FileCategory
        fields = [
            'name', 'display_name', 'allowed_extensions', 
            'max_file_size_mb', 'description'
        ]


class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file uploads with metadata"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    secure_url = serializers.SerializerMethodField()
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'original_filename', 'file', 'file_size', 'file_size_mb',
            'file_type', 'file_extension', 'category', 'category_name',
            'title', 'description', 'tags', 'uploaded_by', 'uploaded_by_name',
            'uploaded_by_email', 'access_level', 'course', 'course_title',
            'status', 'download_count', 'last_accessed', 'created_at',
            'updated_at', 'expires_at', 'is_image', 'is_video', 'is_document',
            'is_expired', 'secure_url'
        ]
        read_only_fields = [
            'id', 'file_size', 'file_type', 'file_extension', 'uploaded_by',
            'download_count', 'last_accessed', 'created_at', 'updated_at'
        ]
    
    def get_secure_url(self, obj):
        """Get secure URL for file access"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.can_access(request.user):
                return obj.get_secure_url()
        return None
    
    def validate_file(self, value):
        """Validate uploaded file"""
        if not value:
            raise serializers.ValidationError("File is required")
        
        # Get category from validated data or instance
        category = self.validated_data.get('category') or getattr(self.instance, 'category', None)
        
        if category:
            # Check file size
            max_size_bytes = category.max_file_size_mb * 1024 * 1024
            if value.size > max_size_bytes:
                raise serializers.ValidationError(
                    f"File size exceeds maximum allowed size of {category.max_file_size_mb}MB"
                )
            
            # Check file extension
            if category.allowed_extensions:
                file_ext = value.name.split('.')[-1].lower()
                if file_ext not in category.allowed_extensions:
                    raise serializers.ValidationError(
                        f"File type '{file_ext}' not allowed. Allowed types: {', '.join(category.allowed_extensions)}"
                    )
        
        return value
    
    def create(self, validated_data):
        """Create file upload with proper metadata"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user
            validated_data['tenant'] = request.user.tenant
        
        # Set original filename
        file_obj = validated_data.get('file')
        if file_obj and not validated_data.get('original_filename'):
            validated_data['original_filename'] = file_obj.name
        
        return super().create(validated_data)


class FileUploadCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for file upload creation"""
    
    class Meta:
        model = FileUpload
        fields = [
            'file', 'category', 'title', 'description', 'tags',
            'access_level', 'course', 'expires_at'
        ]
    
    def validate_file(self, value):
        """Validate uploaded file"""
        if not value:
            raise serializers.ValidationError("File is required")
        return value
    
    def create(self, validated_data):
        """Create file upload with metadata extraction"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user
            validated_data['tenant'] = request.user.tenant
        
        # Set original filename from uploaded file
        file_obj = validated_data.get('file')
        if file_obj:
            validated_data['original_filename'] = file_obj.name
        
        return super().create(validated_data)


class FileAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for file access logs"""
    
    file_name = serializers.CharField(source='file.original_filename', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = FileAccessLog
        fields = [
            'id', 'file', 'file_name', 'user', 'user_email',
            'ip_address', 'user_agent', 'accessed_at'
        ]
        read_only_fields = ['id', 'accessed_at']


class FileProcessingJobSerializer(serializers.ModelSerializer):
    """Serializer for file processing jobs"""
    
    file_name = serializers.CharField(source='file.original_filename', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = FileProcessingJob
        fields = [
            'id', 'file', 'file_name', 'job_type', 'status',
            'parameters', 'result_data', 'error_message',
            'started_at', 'completed_at', 'created_at', 'duration_seconds'
        ]
        read_only_fields = [
            'id', 'started_at', 'completed_at', 'created_at'
        ]
    
    def get_duration_seconds(self, obj):
        """Calculate job duration in seconds"""
        if obj.started_at and obj.completed_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None


class FileUploadListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for file listing"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'original_filename', 'title', 'file_size_mb',
            'file_type', 'category_name', 'uploaded_by_name',
            'access_level', 'status', 'download_count', 'created_at'
        ]


class FileUploadUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating file metadata"""
    
    class Meta:
        model = FileUpload
        fields = [
            'title', 'description', 'tags', 'access_level',
            'expires_at', 'status'
        ]
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance and self.instance.status == 'deleted':
            raise serializers.ValidationError("Cannot modify deleted files")
        return value