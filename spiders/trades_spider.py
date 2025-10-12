import scrapy

class TradesSpider(scrapy.Spider):
    name = 'trades'
    start_urls = ['https://skilledtradesbc.ca/get-certified-about-exams/exam-study-support']
    custom_settings = {
        'USER_AGENT': 'TradeLift-Scraper/1.0',
        'FEEDS': {
            'outputs/study_guide.json': {
                'format': 'json',
                'overwrite': True
            }
        },
        'FEED_EXPORT_ENCODING': 'utf-8'
    }
    
    def parse(self, response):
        """Parse the main study support page."""
        # Find all links in relevant content areas
        for link in response.css('.entry-content a, .page-content a, .content a, .main-content a'):
            url = link.attrib.get('href', '').strip()
            
            # Skip non-http links and anchors
            if not url.startswith('http'):
                url = response.urljoin(url)
            if '#' in url or 'mailto:' in url:
                continue
            
            yield scrapy.Request(
                url,
                callback=self.parse_resource,
                meta={
                    'title': link.css('::text').get('').strip() or url,
                    'url': url
                }
            )
    
    def parse_resource(self, response):
        """Extract content from resource pages."""
        # Try to find content in common content areas
        content = ''
        for selector in ['article', 'main', '.entry-content', '.content', '.main-content']:
            content = ' '.join(response.css(f'{selector} ::text').getall())
            if content.strip():
                break
        
        # Fallback to all paragraphs if no content found
        if not content.strip():
            content = ' '.join(response.css('p ::text').getall())
        
        # Clean and truncate content
        content = ' '.join(content.split())
        if len(content) > 60000:
            content = content[:60000] + '... [truncated]'
        
        yield {
            'title': response.meta['title'],
            'url': response.meta['url'],
            'content': content if content.strip() else None,
            'status': 'ok' if content.strip() else 'no_content'
        }