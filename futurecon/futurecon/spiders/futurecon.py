import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from w3lib.url import url_query_cleaner
import extruct


class FutureconSpider(scrapy.Spider):
    name = 'futurecon'
    allowed_domains = ['www.futureconevents.com']
    start_urls = ['https://futureconevents.com/events//']

    def parse(self, response):
        print("=== Crawling MicroFocus Events ===")
        print("HTTP STATUS: " + str(response.status))
        print("\n")

        events = response.css("ul.bz-events-list")
        # event_names = events[1].css("header.fc-event-header").getall()
        cities = events[0].css("h2::text").getall()
        dates = events[0].css("p.date-time::text").getall()
        urls = events[0].css("a.button::attr(href)").getall()
        urls = urls[::2]

        # print(event_names)
        print(cities)
        print(dates)
