from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
# from twisted.trial import runner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from eventscrawler.spiders.abroad_conferences import AbroadconfSpider
from eventscrawler.spiders.ro_conferences import RoConferencesSpider

# @defer.inlineCallbacks
# def crawl():
#     yield runner.crawl(RoConferencesSpider)
#     yield runner.crawl(AbroadconfSpider)
#     reactor.stop()


if __name__ == '__main__':
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    runner.crawl(AbroadconfSpider)
    runner.crawl(RoConferencesSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    # crawl()
    reactor.run()