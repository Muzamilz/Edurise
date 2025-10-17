from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from .responses import StandardAPIResponse, APIResponseMixin


class TenantFilterMixin:
    """
    Mixin to automatically filter querysets by tenant.
    """
    
    def get_queryset(self):
        """Filter queryset by tenant if available"""
        queryset = super().get_queryset()
        
        if hasattr(self.request, 'tenant') and self.request.tenant:
            # Check if model has tenant field
            if hasattr(queryset.model, 'tenant'):
                queryset = queryset.filter(tenant=self.request.tenant)
        
        return queryset
    
    def perform_create(self, serializer):
        """Automatically set tenant when creating objects"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            if hasattr(serializer.Meta.model, 'tenant'):
                serializer.save(tenant=self.request.tenant)
            else:
                serializer.save()
        else:
            serializer.save()


class OptimizedQueryMixin:
    """
    Mixin for optimized database queries with select_related and prefetch_related.
    """
    select_related_fields = []
    prefetch_related_fields = []
    
    def get_queryset(self):
        """Apply query optimizations"""
        queryset = super().get_queryset()
        
        # Apply select_related for foreign keys
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        
        # Apply prefetch_related for many-to-many and reverse foreign keys
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        
        return queryset


class DashboardMixin:
    """
    Mixin to add common dashboard functionality to ViewSets.
    """
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for the current model"""
        queryset = self.get_queryset()
        
        # Basic statistics
        stats = {
            'total_count': queryset.count(),
            'created_today': queryset.filter(
                created_at__date=timezone.now().date()
            ).count() if hasattr(queryset.model, 'created_at') else 0,
            'created_this_week': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count() if hasattr(queryset.model, 'created_at') else 0,
            'created_this_month': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count() if hasattr(queryset.model, 'created_at') else 0,
        }
        
        return StandardAPIResponse.success(
            data=stats,
            message=f"{self.queryset.model.__name__} dashboard statistics"
        )


class BulkActionMixin:
    """
    Mixin to add bulk actions to ViewSets.
    """
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple objects at once"""
        if not isinstance(request.data, list):
            return StandardAPIResponse.validation_error(
                errors={'non_field_errors': ['Expected a list of objects']},
                message="Bulk create requires a list of objects"
            )
        
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            self.perform_bulk_create(serializer)
            return StandardAPIResponse.success(
                data=serializer.data,
                message=f"Successfully created {len(serializer.data)} objects",
                status_code=status.HTTP_201_CREATED
            )
        
        return StandardAPIResponse.validation_error(
            errors=serializer.errors,
            message="Validation failed for bulk create"
        )
    
    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        """Update multiple objects at once"""
        ids = request.data.get('ids', [])
        update_data = request.data.get('data', {})
        
        if not ids:
            return StandardAPIResponse.validation_error(
                errors={'ids': ['This field is required']},
                message="IDs are required for bulk update"
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        updated_count = queryset.update(**update_data)
        
        return StandardAPIResponse.success(
            data={'updated_count': updated_count},
            message=f"Successfully updated {updated_count} objects"
        )
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Delete multiple objects at once"""
        ids = request.data.get('ids', [])
        
        if not ids:
            return StandardAPIResponse.validation_error(
                errors={'ids': ['This field is required']},
                message="IDs are required for bulk delete"
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        deleted_count, _ = queryset.delete()
        
        return StandardAPIResponse.success(
            data={'deleted_count': deleted_count},
            message=f"Successfully deleted {deleted_count} objects"
        )
    
    def perform_bulk_create(self, serializer):
        """Perform bulk create with tenant awareness"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            serializer.save(tenant=self.request.tenant)
        else:
            serializer.save()


class AnalyticsMixin:
    """
    Mixin to add analytics functionality to ViewSets.
    """
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get analytics for the current model"""
        queryset = self.get_queryset()
        
        # Time-based analytics
        now = timezone.now()
        analytics = {
            'total_count': queryset.count(),
            'trends': {
                'daily': self.get_daily_trend(queryset, days=30),
                'weekly': self.get_weekly_trend(queryset, weeks=12),
                'monthly': self.get_monthly_trend(queryset, months=6)
            }
        }
        
        # Add model-specific analytics
        if hasattr(self, 'get_custom_analytics'):
            analytics.update(self.get_custom_analytics(queryset))
        
        return StandardAPIResponse.success(
            data=analytics,
            message=f"{self.queryset.model.__name__} analytics"
        )
    
    def get_daily_trend(self, queryset, days=30):
        """Get daily trend data"""
        if not hasattr(queryset.model, 'created_at'):
            return []
        
        trend_data = []
        for i in range(days):
            date = timezone.now().date() - timezone.timedelta(days=i)
            count = queryset.filter(created_at__date=date).count()
            trend_data.append({
                'date': date.isoformat(),
                'count': count
            })
        
        return list(reversed(trend_data))
    
    def get_weekly_trend(self, queryset, weeks=12):
        """Get weekly trend data"""
        if not hasattr(queryset.model, 'created_at'):
            return []
        
        trend_data = []
        for i in range(weeks):
            week_start = timezone.now().date() - timezone.timedelta(weeks=i)
            week_end = week_start + timezone.timedelta(days=6)
            count = queryset.filter(
                created_at__date__gte=week_start,
                created_at__date__lte=week_end
            ).count()
            trend_data.append({
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'count': count
            })
        
        return list(reversed(trend_data))
    
    def get_monthly_trend(self, queryset, months=6):
        """Get monthly trend data"""
        if not hasattr(queryset.model, 'created_at'):
            return []
        
        trend_data = []
        for i in range(months):
            date = timezone.now().replace(day=1) - timezone.timedelta(days=32*i)
            month_start = date.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timezone.timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timezone.timedelta(days=1)
            
            count = queryset.filter(
                created_at__date__gte=month_start.date(),
                created_at__date__lte=month_end.date()
            ).count()
            
            trend_data.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        return list(reversed(trend_data))


class ExportMixin:
    """
    Mixin to add data export functionality to ViewSets.
    """
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export data in various formats"""
        export_format = request.query_params.get('format', 'json')
        
        if export_format not in ['json', 'csv']:
            return StandardAPIResponse.validation_error(
                errors={'format': ['Supported formats: json, csv']},
                message="Invalid export format"
            )
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if export_format == 'json':
            serializer = self.get_serializer(queryset, many=True)
            return StandardAPIResponse.success(
                data=serializer.data,
                message=f"Exported {len(serializer.data)} records as JSON"
            )
        
        elif export_format == 'csv':
            # For CSV export, you might want to use a different serializer
            # or implement custom CSV generation logic
            return StandardAPIResponse.success(
                data={'message': 'CSV export not yet implemented'},
                message="CSV export feature coming soon"
            )


class StandardViewSetMixin(
    APIResponseMixin,
    TenantFilterMixin,
    OptimizedQueryMixin,
    DashboardMixin,
    BulkActionMixin,
    AnalyticsMixin,
    ExportMixin
):
    """
    Combined mixin with all standard API functionality.
    Use this mixin to get all common API features in your ViewSets.
    """
    pass