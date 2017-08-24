import json
import re
import time

from constant import lianjia_second_hand_community_url_pattern, LIANJIA_SOURCE_NAME, SECOND_HAND_COMMUNITY_LABEL, \
    cq_url_for_lianjia_city_list, \
    lianjia_new_community_url_pattern, NEW_COMMUNITY_LABEL, STEP_NUM
from util import get_response_text_with_url, get_raw_data_file_path, \
    save_raw_data_in_tsv_file, crawl_raw_data_by_thread_with_rect_list_func_and_city_name


def crawl_lianjia_raw_data(city_name):
    crawl_lianjia_second_hand_community_raw_data(city_name)
    crawl_lianjia_new_community_raw_data(city_name)


def crawl_lianjia_second_hand_community_raw_data(city_name):
    crawl_raw_data_by_thread_with_rect_list_func_and_city_name(crawl_raw_data_with_rect_list, city_name)


def crawl_lianjia_new_community_raw_data(city_name):
    city_url = get_city_url_for_lianjia(city_name)
    community_data = get_lianjia_new_community_data_with_url(city_url)
    for community_list in community_data.values():
        for community in community_list:
            data = filter_for_lianjia_new_community_raw_data(community)
            file_path = get_raw_data_file_path(city_name, LIANJIA_SOURCE_NAME, NEW_COMMUNITY_LABEL)
            save_raw_data_in_tsv_file(file_path, data)


# == helper ==
def get_lianjia_new_community_data_with_url(url):
    text = get_response_text_with_url(url)
    if text:
        data = json.loads(text[20:-1])
        if data and 'data' in data.keys():
            return data['data']
    return []


def get_city_url_for_lianjia(city_name):
    short_city_name = get_short_city_name_for_lianjia_new_community(city_name)
    city_url = lianjia_new_community_url_pattern.format(short_city_name)
    return city_url


def get_short_city_name_for_lianjia_new_community(city_name):
    text = get_response_text_with_url(cq_url_for_lianjia_city_list)
    pattern = re.compile('<li><a href="//(.*?).fang.lianjia.com/ditu/" data-xftrack="10140">(.*?)</a></li>')
    cities = re.findall(pattern, text)
    city_dict = {}
    for city in cities:
        city_dict[city[1]] = (city[0])
    city_dict['重庆'] = 'cq'
    return city_dict[city_name]


def crawl_raw_data_with_rect_list(rect_list, city_name):
    for idx,rect in enumerate(rect_list):
        community_list = get_lianjia_second_hand_community_list_with_rect(rect)
        for community in community_list:
            file_path = get_raw_data_file_path(city_name, LIANJIA_SOURCE_NAME, SECOND_HAND_COMMUNITY_LABEL)
            save_raw_data_in_tsv_file(file_path, community)
        print(str(idx) + '/' + str(STEP_NUM**2))


def get_lianjia_second_hand_community_list_with_rect(rect):
    rect_url = lianjia_second_hand_community_url_pattern.format(rect[0],rect[2],rect[1],rect[3])
    response_text = get_response_text_with_url(rect_url)
    if response_text:
        text_json = json.loads(response_text[43:-1])
        if text_json and 'data' in text_json.keys():
            return text_json['data']
    return []


def filter_for_lianjia_new_community_raw_data(community):
    data = {'community_name': community['resblock_name'],
            'community_id': community['district_id'],
            'lat': community['latitude'],
            'lng': community['longitude'],
            'avg_price': community['average_price'],
            'residence': community['rooms'],
            'frame_area': community['resblock_frame_area'],
            'min_frame_area': community['min_frame_area'],
            'max_frame_area': community['max_frame_area']}
    return data


'''
if __name__ == '__main__':
    start = time.clock()
    # crawl_lianjia_second_hand_community_raw_data('重庆')
    crawl_lianjia_new_community_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''