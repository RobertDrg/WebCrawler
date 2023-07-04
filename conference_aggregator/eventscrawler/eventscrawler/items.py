import scrapy


class Event(scrapy.Item):
    event_url = scrapy.Field()
    event_title = scrapy.Field()
    date_time = scrapy.Field()
    call_for_papers_date = scrapy.Field()
    location = scrapy.Field()
    topics = scrapy.Field()