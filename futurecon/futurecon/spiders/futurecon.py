from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


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
        self.logger.info('Hi, this is an event page! %s', response.url)
        info_dict = yield {
            "event_url": response.url,
            "event_title": response.xpath("//header[@class='fc-event-header ']/h1/span/text()")
            .get(default="not found"),
            "date-time": response.xpath("//section[@class='fc-event-header-content']/p/strong/text()")
            .get(default="not found"),
            "location": response.xpath("//section[@class='fc-event-header-content']/p/strong/a/text()")
            .get(default="Online"),
            "category": "Cybersecurity",
        }


