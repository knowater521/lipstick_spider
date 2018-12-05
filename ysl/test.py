# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq

if __name__ == "__main__":
    d = pq(url='https://www.yslbeautycn.com/plp/list.json?ni=15&s=category_order_14_desc%2Cdefault_sort_asc&pn=1&pageSize=20')
    a = d(".goods-introudce a")
    print(len(a))
    for aa in a:
        print(pq(aa).attr('href'))