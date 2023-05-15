from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from eventscrawler.eventscrawler.items import Event


class FutureconSpider(CrawlSpider):
    name = 'futureconcrawler'
    allowed_domains = ['futureconevents.com']
    start_urls = ['https://futureconevents.com/events']

    rules = (
        Rule(
            LinkExtractor(allow="futureconevents.com/events/", deny=("sponsorship", "2020", "2021", "2022")),
            callback="parse_item"),
    )

    def parse_item(self, response):
        event = Event()
        self.logger.info('Hi, this is an event page! %s', response.url)
        event_url = response.url
        event_title = response.xpath("//header[@class='fc-event-header ']/h1/span/text()").get(default="not found")
        date_time = response.xpath("//section[@class='fc-event-header-content']/p/strong/text()") \
            .get(default="not found")
        location = response.xpath("//section[@class='fc-event-header-content']/p/strong/a/text()") \
            .get(default="Online")
        category = "Cybersecurity"
        # print(date_time)

        event['event_url'] = event_url
        event['event_title'] = event_title
        event['date_time'] = date_time
        event['location'] = location
        event['topics'] = category

        yield event
