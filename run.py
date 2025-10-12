from scrapy.crawler import CrawlerProcess
from spiders.trades_spider import TradesSpider
import os

if __name__ == '__main__':
    os.makedirs('outputs', exist_ok=True)
    process = CrawlerProcess()
    process.crawl(TradesSpider)
    process.start()