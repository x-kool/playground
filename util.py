import json
import requests
import time
import tablib
from requests import RequestException
from retrying import retry

from constant import city_center_base_url, ak, timeout, steps, distance_unit, headers


def get_city_center(city_name):
    city_url = city_center_base_url.format(city_name, ak)
    try:
        response = requests.get(city_url, timeout=timeout)
        response_dict = response.json()
        return response_dict['result']['location']
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


def get_anjuke_2nd_community_info(html):
    if html:
        content = json.loads(html)
        if content and 'val' in content:
            text = content['val']['comms']
            return text
    return None


# TODO city_name 需要转换成全拼
def get_anjuke_2nd_community_url(city_name, rect):
    format_data = [city_name] + rect
    base_url = 'https://{}.anjuke.com/v3/ajax/map/sale/facet/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p=1&zoom=19&' \
               'lat={}_{}&lng={}_{}&kw=&maxp=99'
    url = base_url.format(*format_data)
    return url


def get_date():
    date = time.strftime("%Y_%m_%d", time.localtime())
    return date


def get_tsv_formed_data(community, source, service_life):
    if source == '安居客' and service_life == '二手':
        pre_data = [community['truncate_name'],
                    '%-.6f' % float(community['lat']),
                    '%-.6f' % float(community['lng']),
                    '%-s' % community['address'],
                    '%-s' % community['mid_price'],
                    '%-s' % community['id'],
                    '%-s' % community['prop_num']]
        if community['mid_change']:
            pre_data.append('%-.3f' % (float(community['mid_change'])))
        data = tablib.Dataset(*pre_data)
        return data


def save_and_write_info(city_name, source, service_life, data):
    date = get_date()
    with open('{}_{}_{}_{}'.format(city_name, source, service_life, date), 'a', encoding='utf-8') as file:
        file.write(data.tsv)


