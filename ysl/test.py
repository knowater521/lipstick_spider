# -*- coding: utf-8 -*-

import time
import json
import codecs
import requests
from pyquery import PyQuery as pq

from PIL import Image
from io import BytesIO

host = "https://www.yslbeautycn.com"


def get_product(page_url):
    d = pq(url=host + page_url)
    # 分类
    catalog = d(".list-inline li:last").text()

    # 产品信息
    product_info = {}
    for p in d(".goods-introudce a"):
        this = pq(p)
        product_info[this.text()] = this.attr("href")

    result = []
    for product, url in product_info.items():
        time.sleep(0.5)
        dd = pq(url=host + url)
        for item in dd('.product-color-select').find('.sub-menu.tinyscrollbar li'):
            id = pq(item).attr('code')
            name = pq(item).find('span:last').text().split(" ")
            color_no, name = name[0], ''.join(name[1:])

            img = pq(item).find('img').attr('src')
            response = requests.get(img)
            image = Image.open(BytesIO(response.content))
            pixel = image.getpixel((1, 1))
            colour = "#" + "".join(list(map(lambda x: str(hex(x)).replace("0x", "").zfill(2), pixel)))
            del image, pixel

            result.append({
                'id': id,
                'catalog': catalog,
                'url': host + '/item/' + id,
                'product': product,
                'colour': colour,
                'color_no': color_no,
                'name': name,
                'img': img,
            })
    return result


ysl = []
ysl += get_product('/makeup-lipstick')
ysl += get_product('/makeup-lip-vernis')
ysl += get_product('/makeup-lipoil')
ysl += get_product('/makeup-kiss_brush')
with codecs.open("ysl.json", 'w', encoding='utf-8') as json_file:
    json.dump(ysl, json_file, ensure_ascii=False)
