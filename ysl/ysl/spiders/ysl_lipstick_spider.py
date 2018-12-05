# -*- coding: utf-8 -*-

import scrapy


class YslLipstickSpider(scrapy.Spider):
    name = 'Ysl'
    start_url = ['https://www.yslbeautycn.com/plp/list.json?ni=15&s=category_order_14_desc%2Cdefault_sort_asc&pn=1&pageSize=20']

    def parse(self, response):
        # 从页面中取出页码里包含的链接
        for page_url in response.css('a[title ~= page]::attr(href)').extract():
            page_url = response.urljoin(page_url)
            # 将解析出的href里的链接自动判断补全
            yield scrapy.Request(url=page_url, callback=self.parse)
            # 由解析出的url生成新的请求对象
