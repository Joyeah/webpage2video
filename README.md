# webpage2video
extract picture and text , convert to a video

1. download pictures and text from a webpage
2. convert text to mp3
3. count mp3 duration
4. merge text and picture to a video

## dependencies
- scrapy (for download webpage and extract text, picture)
- pyttsx3 (for text to mp3)
- mutagen (for count mp3 duration)
- ffmpeg-python （ ffmpeg wrapper)


## count mp3 duraion
使用 mutagen 库直接读取音频文件的元信息（如时长）
```python
from mutagen.mp3 import MP3

def get_audio_duration(file_path):
    audio = MP3(file_path)
    return audio.info.length

# 示例
file_path = "your_audio_file.mp3"
duration = get_audio_duration(file_path)
print(f"音频时长: {duration:.2f} 秒")
```
