# -*- coding: utf-8 -*-

import os
import re
import shutil
import uuid
import json
import codecs
from io import BytesIO

import requests
from PIL import Image
from pyquery import PyQuery as pq

host = "https://www.dior.cn"


def get_product(goods_url_list, catalog_name):
    brand_code = 'dior'
    brand_name = '迪奥'

    result = []

    for goods_url in goods_url_list:
        try:
            print("goods:" + goods_url)
            sku_page = pq(url=host + goods_url)
            script = sku_page.find("script")
            for s in script:
                def find_index(elements, type):
                    for index in range(len(elements)):
                        if elements[index]['type'] == type:
                            return index
                    return -1

                script_text = pq(s).text()
                if 'window.initialState = ' in script_text:
                    script_text = script_text.replace('window.initialState = ', '')
                    jo = json.loads(script_text)
                    elements = jo['CONTENT']['cmsContent']['elements']
                    goods_code = re.findall('^/zh_cn/products/([^-]*)-([^-]*)', goods_url)[0][1]
                    goods_name = elements[find_index(elements, 'PRODUCTTITLE')]['title']
                    illustration = elements[find_index(elements, 'PRODUCTTITLE')]['subtitle']

                    variations = elements[find_index(elements, 'PRODUCTVARIATIONS')]['variations']
                    # img
                    sku_img_map = {}
                    images = elements[find_index(elements, 'PRODUCTIMAGES')]['images']
                    for img in images:
                        if img['target'] == 'MOBILE':
                            if 'sku' in img:
                                sku = img['sku']
                            elif len(variations) == 1:
                                sku = variations[0]['sku']
                            if sku:
                                if sku not in sku_img_map:
                                    sku_img_map[sku] = []
                                sku_img_map[sku].append(host + img['uri'])

                    # sku
                    for v in variations:
                        sku_code = v['sku']
                        print("sku:" + sku_code)
                        sku_url = goods_url
                        sku_title = v['title'].split(" ")
                        color_card_url = host + v['image']['uri']
                        rgb_img_response = requests.get(color_card_url)
                        image = Image.open(BytesIO(rgb_img_response.content))
                        if image.mode == 'P':
                            image = image.convert("RGB")
                        pixel0 = image.getpixel((1, 1))
                        pixel1 = image.getpixel((1, image.size[1] - 2))
                        colour0 = "#" + "".join(list(map(lambda x: str(hex(x)).replace("0x", "").zfill(2), pixel0)))
                        colour1 = "#" + "".join(list(map(lambda x: str(hex(x)).replace("0x", "").zfill(2), pixel1)))

                        color_no, sku_name = '#' + sku_title[0], ' '.join(sku_title[1:])
                        if sku_name:
                            sku_img_urls, sku_img_downloads, sku_img_urls = [], [], sku_img_map[sku_code]
                            if sku_img_urls:
                                for sku_img_url in sku_img_urls:
                                    uuid_str = uuid.uuid4().hex
                                    sku_img_file = uuid_str + '.png'
                                    sku_img_downloads.append(sku_img_file)
                                    with codecs.open("./img/" + sku_img_file, 'wb') as img_file:
                                        img_file.write(BytesIO(requests.get(sku_img_url).content).read())
                            result.append({
                                'brand_code': brand_code,
                                'brand_name': brand_name,
                                'catalog_name': catalog_name,
                                'goods_code': goods_code,
                                'goods_name': goods_name,
                                'goods_url': host + '/' + goods_url,
                                'goods_illustration': illustration,
                                'sku_code': sku_code,
                                'sku_name': sku_name,
                                'sku_url': sku_url,
                                'sku_img_urls_array': sku_img_urls,
                                'sku_img_urls': ",".join(sku_img_urls),
                                'sku_img_downloads_array': sku_img_downloads,
                                'sku_img_downloads': ",".join(sku_img_downloads),
                                'color_no': color_no,
                                'color_card_url': color_card_url,
                                'colour': colour0,
                                'colour1': colour1,
                            })
        except Exception as e:
            print(e)
    return result


def find_goods_list(page_url):
    print("page:" + page_url)
    list_page = pq(url=host + page_url)
    goods = list_page(".grid-view .is-product")
    goods_url_list = []
    for g in goods:
        goods_url_list.append(pq(g).find('.product-link').attr('href'))
    return goods_url_list


if os.path.exists('./img/'):
    shutil.rmtree("./img/")
os.mkdir("./img/")

dior = []
dior += get_product(find_goods_list('/zh_cn/女士/彩妆/唇妆/唇膏'), '唇膏')
dior += get_product(find_goods_list('/zh_cn/女士/彩妆/唇妆/唇彩'), '唇彩')
dior += get_product(find_goods_list('/zh_cn/女士/彩妆/唇妆/唇线'), '唇线')
dior += get_product([
    '/zh_cn/products/beauty-Y0028888-%E9%AD%85%E6%83%91%E7%A3%A8%E7%A0%82%E7%BE%8E%E5%94%87%E8%86%8F-%E9%99%90%E9%87%8F%E7%89%88-%E8%BD%BB%E8%BD%BB%E4%B8%80%E6%8A%BF%EF%BC%8C%E6%9F%94%E5%94%87%E7%84%95%E7%8E%B0'],
    '唇膏')
dior += get_product([
    '/zh_cn/products/beauty-Y0028880-dior%E8%BF%AA%E5%A5%A5%E9%AD%85%E6%83%91%E7%A3%A8%E7%A0%82%E7%BE%8E%E5%94%87%E8%86%8F-%E8%BD%BB%E8%BD%BB%E4%B8%80%E6%8A%BF%EF%BC%8C%E6%9F%94%E5%94%87%E7%84%95%E7%8E%B0'],
    '唇膏')
with codecs.open("dior.json", 'w', encoding='utf-8') as json_file:
    json.dump(dior, json_file, ensure_ascii=False)
