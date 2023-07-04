from urllib.parse import urlencode
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from eventscrawler.eventscrawler.items import Event
import dateparser
import re

PROXY_API_KEY = 'dccc8b17-8406-481e-9b98-549f74800bb3'


def get_proxy_url(url):
    payload = {'api_key': PROXY_API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url


class RoConferencesSpider(CrawlSpider):
    name = 'roconfcrawler'
    start_urls = ['https://codecamp.ro/confs', 'https://www.eventbrite.com/b/romania/science-and-tech/',
                  'https://softlead.ro/evenimente-it-c', 'https://softlead.ro/evenimente-it-c/2',
                  'https://softlead.ro/evenimente-it-c/3',
                  'https://conferencealerts.com/country-listing?country=Romania',
                  # 'https://www.conferencealerts.org/romania.php'
                  ]
    rules = (
        # Rule(LinkExtractor(allow=r"/romania.php?page=d+"), callback="parse_conference_alerts_org", follow=True),
        Rule(
            LinkExtractor(allow=("codecamp.ro/conferences/",
                                 "eventbrite.com/d/romania/science-and-tech--events/", "eventbrite.com/e/",
                                 "eventbrite.com/b/romania/science-and-tech/",
                                 "softlead.ro/evenimente-it-c/",
                                 "conferencealerts.com/",
                                 # "conferencealerts.org/", "conferencealerts.org/romania.php?page="
                                 ),
                          deny=("add-your-event", "promotion", "unsubscribe", "terms", "promote", "how-to-use",
                                "password", "help", "contact", "subscribe", "about", "blog", "privacy", "sitemap")),
            callback="parse_item"),
    )

    def parse_item(self, response):
        if "codecamp.ro" in response.url:
            yield from self.parse_codecamp(response)
        elif "eventbrite.com" in response.url:
            yield from self.parse_eventbrite(response)
        elif "softlead.ro" in response.url:
            yield from self.parse_softlead(response)
        elif "conferencealerts.com" in response.url:
            yield from self.parse_conferencealerts(response)
        # elif "conferencealerts.org" in response.url:
        #     yield from self.parse_conference_alerts_org(response)

    def parse_conference_alerts_org(self, response):
        start_date, start_date_day, start_date_month, start_date_year = None, None, None, None
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_title = \
            response.xpath('/html/body/div[5]/div/div[2]/div/div[2]/div/table/tbody/tr[2]/td[2]/span/strong/text()') \
                .get()
        start_date_day = str(response.xpath('//tr[2]/td[1]/div[1]/p/b/text()').get(default="not found"))
        start_date_month = str(response.xpath('//tr[2]/td[1]/div[1]/p/text()').get(default="not found"))
        start_date_year = str(response.xpath('//tr[2]/td[1]/div[1]/p/span/text()').get(default="not found"))
        call_for_papers_date = response.xpath('//tbody/tr[7]/td/span/text()').get(default="Expired")
        location = response.xpath('//table/tbody/tr[9]//span/text()').get(default="not found")
        topics = response.xpath('//tr[11]/td/span/text()[2]').get(default="not found")
        print(event_title)
        print(location)

        if location != "not found":
            location = ', '.join(location.split(',')[1:]).strip()
        if start_date_day != "not found":
            start_date_day = start_date_day.replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
            if start_date_year != "not found":
                if start_date_month != "not found":
                    start_date_month = start_date_month.replace("\n", "").replace("\t", "").strip()
                    start_date = f"{start_date_day} {start_date_month} {start_date_year}"

        event = Event()
        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = start_date if start_date else "not found"
        event['call_for_papers_date'] = call_for_papers_date
        event['location'] = location
        event['topics'] = topics

        yield event

    def parse_conferencealerts(self, response):
        start_date = f''
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_title = response.xpath('//*[@id="eventNameHeader"]/text()').get()
        date_time = str(response.xpath('//*[@id="eventDate"]/text()').get(default="not found"))
        call_for_papers_date = str(response.xpath('//div[8]/table/tbody/tr/td[3]/span[10]/text()')
                                   .get(default="Expired"))
        location = response.xpath('//*[@id="eventCountry"]/text()').get()
        topics = response.xpath('//*[@id="eventDescription"]/text()').get(default="not found").split('.')[0].strip()

        if date_time != "not found":
            pattern = r"(\b\d{1,2})(?:st|nd|rd|th)?\s+to\s+\d{1,2}(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})"
            match = re.search(pattern, date_time)
            if match:
                start_day = match.group(1)
                month = match.group(2)
                year = match.group(3)
                start_date = f"{start_day} {month} {year}"
        event = Event()
        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = start_date if start_date else date_time
        event['call_for_papers_date'] = call_for_papers_date
        event['location'] = location
        event['topics'] = topics

        yield event

    def parse_codecamp(self, response):
        event = Event()
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_title = response.xpath("//h1[@class='elementor-heading-title elementor-size-default']/text()").get()
        date_time = response.xpath("//div[@class='jet-listing-dynamic-field__content']/text()").get()
        call_for_papers_date = response.xpath("//div[@class='jet-listing-dynamic-field__content']/text()") \
            .get(default="Expired")
        location = response.xpath("//span[@class='elementor-icon-list-text']/text()").get()
        topics = 'Codecamp'

        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = date_time
        event['call_for_papers_date'] = call_for_papers_date
        event['location'] = location
        event['topics'] = topics

        yield event

    def parse_eventbrite(self, response):
        event_obj = Event()
        event_title = response.xpath('//h1[@class="event-title"]/text()').get()
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_date = response.xpath('.//time/@datetime').get(default="not found")
        call_for_papers_date = response.xpath('.//time/@datetime').get(default="Expired")
        location = \
            response.xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div[1]/div/main/div/div[1]/div[2]/div['
                           '2]/section/div[2]/section[2]/div/div/div[2]/p/strong/text()').get()
        topics = "Science & Tech"

        event_obj['event_url'] = event_url
        event_obj['event_title'] = event_title
        event_obj['date_time'] = event_date
        event_obj['call_for_papers_date'] = call_for_papers_date
        event_obj['location'] = location
        event_obj['topics'] = topics

        yield event_obj

    def parse_softlead(self, response):
        event_obj = Event()
        event_title = response.xpath('//div[2]/div/div/div/div/h1/text()').get()
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_date = response.xpath('//*[@id="content"]/div[2]/div/ul[1]/li[2]/text()[2]').get(default="not found")
        call_for_papers_date = response.xpath('//*[@id="content"]/div[2]/div/ul[1]/li[2]/text()[2]') \
            .get(default="Expired")
        location = response.xpath('//*[@id="content"]/div[2]/div/ul[1]/li[1]/text()[2]').get(default="not found")
        topics = "ITC&C"

        event_obj['event_url'] = event_url
        event_obj['event_title'] = event_title
        event_obj['date_time'] = str(dateparser.parse(event_date, languages=['ro']))
        event_obj['call_for_papers_date'] = str(dateparser.parse(call_for_papers_date, languages=['ro']))
        event_obj['location'] = location
        event_obj['topics'] = topics

        yield event_obj
