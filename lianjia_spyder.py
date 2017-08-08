# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 18:47:00 2017

@author: xcsliu
"""

import json

import requests
from requests import RequestException

rect_candidate = [['106.576825','106.603092','29.531752','29.559465'],
                  ['106.546825','106.576825','29.531752','29.559465']]


ak = 'GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'
city_name = '重庆'
city_center_url = 'https://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'
timeout = 5

steps = 5
distance_unit = 0.005
rects = []


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
            rects.append([str(lng - dist_lng - distance_unit)[:9],
                          str(lng - dist_lng)[:9],
                          str(lat - dist_lat - distance_unit)[:9],
                          str(lat - dist_lat)[:9]])

            rects.append([str(lng + dist_lng)[:9],
                          str(lng + dist_lng + distance_unit)[:9],
                          str(lat - dist_lat - distance_unit)[:9],
                          str(lat - dist_lat)[:9]])

            rects.append([str(lng - dist_lng - distance_unit)[:9],
                          str(lng - dist_lng)[:9],
                          str(lat + dist_lat)[:9],
                          str(lat + dist_lat + distance_unit)[:9]])

            rects.append([str(lng + dist_lng)[:9],
                          str(lng + dist_lng + distance_unit)[:9],
                          str(lat + dist_lat)[:9],
                          str(lat + dist_lat + distance_unit)[:9]])


def get_url(rect):
    base_url = 'https://ajax.lianjia.com/ajax/mapsearch/area/community?min_longitude={}&max_longitude={}&min_latitude={}&max_latitude={}&&city_id=500000&callback=jQuery1111026263228440180875_1502180579317&_=1502180579330'
    url = base_url.format(*rect)
    return url

def get_info(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print ('链接错误')
        return None


def save_and_write_community_info(community):
    with open('重庆商业小区','a') as file:
        print ('正在写入：{}'.format( str( info_to_string(community) ) ))
        file.write(info_to_string(community))


def parse_info(html):
    data = json.loads(html[43:-1])
    if data and 'data' in data.keys():
        return data['data']


def info_to_string(community):
    line = '\t'.join([community['name'],
                      str(community['latitude']),
                      str(community['longitude']),
                      str(community['avg_unit_price']),
                      community['id'],
                      str(community['house_count']),
                      str(community['min_price_total'])
                      ])
    return line + '\n'

def main(rect):
    html = get_info( get_url(rect) )
    data = parse_info(html)
    for community in data:
        save_and_write_community_info(community)

if __name__ == '__main__':
    get_rects_by_center()
    for rect in rects:
        main(rect)

