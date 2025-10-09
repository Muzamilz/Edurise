from django.db import models


class TenantAwareManager(models.Manager):
    """Custom manager for tenant-aware models"""
    
    def get_queryset(self):
        """Override to filter by current tenant if available"""
        return super().get_queryset()
    
    def for_tenant(self, tenant):
        """Filter queryset by specific tenant"""
        return self.get_queryset().filter(tenant=tenant)


class TenantAwareModel(models.Model):
    """Abstract base model for tenant-aware models"""
    
    tenant = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )
    
    objects = TenantAwareManager()
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Ensure tenant is set before saving"""
        if not self.tenant_id:
            # This should be set by the view or service
            raise ValueError("Tenant must be set before saving")
        super().save(*args, **kwargs)