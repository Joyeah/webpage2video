import scrapy

from webpage2video.items import ArticleItem

# FIXME : 部分转换语音失败，待查
class ChinanewsSpider(scrapy.Spider):
    name = "chinanews"
    allowed_domains = ["www.chinanews.com.cn"]
    start_urls = ["https://www.chinanews.com.cn/"]
    # start_urls = ["http://127.0.0.1:8080/chinanews.html"]

    def parse(self, response):
        with open("cache/chinanews.html", "w", encoding='utf8') as f:
            f.write(response.text)

        hrefs = response.xpath("//a")
        print(f'共获得a.href数量：{len(hrefs)}')
        texts = []
        img_srcs = []
        for href in hrefs:
            # yield scrapy.Request(response.urljoin(href), callback=self.parse)
            text = href.xpath("string(.)").get().strip()
            img_src = href.css('img::attr(src)').get()
            if text and img_src:
                if len(text) < 5 or img_src.endswith('ghs.png'):
                    continue
                print(text, img_src)
                texts.append(text)
                img_srcs.append(response.urljoin(img_src))
        

        article = ArticleItem()
        article['title'] = '中国新闻网首页标题'
        article['summary'] = '中国新闻网摘要'
        article['paragraphs'] = texts
        article['image_urls'] = img_srcs
        
        yield article



