# -*- coding: utf-8 -*-

import os
import re
import shutil
import time
import uuid
import json
import codecs
import requests
from pyquery import PyQuery as pq

from PIL import Image
from io import BytesIO

host = "https://www.yslbeautycn.com"


def get_product(page_url):
    list_page = pq(url=host + page_url)
    # 分类
    catalog = list_page(".list-inline li:last").text()

    # 产品信息
    goods_info = {}
    for p in list_page(".goods-introudce a"):
        this = pq(p)
        goods_info[this.text()] = this.attr("href")

    result = []
    for goods_name, goods_url in goods_info.items():  # goods
        goods_code = re.findall('^/item/([^-]*)', goods_url)[0]
        time.sleep(0.5)
        goods_page = pq(url=host + goods_url)
        for item in goods_page('.product-color-select').find('.sub-menu.tinyscrollbar li'):  # sku
            sku_code = pq(item).attr('code')
            print('spider', sku_code)
            sku_list_data = pq(item).find('span:last').text().split(" ")
            color_no, sku_name = sku_list_data[0], ' '.join(sku_list_data[1:])

            # sku_url
            sku_url = host + '/item/' + sku_code
            # sku_img
            # rgb
            rgb_img = pq(item).find('img').attr('src')
            rgb_img_response = requests.get(rgb_img)
            image = Image.open(BytesIO(rgb_img_response.content))
            pixel = image.getpixel((1, 1))
            colour = "#" + "".join(list(map(lambda x: str(hex(x)).replace("0x", "").zfill(2), pixel)))
            del image, pixel

            sku_img_urls, sku_img_downloads, sku_page = [], [], pq(url=sku_url)
            for sku_img_selector in sku_page('.main-box').find('.swiper-lazy'):
                sku_img_url = pq(sku_img_selector).attr('data-src')
                sku_img_urls.append(sku_img_url)
                uuid_str = uuid.uuid4().hex
                sku_img_file = "./img/" + uuid_str + '.jpg'
                sku_img_downloads.append(uuid_str)
                with codecs.open(sku_img_file, 'wb') as img_file:
                    img_file.write(BytesIO(requests.get(sku_img_url).content).read())
            result.append({
                'catalog': catalog,
                'goods_code': goods_code,
                'goods_name': goods_name,
                'goods_url': goods_url,
                'sku_code': sku_code,
                'sku_name': sku_name,
                'sku_url': sku_url,
                'sku_img_urls': sku_img_urls,
                'sku_img_downloads': sku_img_downloads,
                'color_no': color_no,
                'rgb_img': rgb_img,
                'colour': colour,
            })
    return result


if os.path.exists('./img/'):
    shutil.rmtree("./img/")
os.mkdir("./img/")

ysl = []
ysl += get_product('/makeup-lipstick')
ysl += get_product('/makeup-lip-vernis')
ysl += get_product('/makeup-lipoil')
ysl += get_product('/makeup-kiss_brush')
with codecs.open("ysl.json", 'w', encoding='utf-8') as json_file:
    json.dump(ysl, json_file, ensure_ascii=False)
