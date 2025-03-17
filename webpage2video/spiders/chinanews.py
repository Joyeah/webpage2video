from datetime import datetime
import scrapy
from scrapy.utils.url import parse_url

from webpage2video.items import ArticleItem

class ChinanewsSpider(scrapy.Spider):
    name = "chinanews"
    # allowed_domains = ["www.chinanews.com.cn"]
    start_urls = ["https://www.chinanews.com.cn/photo/"]
    # start_urls = ["http://127.0.0.1:8080/chinanews-photo.html"]

    def parse(self, response):
        '''https://www.chinanews.com.cn/photo/'''
        # with open("cache/chinanews-photo.html", "wb") as f:
        #     f.write(response.body)
        texts = []
        img_urls = []
        # div class="zs21-list-1"
        # block = response.xpath("//div[@class='zs21-list-1']")
        # for img in block.xpath('.//img'):
        #     title = img.css('::attr(alt)').get()
        #     img_src = img.css('::attr(src)').get()
        #     texts.append(title)
        #     img_urls.append(img_src)

        # # class="zxhb"  无文字，忽略

        # # //*[@id="picBox"]/ul/li
        # for li in response.xpath('//*[@id="picBox"]/ul/li'):
        #     title = li.css('span::text').get()
        #     img_src = li.css('img::attr(src)').get()
        #     texts.append(title)
        #     img_urls.append(response.urljoin(img_src))
        resp_url = parse_url(response.url)
        # 解析所有li标签，无文字的忽略；去重
        lis = response.xpath('//div[not(@class="channel-nav" or @class="column-list")]/ul[not(@class="nav_navcon")]/li')
        for li in lis:
            title = li.xpath('string(.)').get().strip()
            if not title:
                continue
            else:
                title = str.strip(title)
                if len(title) <= 10:
                    continue
            
            img_src = li.css('img::attr(src)').get()
            if not img_src:
                continue
            # 去重
            if title in texts: 
                continue
            texts.append(title)
            if resp_url.hostname == 'localhost' or resp_url.hostname == '127.0.0.1':
                img_urls.append(f'{resp_url.scheme}://{resp_url.netloc}/{img_src.split("/")[-1]}')
            else:
                img_urls.append(response.urljoin(img_src))

        
        article = ArticleItem()
        article['filename'] = f'{datetime.now().strftime("%Y%m%d")}chinanews_photo'
        article['title'] = f'中国新闻网图片{datetime.now().strftime("%Y%m%d")}'
        article['summary'] = '中国新闻网图片摘要'
        article['paragraphs'] = texts
        article['image_urls'] = img_urls
        
        yield article



    def parse_home(self, response):
        with open("cache/chinanews.html", "wb") as f:
            f.write(response.body)

        hrefs = response.xpath("//a")
        print(f'共获得a.href数量：{len(hrefs)}')
        texts = []
        img_srcs = []
        for href in hrefs:
            # yield scrapy.Request(response.urljoin(href), callback=self.parse)
            text = href.xpath("string(.)").get().strip()
            img_src = href.css('img::attr(src)').get()
            if text and img_src:
                if len(text) < 8 or img_src.endswith('ghs.png'):
                    continue
                print(text, img_src)
                texts.append(text)
                img_srcs.append(response.urljoin(img_src))
        

        article = ArticleItem()
        article['title'] = '中国新闻网图片'
        article['summary'] = '中国新闻网图片摘要'
        article['paragraphs'] = texts
        article['image_urls'] = img_srcs
        
        yield article



