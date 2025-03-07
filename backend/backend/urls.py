from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/', include('api.urls')),  # Include API routes
    path('admin/', admin.site.urls),    # Admin panel
]

