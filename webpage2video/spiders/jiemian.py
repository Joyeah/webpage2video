import scrapy
from scrapy.utils.url import parse_url
from webpage2video.items import ArticleItem

# 文章索引页：界面影像 https://www.jiemian.com/lists/134.html
class JiemainSpider(scrapy.Spider):
    name = "jiemain"
    # must be set all url host here !!!!important!!!!
    # allowed_domains = ["127.0.0.1:8080", "www.jiemian.com", "img1.jiemian.com", "img2.jiemian.com", "img3.jiemian.com", "img4.jiemian.com"]
    start_urls = ["https://www.jiemian.com/article/10593988.html"]
    start_urls = ['http://127.0.0.1:8080/jiemian_detail.html']
    start_urls = ["https://www.jiemian.com/article/10584320.html"]
    start_urls = ["https://www.jiemian.com/article/10527944.html"]
    start_urls = ["http://127.0.0.1:8080/10527944.html"]
    start_urls = ["https://www.jiemian.com/article/10584320.html"]
    start_urls = ["https://www.jiemian.com/article/8659722.html"]

    # default_headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #     'Accept-Encoding': 'gzip, deflate, sdch, br',
    #     'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    #     'Cache-Control': 'max-age=0',
    #     'Connection': 'keep-alive',
    #     'Host': 'www.jiemian.com',
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    # }

    def parse(self, response):
        title = response.xpath('//div[@class="article-header"]/h1/text()').get()
        # summary = response.xpath('//div[@class="article-header"]/p/text()').get()

        content = response.xpath('//div[@class="article-content"]')
        summary = ''.join(content.xpath('.//p/text()').getall()).strip()

        # image and comment
        # images = content.xpath('.//img[@src]/@src').getall()
        # comments = content.xpath('.//figcaption/text()').getall()
        imgs = []
        texts = []
        figures = content.xpath('.//figure[@class="content-img-focus img-focus"]')
        for figure in figures:
            image_src = figure.xpath('.//img[@src]/@src').get()
            # DEBUG: this use to LOCALHOST debug only
            parsed_url = parse_url(response.url)
            response_host = parsed_url.hostname
            if response_host == '127.0.0.1' or response_host == 'localhost':
                filename = image_src.split('/')[-1]
                image_src = f'{parsed_url.scheme}://{parsed_url.netloc}/{filename}'

            comments = figure.xpath('.//figcaption/text()').get()
            # imgs.append({'image': image, 'comments': comments})
            imgs.append(image_src)
            texts.append(comments)
            
            
        article = ArticleItem()
        article['title'] = title or 'notitle'
        article['summary'] = summary
        article['paragraphs'] = texts
        article['image_urls'] = imgs
        yield article


