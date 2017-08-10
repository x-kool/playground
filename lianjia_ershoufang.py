# -*- coding: utf-8 -*-
import json

import requests
from requests import RequestException

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
        return  r['result']['location']
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
                              '%.6f' % (lng - dist_lng),
                              '%.6f' % (lat - dist_lat - distance_unit),
                              '%.6f' % (lat - dist_lat)])

            rect_list.append(['%.6f' % (lng + dist_lng),
                              '%.6f' % (lng + dist_lng + distance_unit),
                              '%.6f' % (lat - dist_lat - distance_unit),
                              '%.6f' % (lat - dist_lat)])

            rect_list.append(['%.6f' % (lng - dist_lng - distance_unit),
                              '%.6f' % (lng - dist_lng),
                              '%.6f' % (lat + dist_lat),
                              '%.6f' % (lat + dist_lat + distance_unit)])

            rect_list.append(['%.6f' % (lng + dist_lng),
                              '%.6f' % (lng + dist_lng + distance_unit),
                              '%.6f' % (lat + dist_lat),
                              '%.6f' % (lat + dist_lat + distance_unit)])


def get_url(rect):
    base_url = 'https://ajax.lianjia.com/ajax/mapsearch/area/community?' \
               'min_longitude={}&max_longitude={}&min_latitude={}&max_latitude={}' \
               '&&city_id=500000&callback=jQuery1111026263228440180875_1502180579317&_=1502180579330'
    url = base_url.format(*rect)
    return url


def get_info(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('链接错误')
        return None


def save_and_write_community_info(community, name=city_name):
    with open('%s二手房信息(链家)' % name, 'a', encoding='utf-8') as file:
        print('正在写入：{}'.format(str(info_to_string(community))))
        file.write(info_to_string(community))


def parse_info(html):
    if html:
        data = json.loads(html[43:-1])
        if data and 'data' in data.keys():
            return data['data']
    return None


def info_to_string(community):
    space_num = 21 if len(community['name']) == 3 else 20
    line = '\t'.join(
                     [myAlign(community['name'], space_num),
                      myAlign('%-.6f' % (community['latitude']), 20),
                      myAlign('%-.6f' % (community['longitude']), 20),
                      myAlign('%-6s' % (community['avg_unit_price']), 20),
                      myAlign('%-20s' % (community['id']), 20),
                      myAlign('%-5s' % (community['house_count']), 20),
                      myAlign('%-5d' % (int(community['min_price_total'])), 20)]
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
