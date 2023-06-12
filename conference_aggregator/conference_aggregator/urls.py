"""
URL configuration for conference_aggregator project.
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("web_app.urls")),
    path('members/', include('django.contrib.auth.urls')),
    path('members/', include("authentication_app.urls")),
]
