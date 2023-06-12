from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import EventsTb, MyAppUser
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Packages for Google Calendar API
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Generate PDF report file
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = 'http://localhost:8080/'
API_KEY = 'AIzaSyAeOyENMYYHiNdakfNtWKXryd6EP290CF0'


def add_to_google_calendar(request, event):
    creds = None
    user_email = request.user.email
    token_file = f"token_{user_email}.json"
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES, redirect_uri=REDIRECT_URI)
            creds = flow.run_local_server(port=8080)

        with open(token_file, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds, developerKey=API_KEY)
        print(event.date_time)
        event_data = {
            'summary': str(event.event_title),
            'location': str(event.location),
            'description': str(event.topics),
            'colorId': 6,
            'start': {
                'dateTime': str(event.date_time) + 'T10:00:00Z',
                'timeZone': "Europe/Bucharest",
            },
            'end': {
                'dateTime': str(event.date_time) + 'T17:00:00Z',
                'timeZone': "Europe/Bucharest",
            },
        }
        event = service.events().insert(calendarId=user_email, body=event_data).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except HttpError as error:
        print("An error occurred:", error)


@login_required(login_url='login')
def event_details(request, event_id):
    event = get_object_or_404(EventsTb, pk=event_id)
    user = request.user.myappuser
    if request.method == 'POST':
        if 'add_to_favorites' in request.POST:
            user.favorite_events.add(event)
        elif 'add_to_calendar' in request.POST:
            add_to_google_calendar(request, event)

    context = {
        'event': event
    }
    return render(request, 'events/event_details.html', context)


def home(request):
    selected_topic = request.GET.get('topic')
    events = EventsTb.objects.all().order_by('date_time')
    topics = EventsTb.objects.values_list('topics', flat=True).distinct()

    if selected_topic:
        events = events.filter(topics__icontains=selected_topic)
        topics = topics.filter(topics__icontains=selected_topic)

    paginator = Paginator(events, 10)
    page = request.GET.get('page')
    events_page = paginator.get_page(page)

    now = timezone.now()
    nearest_events = events.filter(date_time__gte=now)[:6]
    nearest_events_romania = events.filter(date_time__gte=now, location__icontains='Romania')[:6]
    nearest_events_tech = events.filter(date_time__gte=now, topics__icontains='Tech')[:6]
    context = {
        'events': events_page,
        'topics': topics,
        'selected_topic': selected_topic,
        'nearest_events': nearest_events,
        'nearest_events_romania': nearest_events_romania,
        'nearest_events_tech': nearest_events_tech
    }
    return render(request, 'events/home.html', context)


def index(request):
    selected_topic = request.GET.get('topic')
    events = EventsTb.objects.all().order_by('date_time')
    topics = EventsTb.objects.values_list('topics', flat=True).distinct()

    if selected_topic:
        events = events.filter(topics__icontains=selected_topic)
        topics = topics.filter(topics__icontains=selected_topic)
        print("Filtered Events:", events)

    paginator = Paginator(events, 10)
    page = request.GET.get('page')
    events_page = paginator.get_page(page)
    context = {
        'events': events_page,
        'topics': topics,
        'selected_topic': selected_topic
    }
    return render(request, 'events/event_list.html', context)


def search_view(request):
    search_query = request.GET.get('search_query', '')
    multiple_queries = Q(Q(event_title__icontains=search_query) | Q(location__icontains=search_query))
    events = EventsTb.objects.filter(multiple_queries).order_by('date_time')

    paginator = Paginator(events, 10)
    page = request.GET.get('page')
    events_page = paginator.get_page(page)
    context = {
        'events': events_page,
        'search_query': search_query,
    }
    return render(request, 'events/search_results.html', context)


def generate_pdf(events):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Set up the PDF content
    pdf.setTitle('My Events')
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(230, 800, 'My Events')
    pdf.setFont('Helvetica', 12)
    y = 750

    # Add event information to the PDF
    for event in events:
        pdf.setFont('Helvetica-Bold', 16)
        pdf.drawString(80, y, f'Event Title: {event.event_title}')
        pdf.setFont('Helvetica', 12)
        pdf.drawString(80, y - 20, f'Date: {event.date_time}')
        pdf.drawString(80, y - 40, f'Call for papers Date: {event.call_for_papers_date}')
        pdf.drawString(80, y - 60, f'Location: {event.location}')
        pdf.drawString(80, y - 80, f'Event Web Page: {event.event_url}')
        # Add more event details as needed
        y -= 100

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer


@login_required
def my_events(request):
    user = request.user
    try:
        my_app_user = user.myappuser
    except MyAppUser.DoesNotExist:
        my_app_user = None

    if my_app_user:
        favorite_events = my_app_user.favorite_events.all()
        paginator = Paginator(favorite_events, 5)
        page = request.GET.get('page')
        events_page = paginator.get_page(page)
    else:
        favorite_events = []

    if request.method == 'POST' and 'generate_pdf' in request.POST:
        # Generate the PDF file
        pdf_file = generate_pdf(favorite_events)

        # Prepare the HTTP response with the PDF file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="my_events.pdf"'
        response.write(pdf_file.getvalue())
        return response
    elif request.method == 'POST':
        # Handle unfavorite event action
        event_id = request.POST.get('event_id')
        if event_id:
            event = get_object_or_404(EventsTb, pk=event_id)
            if my_app_user and event in my_app_user.favorite_events.all():
                my_app_user.favorite_events.remove(event)

    context = {
        'favorite_events': events_page
    }
    return render(request, 'events/my_events.html', context)
