from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer

from eventscrawler.eventscrawler.spiders.abroad_conferences import AbroadconfSpider
from eventscrawler.eventscrawler.spiders.ro_conferences import RoConferencesSpider


# @defer.inlineCallbacks
def start_crawler():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    yield runner.crawl(AbroadconfSpider)
    yield runner.crawl(RoConferencesSpider)
    yield runner.join()
    reactor.stop()
