import os
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

threads = 10
filenames = os.listdir('imgs')


def transform(file_path):
    print("正在转换：" + file_path)
    img = Image.open("imgs/" + file_path)
    img = img.convert('RGBA')
    for i in range(0, img.size[0]):
        for j in range(0, img.size[1]):
            img_data = img.getpixel((i, j))
            if img_data[3] < 70:
                img.putpixel((i, j), (0, 0, 0, 255))
            else:
                img.putpixel((i, j), (255, 255, 255, 255))
    img = img.convert('P')
    img.save("imgs_guess/" + file_path.replace(".png", "#guess.png"))


with ThreadPoolExecutor(35) as executor:
    executor.map(transform, filenames)
