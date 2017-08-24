import json
import time
from pypinyin import lazy_pinyin

from constant import source_name_anjuke, second_hand, anjuke_2nd_community_url_pattern, \
    anjuke_new_community_url_pattern, first_hand
from util import save_raw_data_in_tsv_file, get_response_text_with_url, get_raw_data_file_path, \
    crawl_raw_data_with_thread


def crawl_anjuke_raw_data(city_name):
    crawl_anjuke_second_hand_community_raw_data(city_name)
    crawl_anjuke_new_community_raw_data(city_name)
    crawl_anjuke_second_hand_single_apt_raw_data()


# TODO(Ke) 把四部分数据和后面的接口打通以后，补充单套二手房信息
def crawl_anjuke_new_community_raw_data(city_name):
    crawl_raw_data_with_thread(crawl_new_community_raw_data_with_rect_list, city_name)


def crawl_anjuke_second_hand_community_raw_data(city_name):
    crawl_raw_data_with_thread(crawl_second_community_raw_data_with_rect_list, city_name)


def crawl_anjuke_second_hand_single_apt_raw_data():
    pass


# == helper ==
def crawl_new_community_raw_data_with_rect_list(rect_list, city_name):
    for idx,rect in enumerate(rect_list):
        community_list = get_anjuke_new_community_list_with_rect(rect)
        for community in community_list:
            data = get_useful_element_in_raw_data_for_new_community(community)
            file_path = get_raw_data_file_path(city_name, source_name_anjuke, first_hand)
            save_raw_data_in_tsv_file(file_path, data)
        print(str(idx) + '/' + str(10000))


def get_anjuke_new_community_list_with_rect(rect):
    rect_url = anjuke_new_community_url_pattern.format(*rect)
    response_text = get_response_text_with_url(rect_url)
    if response_text:
        content = json.loads(response_text[43:-1])
        if content and 'result' in content:
            text = content['result']['rows']
            return text
    return []


def crawl_second_community_raw_data_with_rect_list(rect_list, city_name):
    for rect in rect_list:
        community_list = get_anjuke_second_hand_community_list_with_rect(city_name, rect)
        for community in community_list:
            file_path = get_raw_data_file_path(city_name, source_name_anjuke, second_hand)
            save_raw_data_in_tsv_file(file_path, community)


def get_anjuke_second_hand_community_list_url(city_name, rect):
    city_name_pinyin = ''.join(lazy_pinyin(city_name))
    url = anjuke_2nd_community_url_pattern.format(city_name_pinyin, rect[1], rect[3], rect[0], rect[2])
    return url


def get_anjuke_second_hand_community_list_with_rect(city_name, rect):
    rect_url = get_anjuke_second_hand_community_list_url(city_name, rect)
    response_text = get_response_text_with_url(rect_url)
    if response_text:
        content = json.loads(response_text)
        if content and 'val' in content:
            text = content['val']['comms']
            return text
    return []


def get_useful_element_in_raw_data_for_new_community(community):
    residence_info = ','.join(['[户型: %-s  面积: %-2.f ]' % (detail['alias'], float(detail['area'])) for detail in community['house_types']])
    data = {'loupan_name': community['loupan_name'],
            'loupan_id': community['loupan_id'],
            'build_type': community['build_type'],
            'baidu_lat': community['baidu_lat'],
            'baidu_lng': community['baidu_lng'],
            'address': community['address'],
            'fitment_type': community['fitment_type'],
            'new_price': community['new_price'],
            'is_sales_promotion': community['is_sales_promotion'],
            'residence_info': residence_info}
    return data


'''
if __name__ == '__main__':
    start = time.clock()
    crawl_anjuke_new_community_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
'''