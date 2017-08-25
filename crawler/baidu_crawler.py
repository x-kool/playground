import requests
import time
from retrying import retry

from constant import BAIDU_POI_CATEGORIES, BAIDU_API_AK, baidu_poi_url_pattern, TIMEOUT, BAIDU_SOURCE_NAME, \
    BAIDU_POI_LABEL, STEP_NUM
from util import get_file_path, save_raw_data_in_tsv_file, \
    crawl_raw_data_by_thread_with_rect_list_func_and_city_name

# global variable to recognise whether poi is stored
stored_poi_uid_list = []
def crawl_baidu_raw_data(city_name):
    global stored_poi_uid_list
    crawl_raw_data_by_thread_with_rect_list_func_and_city_name(crawl_poi_raw_data_with_rect_list, city_name)


# == helper ==
def crawl_poi_raw_data_with_rect_list(rect_list, city_name):
    for idx,rect in enumerate(rect_list):
        for category in BAIDU_POI_CATEGORIES:
            poi_list = get_baidu_poi_list(category, rect)
            for poi in poi_list:
                file_path = get_file_path(city_name, BAIDU_SOURCE_NAME, BAIDU_POI_LABEL)
                if poi['uid'] not in stored_poi_uid_list:
                    stored_poi_uid_list.append(poi['uid'])
                    data = filter_for_baidu_poi_raw_data(poi)
                    save_raw_data_in_tsv_file(file_path, data)
        print(str(idx) + '/' + str(STEP_NUM**2))


@retry(stop_max_attempt_number=10)
def get_baidu_poi_list(category, rect):
    poi_url = get_baidu_poi_url(category, rect)
    try:
        response = requests.get(poi_url, timeout=TIMEOUT)
        response_json = response.json()
        return response_json['results']
    except:
        raise ConnectionError


def get_baidu_poi_rect_form(rect):
    formed_rect = ','.join([rect[1], rect[0], rect[3], rect[2]])
    return formed_rect


def get_baidu_poi_url(category, rect):
    formed_rect = get_baidu_poi_rect_form(rect)
    poi_url = baidu_poi_url_pattern.format(category, formed_rect, BAIDU_API_AK)
    return poi_url

def filter_for_baidu_poi_raw_data(poi):
    data = {'name': poi['name'],
            'uid': poi['uid'],
            'lat': poi['location']['lat'],
            'lng': poi['location']['lng']}
    if poi.get('detail_info'):
        tags = poi['detail_info'].get('tag', '其他;其他').split(';')
        data['category'] = tags[0]
        data['sub_category'] = tags[1] if len(tags) > 1 else '其他'
        data['type'] = poi['detail_info']['type'] if poi['detail_info'].get('type') else ''
        data['navi_location'] = poi['detail_info']['navi_location'] if poi['detail_info'].get('navi_location') else ''
    data['address'] = poi['address'] if poi.get('address') else ''
    data['street_id'] = poi['street_id'] if poi.get('street_id') else ''
    return data

#'''
if __name__ == '__main__':
    start = time.clock()
    crawl_baidu_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''