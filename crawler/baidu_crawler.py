import requests
import time
from retrying import retry

from constant import baidu_poi_categories, ak, baidu_poi_url_pattern, timeout, source_name_baidu, baidu_poi
from util import get_raw_data_file_path, save_raw_data_in_tsv_file, \
    crawl_raw_data_with_thread

# global variable to recognise whether poi is stored
stored_poi_uid_list = []
def crawl_baidu_raw_data(city_name):
    global stored_poi_uid_list
    crawl_raw_data_with_thread(crawl_poi_raw_data_with_rect_list, city_name)


# == helper ==
def crawl_poi_raw_data_with_rect_list(rect_list, city_name):
    for idx,rect in enumerate(rect_list):
        for category in baidu_poi_categories:
            poi_list = get_baidu_poi_list(category, rect)
            for poi in poi_list:
                file_path = get_raw_data_file_path(city_name, source_name_baidu, baidu_poi)
                if poi['uid'] not in stored_poi_uid_list:
                    stored_poi_uid_list.append(poi['uid'])
                    data = get_useful_element_in_raw_data_for_baidu_poi(poi)
                    save_raw_data_in_tsv_file(file_path, data)
        print(str(idx) + '/' + str(10000))


@retry(stop_max_attempt_number=10)
def get_baidu_poi_list(category, rect):
    rect = ','.join([rect[1],rect[0],rect[3],rect[2]])
    poi_url = baidu_poi_url_pattern.format(category, rect, ak)
    try:
        response = requests.get(poi_url, timeout=timeout)
        response_json = response.json()
        return response_json['results']
    except:
        raise ConnectionError


def get_useful_element_in_raw_data_for_baidu_poi(poi):
    data = {'name': poi['name'],
            'lat': poi['location']['lat'],
            'lng': poi['location']['lng'],
            'address': poi['address'],
            'uid': poi['uid']}
    if poi.get('detail_info'):
        tags = poi['detail_info'].get('tag', '其他;其他').split(';')
        data['category'] = tags[0]
        data['sub_category'] = tags[1] if len(tags) > 1 else '其他'
    return data

'''
if __name__ == '__main__':
    start = time.clock()
    crawl_baidu_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
'''