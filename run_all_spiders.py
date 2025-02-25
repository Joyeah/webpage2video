from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_all_spiders():
    process = CrawlerProcess(get_project_settings())

    # 列出所有爬虫并运行
    for spider_name in process.spider_loader.list():
        process.crawl(spider_name)

    process.start()  # 脚本会在这里阻塞，直到所有爬虫完成

if __name__ == "__main__":
    run_all_spiders()