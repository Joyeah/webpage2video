import os

def is_not_image(url):
    # 方法1：检查扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.img']
    _, ext = os.path.splitext(url.lower())  # noqa: F821
    if ext not in image_extensions:
        return True