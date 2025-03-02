from datetime import datetime
import json
import scrapy

from webpage2video.items import ArticleItem


class MsnnewsSpider(scrapy.Spider):
    '''
    MSN新闻爬虫, use json data
    version: 0.1
    '''
    name = "msnnews"
    allowed_domains = ["www.msn.cn", "assets.msn.cn", "img-s.msn.cn"]
    # start_urls = ["https://www.msn.cn/zh-cn"]  
    # start_urls = ["https://assets.msn.cn/resolver/api/resolve/v3/config/?expType=AppConfig&expInstance=default&apptype=windows&v=20250224.570&targetScope={%22audienceMode%22:%22adult%22,%22browser%22:{%22browserType%22:%22edgeChromium%22,%22version%22:%22133%22,%22ismobile%22:%22false%22},%22deviceFormFactor%22:%22desktop%22,%22domain%22:%22www.msn.cn%22,%22locale%22:{%22content%22:{%22language%22:%22zh%22,%22market%22:%22cn%22},%22display%22:{%22language%22:%22zh%22,%22market%22:%22cn%22}},%22ocid%22:%22widgetonlockscreen%22,%22os%22:%22windows%22,%22platform%22:%22web%22,%22pageType%22:%22windowshp%22,%22pageExperiments%22:[%22prg-ch-lsbtwk1%22,%22prg-msn-blsbidmho%22,%22prg-pr2-dis-signal%22,%22prg-update-hide-hrt%22]}"] # config json数据
    start_urls = ["https://assets.msn.cn/service/news/feed/pages/channelfeed?InterestIds=Y_77f04c37-b63e-46b4-a990-e926f7d129ff&activityId=2016E08B-3D23-4A19-99AC-2762CCB659C5&apikey=0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM&cm=zh-cn&it=edgeid&memory=8&ocid=social-peregrine&scn=APP_ANON&timeOut=2000&user=m-1F779C3596076411290F88DE978D65A3"] # 新闻列表json数据
    # start_urls = ["http://127.0.0.1:8080/channelfeed.json"]    # def start_requests(self):
    #     default_headers = {
    #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #         'Accept-Encoding': 'gzip, deflate, sdch, br',
    #         'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    #         'Cache-Control': 'max-age=0',
    #         'Connection': 'keep-alive',
    #         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    #     }
    #     for url in self.start_urls:
    #         yield scrapy.Request(url, headers=default_headers, callback=self.parse)

    def parse(self, response):
        '''https://assets.msn.cn/service/news/feed/pages/channelfeed...'''
        with open('cache/channelfeed.json', 'wb') as f:
            f.write(response.body)

        img_urls = []
        texts = []
        data = json.loads(response.text)
        for section in data['sections']:
            for card in section['cards']:
                if card['type'] == 'article':
                    title = card['title']
                    abstract = card['abstract']
                    # url = card['url']
                    if 'images' in card and len(card['images']) > 0:
                        img_url = card['images'][0]['url']
                        print(title, img_url)
                        img_urls.append(img_url)
                        texts.append(abstract)
                
        article = ArticleItem()
        article['title'] = article['filename'] = f'MSN新闻{datetime.now().strftime("%Y%m%d")}'
        article['image_urls'] = img_urls
        article['paragraphs'] = texts

        yield article
        





    def parse_config(self, response):
        '''https://assets.msn.cn/resolver/api/resolve/v3/config/?...'''
        # with open('cache/msn-config.json', 'wb') as f:
        #     f.write(response.body)

        config = json.loads(response.text)
        print(json.dumps(config, indent=2))
        
        # menu_items = config['configs']['shared/msn-ns/CommonHeaderWC/default']['properties']['navigationConfig']['hamburgerMenuItems']
        menu_items = config['configs']['shared/msn-ns/CommonHeaderWC/default']['properties']['navigationConfig']['contextualNavItems']
        for item in menu_items:
            if item['id'] == 'news':
                # "externalUrl": "https://www.msn.com/zh-cn/channel/topic/要闻/tp-Y_77f04c37-b63e-46b4-a990-e926f7d129ff"
                externalUrl = item['renderInfo']['externalUrl']
                print(externalUrl)
                # yield scrapy.Request(item['renderInfo']['externalUrl'], callback=self.parse_news_list_html)
                yield response.follow(externalUrl, callback=self.parse_news_list_html, dont_filter=True)
    
    def parse_news_list_html(self, response):
        with open('cache/msnnews_news_list.html', 'wb') as f:
            f.write(response.body)
        
        # 页面中找不到channelfeed的合成json数据，应该是js动态生成的。
        print('News list html parsed')

        

    def parse_homepage(self, response):
        '''https://www.msn.cn/zh-cn'''
        with open('cache/msnnews.html', 'wb') as f:
            f.write(response.body)

        client_settings = response.xpath('head/@data-client-settings').get()
        settings = json.loads(client_settings)
        print(json.dumps(settings, indent=2))
        crs = settings['servicesEndpoints']['crs']
        url = f'{crs['domain']}{crs["path"]}{crs["v"]}/config'


        hrefs = response.css('a')
        for href in hrefs:
            print(href.xpath("@href").extract())
        
