import requests
import time
from requests import RequestException

from constant import city_center_base_url, ak, timeout, steps, distance_unit


def get_city_center(city_name):
    city_url = city_center_base_url.format(city_name, ak)
    try:
        r = requests.get(city_url, timeout=timeout).json()
        return r['result']['location']
    except:
        raise ConnectionError


def get_rects_by_center(location):
    lng = location['lng']  # city center [lat, lng]
    lat = location['lat']
    # 经纬度+-1.2度范围
    rect_list = []
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
    return rect_list


def get_rect_list(city_name):
    location = get_city_center(city_name)
    rect_list = get_rects_by_center(location)
    return rect_list


def get_html(self, url):
    try:
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('链接错误')
        return None


def get_date():
    date = time.strftime("%Y_%m_%d", time.localtime())
    return date