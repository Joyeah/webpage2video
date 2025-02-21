import scrapy


class OnepageSpider(scrapy.Spider):
    name = "onepage"
    allowed_domains = ["www.jiemian.com"]
    start_urls = ["https://www.jiemian.com/article/10593988.html"]

    def parse(self, response):
        pass
