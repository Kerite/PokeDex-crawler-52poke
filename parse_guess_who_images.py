import os
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

threads = 10
filenames = os.listdir('pokemon_images')


def transform(file_path: str):
    """
    转换宝可梦图像到猜猜我是谁
    :param file_path: 转换的文件名
    :return:
    """
    print("正在转换：" + file_path)
    img = Image.open("pokemon_images/" + file_path)
    img = img.convert('RGBA')
    for i in range(0, img.size[0]):
        for j in range(0, img.size[1]):
            img_data = img.getpixel((i, j))
            if img_data[3] < 70:
                img.putpixel((i, j), (0, 0, 0, 255))
            else:
                img.putpixel((i, j), (255, 255, 255, 255))
    img = img.convert('P')
    img.save("./images_guess_who_i_am/" + file_path.replace(".webp", "#guess.webp"), 'WEBP')


if __name__ == '__main__':
    with ThreadPoolExecutor(35) as executor:
        executor.map(transform, filenames)
