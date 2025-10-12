import scrapy

class TradesSpider(scrapy.Spider):
    name = 'trades'
    start_urls = ['https://skilledtradesbc.ca/get-certified-about-exams/exam-study-support']
    custom_settings = {
        'FEEDS': {
            'outputs/study_guide.json': {'format': 'json', 'overwrite': True}
        }
    }
    
    def parse(self, response):
        # Get all links from the page
        for link in response.css('a'):
            url = link.attrib.get('href', '').strip()
            if not url or '#' in url or 'mailto:' in url:
                continue
                
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse_resource, meta={
                'title': link.css('::text').get('').strip() or url,
                'url': url
            })
    
    def parse_resource(self, response):
        # Get content from paragraphs
        content = ' '.join(response.css('p ::text').getall())
        content = ' '.join(content.split())
        
        yield {
            'title': response.meta['title'],
            'url': response.meta['url'],
            'content': content if content.strip() else None,
            'status': 'ok' if content.strip() else 'no_content'
        }