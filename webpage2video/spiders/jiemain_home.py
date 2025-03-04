from datetime import datetime
import scrapy

from webpage2video.items import ArticleItem


class JiemainHomeSpider(scrapy.Spider):
    name = "jiemain_home"
    # allowed_domains = ["www.jiemian.com"]
    start_urls = ["https://www.jiemian.com/"]
    start_urls = ["http://127.0.0.1:8080/jiemian.html"]

    def parse(self, response):
        imgs = []
        texts = []
        # news-view, columns-lists
        # news-view
        items = response.xpath('//div[@class="news-view"]')
        for item in items:
            href = item.css('img::attr(src)').get() or item.xpath('.//img/@src').get()
            if not href:
                self.logger.warning(f'No image found in {item.get()}')
                continue
            text = item.css('img::attr(alt)').get()
            if not text:
                text = item.css('span.title::text').get() 
                if not text:
                    text = item.css('p.title::text').get()
                    if text:
                        text2 = item.css('div.news-main::text').get()
                        if text2:
                            text = text + text2
                    else:
                        text = item.css('::text').get()
                        if not text:
                            text = 'No Text here'


            # add to list
            if not href in imgs:
                imgs.append(href)
                texts.append(text)
            
        article = ArticleItem()
        article['title'] = article['filename'] = f'界面新闻{datetime.now().strftime("%Y%m%d")}'
        article['summary'] = ''
        article['image_urls'] = imgs
        article['paragraphs'] = texts
        yield article