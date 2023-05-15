from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from eventscrawler.eventscrawler.items import Event
import dateparser
from dateutil import parser


class RoConferencesSpider(CrawlSpider):
    name = 'roconfcrawler'
    start_urls = ['https://codecamp.ro/confs', 'https://www.eventbrite.com/b/romania/science-and-tech/',
                  'https://softlead.ro/evenimente-it-c', 'https://softlead.ro/evenimente-it-c/2',
                  'https://softlead.ro/evenimente-it-c/3',
                  'https://conferencealerts.com/country-listing?country=Romania']
    rules = (
        Rule(
            LinkExtractor(allow=("codecamp.ro/conferences/",
                                 "eventbrite.com/d/romania/science-and-tech--events/", "eventbrite.com/e/",
                                 "eventbrite.com/b/romania/science-and-tech/",
                                 "softlead.ro/evenimente-it-c/",
                                 "conferencealerts.com/"), deny=("add-your-event", "promotion", "unsubscribe")),
            callback="parse_item"),
        Rule(
            LinkExtractor(allow=('/evenimente-it-c/\d+')),
            follow=True
        ),
        Rule(
            LinkExtractor(allow=('/evenimente-it-c/.+')),
            callback='parse_softlead'
        ),
        # Rule(LinkExtractor(restrict_xpaths="//a[@class='page-link' and contains(text(), 'Next')]"), follow=True),
        # Rule(LinkExtractor(restrict_xpaths="//h3[@class='media-heading']/a"), callback='parse_conferencealerts'),
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

    def parse_conferencealerts(self, response):
        formatted_date = ''
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_title = response.xpath('//*[@id="eventNameHeader"]/text()').get()
        date_time = str(response.xpath('//*[@id="eventDate"]/text()').get(default="not found"))
        location = response.xpath('//*[@id="eventCountry"]/text()').get()
        topics = response.xpath('//*[@id="eventDescription"]/text()').get(default="not found").split('.')[0].strip()

        if date_time != "not found":
            start_date_str = date_time.split("to")[0].strip()
            start_date = parser.parse(start_date_str)
            formatted_date = start_date.strftime("%Y-%m-%d")
        event = Event()
        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = formatted_date if formatted_date else date_time
        event['location'] = location
        event['topics'] = topics

        yield event

    def parse_codecamp(self, response):
        event = Event()
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_title = response.xpath("//h1[@class='elementor-heading-title elementor-size-default']/text()").get()
        date_time = response.xpath("//div[@class='jet-listing-dynamic-field__content']/text()").get()
        location = response.xpath("//span[@class='elementor-icon-list-text']/text()").get()
        topics = 'Codecamp'

        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = date_time
        event['location'] = location
        event['topics'] = topics

        yield event

    def parse_eventbrite(self, response):
        event_obj = Event()
        event_title = response.xpath('//h1[@class="event-title"]/text()').get()
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_date = response.xpath('.//time/@datetime').get(default="not found")
        location = \
            response.xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div[1]/div/main/div/div[1]/div[2]/div['
                           '2]/section/div[2]/section[2]/div/div/div[2]/p/strong/text()').get()
        topics = "Science & Tech"

        event_obj['event_url'] = event_url
        event_obj['event_title'] = event_title
        event_obj['date_time'] = event_date
        event_obj['location'] = location
        event_obj['topics'] = topics

        yield event_obj

    def parse_softlead(self, response):
        event_obj = Event()
        event_title = response.xpath('//div[2]/div/div/div/div/h1/text()').get()
        self.logger.info(f'Hi, this is an event page! {response.url}')
        event_url = response.url
        event_date = response.xpath('//*[@id="content"]/div[2]/div/ul[1]/li[2]/text()[2]').get(default="not found")
        location = response.xpath('//*[@id="content"]/div[2]/div/ul[1]/li[1]/text()[2]').get(default="not found")
        topics = "ITC&C"

        event_obj['event_url'] = event_url
        event_obj['event_title'] = event_title
        event_obj['date_time'] = str(dateparser.parse(event_date, languages=['ro']))
        event_obj['location'] = location
        event_obj['topics'] = topics

        yield event_obj
