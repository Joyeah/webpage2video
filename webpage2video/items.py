# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from fileinput import filename
import scrapy


class ArticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    paragraphs = scrapy.Field()
    image_urls = scrapy.Field()  # 图片链接列表
    images = scrapy.Field()     # 图片下载后的信息（由 ImagesPipeline 自动填充
    image_paths = scrapy.Field() # 图片存储路径列表
    filename = scrapy.Field() # 文章保存的文件名
