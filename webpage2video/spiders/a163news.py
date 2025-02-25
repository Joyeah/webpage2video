from datetime import datetime
import json
import scrapy
from scrapy.utils.url import parse_url

from utils.urltools import is_not_image
from webpage2video.items import ArticleItem
from urllib.parse import urlparse, parse_qs, unquote


class A163newsSpider(scrapy.Spider):
    '''
    scrapy news.163.com news channel list
    version: 1.0
    '''
    name = "163news"
    # allowed_domains = ["news.163.com", "nimg.ws.126.net"]
    start_urls = ["https://news.163.com/"]
    # 要闻：通过二次请求，回调填充
    start_urls = [
        # "http://127.0.0.1:8080/data_callback.json"
        # "https://news.163.com/special/cm_yaowen20200213/?callback=data_callback",
        "https://tech.163.com/special/00097UHL/tech_datalist.js?callback=data_callback",
        # "https://news.163.com/special/cm_guoji/?callback=data_callback"
    ]

    def parse(self, response):
        '''
        不请求首页，直接的二次请求
        https://news.163.com/special/cm_yaowen20200213/?callback=data_callback'''
        # with open("cache/163news.html", "wb") as f:
        #     f.write(response.body)
        
        # 中间新闻要闻：mid_main[0]，二次请求，回调填充
        # for item in response.xpath('//div[@class="mid_main"]'):
        #     print(item)
        
        text = response.text
        text = text.strip().replace("data_callback", "").lstrip("(").rstrip(")")
        with open("cache/data_callback.json", "w", encoding="utf8") as f:
            f.write(text)
        
        texts = []
        img_urls = []
        data = json.loads(text)
        for item in data:
            if 'newstype' in item and item['newstype'] == 'article' and 'imgurl'in item and item['imgurl']:
                try:
                    texts.append(item['title'])
                    # https://nimg.ws.126.net/?url=http%3A%2F%2Fcms-bucket.ws.126.net%2F2025%2F0225%2Fd04f7752p00ss81h1001pc0009c0070c.png&thumbnail=190y120&quality=100&type=jpg
                    # decodeURIComponent(item['imgurl'])
                    if is_not_image(item['imgurl']):
                        parsed_url = urlparse(item['imgurl'])
                        query_params = parse_qs(parsed_url.query)
                        if 'url' in query_params:
                            imgurl = query_params['url'][0]
                            img_urls.append(imgurl)
                    else:
                        img_urls.append(item['imgurl'])
                except Exception as e:
                    print(e)
                    pass
                

        channelname = ''
        if 'channelname' in data[0]:
            channelname = data[0]['channelname']
        elif 'cm_yaowen' in response.url:
            channelname = '要闻'
        elif 'tech_datalist' in response.url:
            channelname = '科技'
        elif 'cm_guoji' in response.url:
            channelname = '国际'
    
        article = ArticleItem()
        article['title'] = f'news163{channelname}{datetime.now().strftime("%Y%m%d")}'
        article['summary'] = ''
        article['paragraphs'] = texts
        article['image_urls'] = img_urls
        yield article



        