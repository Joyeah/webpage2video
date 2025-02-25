# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from email.mime import base
import os
import re
from PIL import Image
from itemadapter import ItemAdapter
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from scrapy.exceptions import DropItem
from pathlib import PurePosixPath
import scrapy.utils
from scrapy.utils.httpobj import urlparse_cached
import pyttsx3
import subprocess
import logging
logger = logging.getLogger(__name__)

class Webpage2VideoPipeline(ImagesPipeline):
    # def process_item(self, item, spider):
    #     print(ItemAdapter(item).asdict())
    #     return item
    default_headers = {
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        # "Referer": "https://www.jiemian.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
    }

    def get_media_requests(self, item, info):
        out = self.store.basedir
        # 标题与简介
        title = item['title']
        filename = re.sub(r'[\W\s]', '', title)
        item['filename'] = filename
        if 'summary' in item and 'summary' in item:
            summary = item['summary'] or ''
            with open(f'{out}/{filename}_summary.txt', 'w', encoding='utf-8') as f:
                f.write(item['title'] + '\n')
                f.write(summary + '\n')
        # 保存图片顺序
        with open(f'{out}/{filename}_order.txt', 'w', encoding='utf-8') as f:
            for image_url in item['image_urls']:
                imgfilename = image_url.split('/')[-1]
                f.write(imgfilename + '\n')
                
        # 遍历图片
        for i in range(len(item['image_urls'])):
            image_url = item['image_urls'][i]
            imgfilename = image_url.split('/')[-1]
            # 移到item_completed()中，因为图片下载时会自动创建file_path指定路径，不需要的检查路径是否存在
            # text = item['paragraphs'][i]
            # with open(f'{out}/{imgfilename}.txt', 'w', encoding='utf-8') as f:
            #     f.write(text + '\n')
            # 如果已经存在了就不再下载
            image_path = os.path.join(self.store.basedir, imgfilename)
            if os.path.exists(image_path):
                continue
            # parsed_url = scrapy.utils.url.parse_url(image_url)
            # self.default_headers['Referer'] = f'{parsed_url.scheme}//{parsed_url.netloc}/' #'https://www.jiemian.com'
            # yield scrapy.Request(image_url, headers=self.default_headers)
            yield scrapy.Request(image_url)

            

    def file_path(self, request, response = None, info = None, *, item = None):
        filename = PurePosixPath(urlparse_cached(request).path).name
        return filename
    
    def item_completed(self, results, item, info):
        # image_paths = [x['path'] for ok, x in results if ok]
        # if not image_paths:
        #     raise DropItem("Item contains no images")
        # item['image_paths'] = image_paths  # 保存的图片路径
        
        # 保存图片对应的文字
        out = self.store.basedir
        for i in range(len(item['image_urls'])):
            text = item['paragraphs'][i]
            imgfilefullname = item['image_urls'][i].split('/')[-1]
            imgfilename = imgfilefullname.split('.')[0]

            with open(f'{out}/{imgfilename}.txt', 'w', encoding='utf-8') as f:
                f.write(text + '\n')

        return item
        
    
class MoviePipeline:
    def process_item(self, item, spider):
        """
        TODO TTS and Convert to MP4
        """
        print("Media Pipeline::process_item::")
        print(ItemAdapter(item))
        
        # step1: 转换文本到音频文件MP3
        mp3paths = []
        engine = pyttsx3.init()
        basedir = spider.settings.get('IMAGES_STORE')
        # summary
        if 'summary' in item and item['summary']:
            summary_audio = f'{basedir}/{item["filename"]}_summary.mp3'
            engine.save_to_file(item['summary'], summary_audio)

        # 遍历文字
        for i in range(len(item['paragraphs'])):
            paragraph = item['paragraphs'][i]
            image_url = item['image_urls'][i]
            imgfilename = image_url.split('/')[-1]
            # 图片不存在的不处理
            if not os.path.exists(os.path.join(basedir, imgfilename)):
                continue

            imgfilename = imgfilename.split('.')[0]
            mp3file = f'{basedir}/{imgfilename}.mp3'
            if not os.path.exists(mp3file):
                logger.info(f'Convert text to MP3: {mp3file}')
                engine.save_to_file(paragraph, mp3file)
            mp3paths.append(mp3file)
            engine.runAndWait()
        
        logger.info('Media Pipeline::process_item:: Convert to mp3 Done')

        self.gen_video2(item, spider, basedir, mp3paths)

        return item
        

    def gen_video(self, item, spider, basedir, summary_audio, mp3paths):
        """生成音频及视频文件

        Args:
            item (_type_): _description_
            spider (_type_): _description_
            basedir (_type_): _description_
            summary_audio (_type_): _description_
            mp3paths (_type_): _description_

        Returns:
            _type_: _description_
        Deprecated:
            write_videofile()非常慢

        """
        # step2: 生成视频文件
        # 创建一个空列表存储视频片段
        video_clips = []
        # 片头summary
        first_imagepath = item['image_urls'][0].split('/')[-1]
        first_imagepath = first_imagepath.split('.')[0]
        summary_image = os.path.join(basedir, first_imagepath)  # 获取第一张
        summary_clip = self.makeVideoClip(summary_image, summary_audio)
        video_clips.append(summary_clip)

        # 合并图片音频文件到视频文件MP4
        # for image_path, mp3path in zip(item['image_paths'], mp3paths):
        for image_path, mp3path in zip(item['image_urls'], mp3paths):
            image_path = os.path.join(basedir, image_path.split('/')[-1])
            video_clip = self.makeVideoClip(image_path, mp3path)
            video_clips.append(video_clip)

        
        # 将所有视频片段合并成一个视频
        final_video = concatenate_videoclips(video_clips, method='compose')  #.resize((1920, 1080)).set_position(('center','center'))
        # 保存合并后的视频到本地
        video_fname = item['filename'] or re.sub(r'[\W\s]', '', item['title'])
        # final_video.write_videofile(f'{basedir}/{video_fname}.mp4', fps=24, codec='mpeg4', bitrate='1000k')
        # final_video.write_videofile(f'{basedir}/{video_fname}.mp4', fps=24, preset='ultrafast', audio_codec='aac', audio_bitrate='192k')
        final_video.write_videofile(f'{basedir}/{video_fname}.mp4', fps=15, codec="libx264", preset="ultrafast", threads=8)
        logger.info('Media Pipeline::process_item:: Convert to mp4 Done')
        # return item
        

    def makeVideoClip(self, image_path, mp3path):
        # 获得音频文件的时长
        audio_clip = AudioFileClip(mp3path)
        audio_duration = audio_clip.duration

        # 创建图片视频片断对象
        image_clip = ImageClip(image_path, duration=audio_duration)
        image_clip.fadein(0.5)

        image_clip = image_clip.resized(width=1280)
        # 将图片和音频合成一个视频，并保存为mp4格式
        video_clip = image_clip.with_audio(audio_clip)
        
        return video_clip
    
    def gen_video2(self, item, spider, basedir, mp3paths):
        """生成音频及视频文件,采用ffmepg生成单图片视频,再合并
        """
        # step2: 生成视频文件
        # 创建一个列表存储视频片段
        video_clips = []
        # 片头summary
        if 'summary' in item and item['summary']:
            summary_audio = f'{basedir}/{item["filename"]}_summary.mp3'
            first_imagepath = item['image_urls'][0].split('/')[-1]
            first_imagepath = first_imagepath.split('.')[0]
            summary_image = os.path.join(basedir, first_imagepath)  # 获取第一张
            summary_clip = self.makeVideoClip2(summary_image, summary_audio)
            video_clips.append(summary_clip)
        
        # 合并图片音频文件到视频文件MP4
        for image_path, mp3path in zip(item['image_urls'], mp3paths):
            image_path = os.path.join(basedir, image_path.split('/')[-1])
            if os.path.exists(image_path):
                video_clip = self.makeVideoClip2(image_path, mp3path)
                video_clips.append(video_clip)

        # 创建一个列表存储视频片段
        clip_list = f'{basedir}/{item['filename']}_list.txt'
        with open(clip_list, 'w') as f:
            for vid in video_clips:
                f.write("file '%s'\n" % vid.split(os.path.sep)[-1])

        # 将所有视频片段合并成一个视频
        self.merge_video_clips(item, spider, basedir)
        logger.info('Media Pipeline::gen_video2:: Convert to mp4 Done')
        
        # 删除临时文件
        if os.path.exists(clip_list):
            os.remove(clip_list)
        if os.path.exists(f'{basedir}/{item["filename"]}_summary.mp3'):
            os.remove(f'{basedir}/{item["filename"]}_summary.mp3')
        for vid in video_clips:
            os.remove(vid)




    def makeVideoClip2(self, image_path, mp3path):
        """
        用ffmepg生成单图片视频
        ffmpeg -loop 1 -i 1.jpg -i 1.mp3 -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -c:a aac -t 10 -pix_fmt yuv420p -y 1.mp4
        特效：
            fade=t=in:st=0:d=1：淡入效果，从第 0 秒开始，持续 1 秒。
            fade=t=out:st=4:d=1：淡出效果，从第 4 秒开始，持续 1 秒
        """
        # 获得音频文件的时长
        audio_clip = AudioFileClip(mp3path)
        audio_duration = audio_clip.duration
        audio_clip.close()

        video_clip_path = image_path.split('.')[0] + '.mp4'
        if os.path.exists(video_clip_path):
            return video_clip_path

        command = [
            'ffmpeg', '-loop', '1', '-i', image_path, '-i', mp3path,
            '-vf', f'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fade=t=in:st=0:d=1,fade=t=out:st={audio_duration-1}:d=1',
            '-c:v', 'libx264', '-c:a', 'aac', '-t', str(audio_duration), '-pix_fmt', 'yuv420p', '-y', video_clip_path

        ]
        subprocess.run(command)
        logger.info('Media Pipeline::makeVideoClip2:: Make Video clip Done')
        return video_clip_path

    def merge_video_clips(self, item, spider, basedir):
        """
        合并多个视频片段，并保存为一个新的视频文件。
        ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
        Args:
            item (dict): 爬虫项目数据。
            spider (Spider): 正在运行的爬虫实例。
            basedir (str): 基础目录路径。

        Returns:
            None
        """
        clip_list = f'{basedir}/{item['filename']}_list.txt'
        title = item['filename'] or re.sub(r'[\W\s]', '', item['title'])
        output = os.path.join(basedir, f'{title}_total' + '.mp4')
        command = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', clip_list, '-c', 'copy', '-y', output
        ]
        print(' '.join(command))
        subprocess.run(command)
        logger.info('Media Pipeline::merge_video_clips:: Merge Video Done')
        # 添加背景音乐
        # ffmpeg -i 1.mp4 -stream_loop -1 -i background.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=3[audio]" -map 0:v:0 -map "[audio]" -c:v copy -shortest -y 1-mu.mp4
        # ffmpeg -i download/图集水培蔬菜在海上种地未来农业能否喂饱所有人_total.mp4 -stream_loop -1 -i background.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=3[audio]" -map 0:v:0 -map "[audio]" -c:v copy -c:a aac -shortest -y download\图集水培蔬菜在海上种地未来农业能否喂饱所有人_music.mp4
        music_video = os.path.join(basedir, f'{title}_music' + '.mp4')
        # music_video = f'{basedir}/{title}_music' + '.mp4'
        command = [
            'ffmpeg', '-i', output, '-stream_loop', '-1','-i', 'background.mp3', '-filter_complex', '[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=3[audio]', '-map', '0:v:0', '-map', '[audio]','-c:v', 'copy', '-c:a', 'aac', '-shortest', '-y', music_video
        ]
        print(' '.join(command))
        subprocess.run(command)
        logger.info('Media Pipeline::merge_video_clips:: Add backgroud music Done')
        
        subprocess.run(['rm', clip_list, output])

