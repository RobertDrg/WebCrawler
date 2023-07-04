"""
URL configuration for conference_aggregator project.
"""
from django.urls import path, include, re_path
from conference_aggregator.admin import admin_site


urlpatterns = [
    path('admin/startwebcrawler/', admin_site.startwebcrawler, name='service-startwebcrawler'),
    re_path('^admin/', admin_site.urls),
    path('', include("web_app.urls")),
    path('members/', include('django.contrib.auth.urls')),
    path('members/', include("authentication_app.urls")),
]
