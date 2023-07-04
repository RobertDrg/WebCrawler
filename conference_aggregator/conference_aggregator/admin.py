from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from .crawler_utils import start_crawler


class ConferenceAggregatorAdminSite(admin.AdminSite):
    index_template = 'admin/index.html'

    def get_urls(self):
        urls = super().get_urls()
        return urls + [
            path('startwebcrawler/', self.startwebcrawler, name='service-startwebcrawler')
        ]

    def startwebcrawler(self, request):
        start_crawler()
        return HttpResponse("Web crawler finished.")


admin_site = ConferenceAggregatorAdminSite(name='conferenceadmin')
admin_site._registry.update(admin.site._registry)
