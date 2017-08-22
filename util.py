import time

import requests
from requests import RequestException
from retrying import retry

from constant import city_center_url_pattern, ak, timeout, steps, distance_unit, headers


def get_city_center_lng_lat_by_city_name(city_name):
    city_url = city_center_url_pattern.format(city_name, ak)
    try:
        response = requests.get(city_url, timeout=timeout)
        response_dict = response.json()
        location = response_dict['result']['location']
        return location['lng'], location['lat']
    except:
        raise ConnectionError


def get_rects_by_lng_lat(lng, lat):
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


def get_rect_list_with_city_name(city_name):
    lng, lat = get_city_center_lng_lat_by_city_name(city_name)
    rect_list = get_rects_by_lng_lat(lng, lat)
    return rect_list


@retry(stop_max_attempt_number=10)
def get_response_text_with_url(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('链接错误')
        return None


def get_date():
    date = time.strftime("%Y_%m_%d", time.localtime())
    return date


def get_raw_data_file_path(city_name, source_name, service_life):
    date = get_date()
    file_path = '{}_{}_{}_{}.tsv'.format(city_name, source_name, service_life, date)
    return file_path


def save_raw_data_in_tsv_file(file_path, data):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(data.tsv)
