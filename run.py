from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.trades_spider import TradesSpider
import os

def main():
    """Run the spider and save results."""
    # Create outputs directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    
    # Get settings and run spider
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(TradesSpider)
    process.start()

if __name__ == '__main__':
    main()