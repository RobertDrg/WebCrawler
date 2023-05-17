from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from eventscrawler.eventscrawler.items import Event


class AbroadconfSpider(CrawlSpider):
    name = 'abroadconfcrawler'
    start_urls = ['https://futureconevents.com/events', 'https://techevents.online/',
                  'https://conferencemonkey.org/top/conferences']

    rules = (
        Rule(LinkExtractor(allow=r"/top/conferences\?page=\d+"), callback="parse_conferencemonkey", follow=True),
        Rule(
            LinkExtractor(allow=("futureconevents.com/events/", "techevents",
                                 "conferencemonkey.org/top/conferences", "conferencemonkey.org/conference/"),
                          deny=("sponsorship", "2020", "2021", "2022", "facebook", "instagram", "subscribe")),
            callback="parse_item"),
    )

    def parse_item(self, response):
        if "futureconevents.com" in response.url:
            yield from self.parse_futurecon(response)
        elif "techevents" in response.url:
            yield from self.parse_techevents(response)
        elif "conferencemonkey" in response.url:
            yield from self.parse_conferencemonkey(response)

    def parse_conferencemonkey(self, response):
        self.logger.info('Hi, this is an event page! %s', response.url)
        event_url = response.url
        event_title = response.xpath('//*[@id="page-title"]/text()').get(default="not found")
        date_time = response.xpath('//div[2]/div[2]/div[2]/div[2]/div[3]/h4/time/text()').get(default="not found")
        location = response.xpath('//div[@class="location-details"]//p/text()').get(default="not found")
        topics = response.xpath('//*[@id="tags"]/li/a/text()').getall()

        event_title = event_title.replace("\n", "").strip()
        location = location.replace("\n", "").replace("  ", "").strip()
        print(location)

        event = Event()
        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = date_time.strip()
        event['location'] = location
        event['topics'] = topics

        yield event

    def parse_futurecon(self, response):
        self.logger.info('Hi, this is an event page! %s', response.url)
        event_url = response.url
        event_title = response.xpath("//header[@class='fc-event-header ']/h1/span/text()").get(default="not found")
        date_time = response.xpath("//section[@class='fc-event-header-content']/p/strong/text()") \
            .get(default="not found")
        location = response.xpath("//section[@class='fc-event-header-content']/p/strong/a/text()") \
            .get(default="Online")
        category = "Cybersecurity"

        event = Event()
        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = date_time
        event['location'] = location
        event['topics'] = category

        yield event

    def parse_techevents(self, response):
        self.logger.info('Hi, this is an event page! %s', response.url)
        event_url = response.url
        event_title = response.xpath('//*[@id="wrapper"]/div/div/h1/text()').get(default="not found")
        date_time = response.xpath('//*[@id="sidebar"]/div/div/p/text()').get(default="not found")
        location = response.xpath('//*[@id="sidebar"]/div/div/address/text()').get(default="not found")
        category = "Tech"

        event = Event()
        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = date_time
        event['location'] = location
        event['topics'] = category

        yield event
