'''
TODO: BUG 无法下载图片media_failed
1. 提取path中的id
https://www.msn.cn/zh-cn/news/other/%E4%BA%9A%E9%A9%AC%E9%80%8A%E6%B2%B3%E6%9C%89%E5%A4%9A%E6%81%90%E6%80%96-%E6%B5%81%E9%87%8F%E6%98%AF%E9%95%BF%E6%B1%9F%E7%9A%84%E4%B8%83%E5%80%8D-%E5%A6%82%E4%BB%8A%E6%B2%A1%E4%B8%80%E5%BA%A7%E6%A1%A5%E6%95%A2%E8%B7%A8%E8%B6%8A%E5%AE%83/ar-AA1AHmwE?ocid=msedgdhp&pc=U531&cvid=67d0db7964c74cdf8e0e749912070d0d&ei=89
2. 组合为json数据地址：
https://assets.msn.cn/content/view/v2/Detail/zh-cn/AA1AGljI

命令行：
scrapy crawl myspider -a url=http://...
'''
from datetime import datetime
import json
import math
import re
from urllib.parse import urlparse
import scrapy

from webpage2video.items import ArticleItem


class MsnnewsPageSpider(scrapy.Spider):
    name = "msnnews_page"
    allowed_domains = ["assets.msn.cn"]
    start_urls = ["https://assets.msn.cn/content/view/v2/Detail/zh-cn/AA1AGljI"]
    
    def __init__(self, url=None, *args, **kwargs):
        super(MsnnewsPageSpider, self).__init__(*args, **kwargs)
        # 解析URL并转为json url
        if not url:
            # raise ValueError("No URL provided")
            pass
        else:
            parsed_url = urlparse(url)
            id = parsed_url.path.split('/')[-1]  # ar-AA1AHmwE
            if '-' in id:
                id = id.split('-')[1]
            json_url = f'https://assets.msn.cn/content/view/v2/Detail/zh-cn/{id}'

            self.start_urls = [json_url] 

        
    def parse(self, response):
        self.logger.info(f'Starting spider on {response.url}')
        parsed_url = urlparse(response.url)
        id = parsed_url.path.split('/')[-1]  # AA1AHmwE

        with open(f'cache/msnnews-{id}.json', 'wb') as f:
            f.write(response.body)

        img_urls = []
        texts = []
        data = json.loads(response.text) 
        
        title = data['title']
        
        for img in data['imageResources']:
            img_urls.append(img['url'])

        # "<p>3月，冬春交替之际，冷空气、暖湿气流都十分活跃，带来的天气“五花八门”，雨雪、大风、沙尘、降温……这周在我国轮番上演。</p><p>1、降温</p><p>昨天，一股冷空气开始影响我国新疆北部，今天冷空气继续东移影响我国，内蒙古、甘肃、宁夏等地出现降温。而中东部多地在冷空气抵达之前，今天气温仍较常年同期偏高明显，东北多地最高气温在10℃以上，华北南部到长江沿线最高气温达20℃上下。</p><p><p><img data-reference=\"image\" data-document-id=\"cms/api/amp/image/AA1AGssW\"></p></p><p>13日至15日，还将有新一股冷空气东移南下，在两股冷空气接连影响下，一直到周末，我国大部地区气温将波动下滑，多地最高气温累计降幅可达10℃以上。</p><p><p><img data-reference=\"image\" data-document-id=\"cms/api/amp/image/AA1AGnAM\"></p>海平面气压500百帕高度场图，图中绿色为冷高压。</p><p>16日前后气温将降至本次过程的低点，最高气温15℃线退至江南南部，华北南部到长江沿线最高气温降至10℃上下。</p><p>2、大风、沙尘</p><p>冷空气制造降温的同时，也带来了大风。今明天，内蒙古、河北、黑龙江、吉林、辽宁等地将有5至6级风，明天内蒙古东南部阵风风力或有一定极端性。</p><p>在大风推动下，沙尘天气也向东向南推进，中央气象台今天晚上发布了沙尘暴蓝色预警，预计今天夜间到明天，新疆南部、内蒙古中部和东南部、甘肃东部、陕西中北部、山西、河北、北京、天津、河南中北部、山东、辽宁中西部、吉林西部等地有扬沙或浮尘天气，其中内蒙古中部局地有沙尘暴。</p><p><p><img data-reference=\"image\" data-document-id=\"cms/api/amp/image/AA1AGq5L\"></p></p><p>从历史数据统计来看，春季为我国沙尘天气高发期，约80%的沙尘过程都出现在3月至5月。沙尘天气下，大家尽量减少户外活动，出门做好防范。</p><p>3、暴雪</p><p>冷空气东移过程中，地面气旋系统东移并发展加强，冷涡后部冷空气与高空槽前西南暖湿气流辐合，将给内蒙古东北部、东北一带带去较大范围的雨雪天气，今明天将是降雪的鼎盛时段。</p><p><p><img data-reference=\"image\" data-document-id=\"cms/api/amp/image/AA1AGnAW\"></p></p><p>预计今天夜间到明天，内蒙古东北部、黑龙江北部等地部分地区有大到暴雪，局地大暴雪。明天夜间到后天，东北地区北部和东部、新疆沿天山地区和南部山区、西藏北部和东部、青海、川西高原等地部分地区有小雪或雨夹雪，其中，黑龙江北部等地部分地区有中到大雪。</p><p><p><img data-reference=\"image\" data-document-id=\"cms/api/amp/image/AA1AGnB1\"></p></p><p>之后，新一股冷空气南下和暖湿气流交汇，13日至15日西北地区东部、华北等地降雪也将会发展增多，大家继续留意临近预报。</p><p>4、暴雨</p><p>本周，南支槽波动频繁，加上冷空气南下，南方大部将维持多阴雨的天气格局，部分地区降雨较强，还将出现大到暴雨。</p><p>预计3月12日至15日，南方地区将有一次较强降雨过程，湖南中南部、江西中部、浙江西南部、福建西部、广西东北部、广东西北部的部分地区有大到暴雨、局地大暴雨，降雨主要出现在12日夜间至14日夜间。</p><p><p><img data-reference=\"image\" data-document-id=\"cms/api/amp/image/AA1AGhAE\"></p></p><p>降雨时伴有雷电天气，江南中南部、华南中北部部分地区有短时强降水（最大小时降雨量20～50毫米），局地有雷暴大风或冰雹天气，强对流主要影响时段在13日夜间至15日白天。</p><p>5、回南天</p><p>随着低空南风增强，今天在广西、广东北部部分地区出现了回南天。即使没有回南天，由于湿度大，也是湿漉漉的感觉。</p><p><p><img data-reference=\"image\" data-document-id=\"cms/api/amp/image/AA1AGjW2\"></p>今天，广西南宁出现回南天（图/曾海科）</p><p>16日之前，广东、广西等地这种潮湿的感觉还将持续，之后随着冷空气南下，湿漉漉的天气有望结束。</p><p>---------------------------------</p><p>本周天气“大杂烩”，你都被哪些天气“圈”住了？</p>",
        body = scrapy.Selector(text=data['body'])
        ptexts = body.css('p::text').getall()
        if len(ptexts)> len(img_urls):
            ps = []
            for ptext in ptexts:
                if re.match(r'(\d+\.|\d+\、)', ptext):
                    texts.append(''.join(ps))
                    ps = []
                ps.append(ptext)
            
            if len(ps)>0:
                texts.append(''.join(ps))

        if len(texts) == 1:
            texts  =[]
            # body中无序号, 按整句切分
            ptext = body.xpath('string(.)').get()
            ps = ptext.split('。')
            n = math.floor(len(ps) / len(img_urls)) 
            for i in range(len(img_urls)):
                texts.append(''.join(ps[i*n:(i+1)*n]))
            # 剩余的句子
            if n < len(ps) / len(img_urls):
                texts[-1]= texts[-1] + ''.join(ps[n*len(img_urls):])

        article = ArticleItem()
        article['title'] = f'MSN新闻-{title}'
        article['filename'] = f'{datetime.now().strftime("%Y%m%d")}MSN新闻-{title}'
        article['image_urls'] = img_urls
        article['paragraphs'] = texts

        yield article
