"""
作为安居客二手房信息的有效补充，可以提供 [户型-面积-楼层总数] 等信息
通过楼盘id可以和二手房信息一一对应，有待整合
"""
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
            rect_list.append(['%.6f' % (lat - dist_lat - distance_unit),
                              '%.6f' % (lat - dist_lat),
                              '%.6f' % (lng - dist_lng - distance_unit),
                              '%.6f' % (lng - dist_lng)])

            rect_list.append(['%.6f' % (lat - dist_lat - distance_unit),
                              '%.6f' % (lat - dist_lat),
                              '%.6f' % (lng + dist_lng),
                              '%.6f' % (lng + dist_lng + distance_unit)])

            rect_list.append(['%.6f' % (lat + dist_lat),
                              '%.6f' % (lat + dist_lat + distance_unit),
                              '%.6f' % (lng - dist_lng - distance_unit),
                              '%.6f' % (lng - dist_lng)])

            rect_list.append(['%.6f' % (lat + dist_lat),
                              '%.6f' % (lat + dist_lat + distance_unit),
                              '%.6f' % (lng + dist_lng),
                              '%.6f' % (lng + dist_lng + distance_unit)])


def get_url(rect):  # 这个base_url 区别于 facet 的小区信息，这个是该区域内在售的单套信息
    base_url = 'https://chongqing.anjuke.com/v3/ajax/map/sale/prop_list/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p=1&zoom=16&' \
               'lat={}_{}&lng={}_{}&kw=&maxp=99'
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
    with open('%s二手房单套信息(安居客)' % name, 'a', encoding='utf-8') as file:
        print('正在写入：{}'.format(str(info_to_string(community))))
        file.write(info_to_string(community))


def parse_info(html):
    if html:
        content = json.loads(html)
        if content and 'val' in content:
            text = content['val']['props']
            return text
    return None


def info_to_string(community):
    space_num = 21 if len(community['comm_name']) == 3 else 20
    line = '\t'.join(
        [myAlign(community['comm_name'], space_num),
         myAlign('%-20s' % (community['comm_id']), 20),
         myAlign('%-6s' % (community['area']), 20),
         myAlign('%-20s' % (community['rhval']), 20),
         myAlign('%-20s' % (community['floor_tag']), 20)]
    )
    return line + '\n'


def get_all_community_price_info(rect_list):
    get_rects_by_center()
    for rect in rect_list:
        rect_url = get_url(rect)
        html = get_info(rect_url)
        data = parse_info(html)
        if data:
            for single_prop in data:
                save_and_write_community_info(single_prop)


def main():
    get_all_community_price_info(rect_list)


if __name__ == '__main__':
    main()
