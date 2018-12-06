# -*- coding: utf-8 -*-
import time
from pyquery import PyQuery as pq

if __name__ == "__main__":
    host = "https://www.yslbeautycn.com"
    d = pq(url=host + '/makeup-lipstick')
    # 分类
    catalog = d(".list-inline li:last").text()

    # 产品信息
    productInfo = {}
    for p in d(".goods-introudce a"):
        this = pq(p)
        productInfo[this.text()] = this.attr("href")

    res = []
    for product, url in productInfo.items():
        time.sleep(0.5)
        dd = pq(url=host + url)
        details = {}
        for item in dd('.product-color-select').find('.sub-menu.tinyscrollbar li'):
            that = pq(item)
            name = pq(item).find('span:last').text().split(" ")
            color_number, name = name[0], ''.join(name[1:])
            res.append({
                'id': that.attr('code'),
                'catalog': catalog,
                'url': url,
                'product': product,
                'color_number': color_number,
                'name': name,
                'img': pq(item).find('img').attr('src'),
            })
    print(res)
