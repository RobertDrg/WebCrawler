from django.db import models
from django.contrib.auth.models import User


class MyAppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class EventsTb(models.Model):
    event_url = models.TextField(blank=True, null=True)
    event_title = models.TextField(blank=True, null=True)
    date_time = models.TextField(blank=True, null=True)
    call_for_papers_date = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    favorites = models.ManyToManyField(MyAppUser, related_name='favorite_events', blank=True)
    topics = models.TextField(blank=True, null=True)
    hash = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'events_tb'
