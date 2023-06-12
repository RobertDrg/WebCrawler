from django.db import models
from datetime import date
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

    @property
    def days_till(self):
        today = date.today()
        days_till = self.date_time.date() - today
        days_till_stripped = str(days_till).split(",", 1)[0]
        return days_till_stripped

    @property
    def has_passed(self):
        today = date.today()
        if self.date_time.date() < today:
            thing = "Past"
        else:
            thing = "Future"
        return thing
