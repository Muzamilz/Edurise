from django.urls import path

# All ViewSets for this app are registered in apps/api/urls.py
# This file is reserved for custom non-ViewSet endpoints only

app_name = 'content'

urlpatterns = [
    # Custom non-ViewSet endpoints can be added here if needed
    # Example:
    # path('custom-endpoint/', CustomView.as_view(), name='custom-endpoint'),
]