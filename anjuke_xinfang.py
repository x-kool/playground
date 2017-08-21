import json

import requests
from requests import RequestException

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}

ak = 'GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'
city_name = '重庆'
city_center_url = 'https://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'
timeout = 5

steps = 100
distance_unit = 0.005
rect_list = []


def myAlign(string, length=0):
    if length == 0:
        return string
    slen = len(string)
    re = string
    if isinstance(string, str):
        placeholder = ' '
    else:
        placeholder = u'　'
    while slen < length:
        re += placeholder
        slen += 1
    return re


def get_city_center():
    city_url = city_center_url.format(city_name, ak)
    try:
        r = requests.get(city_url, timeout=timeout).json()
        return r['result']['location']
    except:
        raise ConnectionError


def get_rects_by_center():
    location = get_city_center()
    lng = location['lng']  # city center [lat, lng]
    lat = location['lat']
    # 经纬度+-1.2度范围
    for units_lng in range(steps):
        dist_lng = units_lng * distance_unit
        for units_lat in range(steps):
            dist_lat = units_lat * distance_unit
            rect_list.append(['%.6f' % (lng - dist_lng - distance_unit),
                              '%.6f' % (lat - dist_lat - distance_unit),
                              '%.6f' % (lng - dist_lng),
                              '%.6f' % (lat - dist_lat)])

            rect_list.append(['%.6f' % (lng + dist_lng),
                              '%.6f' % (lat - dist_lat - distance_unit),
                              '%.6f' % (lng + dist_lng + distance_unit),
                              '%.6f' % (lat - dist_lat)])

            rect_list.append(['%.6f' % (lng - dist_lng - distance_unit),
                              '%.6f' % (lat + dist_lat),
                              '%.6f' % (lng - dist_lng),
                              '%.6f' % (lat + dist_lat + distance_unit)])

            rect_list.append(['%.6f' % (lng + dist_lng),
                              '%.6f' % (lat + dist_lat),
                              '%.6f' % (lng + dist_lng + distance_unit),
                              '%.6f' % (lat + dist_lat + distance_unit)])


def get_url(rect):
    base_url = 'https://api.fang.anjuke.com/web/loupan/mapNewlist/?city_id=20&callback=jQuery1113006248457428238563_1502272365154&zoom=16&' \
               'swlng={}&swlat={}&nelng={}&nelat={}&' \
               'order=rank&order_type=asc&region_id=0&sub_region_id=0&house_type=0&property_type=0&price_id=0&bunget_id=0&status_sale=3%2C4%2C6%2C7%2C5&price_title=%E5%85%A8%E9%83%A8&keywords=&page=1&page_size=500&timestamp=29&_=1502272365159'

    url = base_url.format(*rect)
    return url


def get_info(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('链接错误')
        return None


def save_and_write_community_info(community, name=city_name):
    with open('%s楼盘信息(安居客)' % name, 'a', encoding='utf-8') as file:
        print('正在写入：{}'.format(str(info_to_string(community))))
        file.write(info_to_string(community))


def parse_info(html):
    if html:
        content = json.loads(html[43:-1])
        if content and 'result' in content:
            text = content['result']['rows']
            return text
    return None


def info_to_string(community):
    space_num = 21 if len(community['loupan_name']) == 3 else 20
    residence_info = '\t'.join(['[户型: %-s  面积: %-2.f ]' % (i['alias'], float(i['area'])) for i in community['house_types']])

    line = '\t'.join(
        [myAlign(community['loupan_name'], space_num),
         myAlign('%-20s' % (community['loupan_id']), 20),
         myAlign('%-20s' % (community['build_type']), 30),
         myAlign('%-.6f' % (float(community['baidu_lat'])), 20),
         myAlign('%-.6f' % (float(community['baidu_lng'])), 20),
         myAlign('%-20s' % (community['address']), 60),
         myAlign('%-20s' % (community['fitment_type']), 20),
         myAlign('%-6s' % (community['new_price']), 20),
         myAlign('%-5s' % (community['is_sales_promotion']), 20),
         myAlign('%-s' % (residence_info))]
    )
    return line + '\n'


def get_all_community_price_info(rect_list):
    get_rects_by_center()
    for rect in rect_list:
        rect_url = get_url(rect)
        html = get_info(rect_url)
        data = parse_info(html)
        if data:
            for community in data:
                save_and_write_community_info(community)


def main():
    get_all_community_price_info(rect_list)


if __name__ == '__main__':
    main()
