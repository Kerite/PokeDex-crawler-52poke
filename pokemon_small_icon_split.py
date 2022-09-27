from PIL import Image
import requests
from io import BytesIO

from src import utils

proxies = {
    'http': '127.0.0.1:7890',
    'https': '127.0.0.1:7890'
}


def cut_image():
    image_url = 'https://media.52poke.com/wiki/f/f8/MSP.png'
    r = requests.get(image_url, proxies=proxies)
    image = Image.open(BytesIO(r.content))
    image.show()
    width, height = image.size
    item_width = int(width / 30)
    item_height = int(height / 42)
    box_list = []
    # 循环每行
    for i in range(0, 42):
        # 循环每行中的每个元素
        for j in range(0, 30):
            box = (j * item_width, i * item_height, (j + 1) * item_width, (i + 1) * item_height)
            box_list.append(box)

    return [image.crop(box) for box in box_list]


def cut_mst():
    image_url = 'https://media.52poke.com/wiki/d/df/MST_20px.png'
    r = requests.get(image_url, proxies=utils.proxies)
    image_data = Image.open(BytesIO(r.content))
    item_width, height = image_data.size
    item_height = item_width
    box_list = []
    for i in range(0, 21):
        box = (0, i * item_height, item_width, (i + 1) * item_height)
        box_list.append(box)

    return [image_data.crop(box) for box in box_list]


if __name__ == '__main__':
    image_list = cut_mst()
    index = 0
    for image in image_list:
        image.save('./mst_cut/' + str(index) + '.png', 'PNG')
        index += 1
