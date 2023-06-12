from django.urls import path
from .views import home, index, search_view, event_details, my_events


urlpatterns = [
    path('', home, name='home'),
    path('event-list/', index, name='event-list'),
    path('search/', search_view, name='search'),
    path('events/<int:event_id>/', event_details, name='event_details'),
    path('my-events/', my_events, name='my_events'),
]
