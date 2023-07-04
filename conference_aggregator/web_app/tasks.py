from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone


@shared_task
def send_upcoming_events_email():
    user = get_user_model()
    users = user.objects.filter(
        myappuser__favorite_events__date_time__lte=timezone.now() + timezone.timedelta(weeks=2)).distinct()

    for user in users:
        favorite_events = user.myappuser.favorite_events.filter(
            date_time__lte=timezone.now() + timezone.timedelta(weeks=2))
        if favorite_events.exists():
            email_subject = "Upcoming Events Notification"
            email_body = "You have upcoming events within the next 2 weeks:\n\n"

            for event in favorite_events:
                email_body += f"- {event.event_title}\n"  # Customize the email body as needed

            send_mail(email_subject, email_body, user.email, [user.email])
