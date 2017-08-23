import json
import threading
from pypinyin import lazy_pinyin

from constant import process_num, source_name_anjuke, second_hand, anjuke_2nd_community_url_pattern
from util import save_raw_data_in_tsv_file, get_response_text_with_url, get_rect_list_with_city_name, \
    get_raw_data_file_path


def crawl_anjuke_raw_data(city_name):
    crawl_anjuke_second_hand_apt_raw_data(city_name)
    crawl_anjuke_new_apt_raw_data()
    crawl_anjuke_second_hand_single_apt_raw_data()


# TODO(Ke) 把四部分数据和后面的接口打通以后，补充新楼盘和单套二手房信息
def crawl_anjuke_new_apt_raw_data():
    pass

def crawl_anjuke_second_hand_single_apt_raw_data():
    pass

def crawl_anjuke_second_hand_apt_raw_data(city_name):
    rect_list = get_rect_list_with_city_name(city_name)
    len_of_sub_rect_list_for_thread = int(len(rect_list) / process_num)
    process_list = []
    for i in range(process_num):
        process = threading.Thread(target=crawl_raw_data_with_rect_list,
                                   args=(rect_list[i * len_of_sub_rect_list_for_thread: (i + 1) * len_of_sub_rect_list_for_thread],
                                         city_name))
        process.start()
        process_list.append(process)
    for process in process_list:
        process.join()

# == helper ==
def crawl_raw_data_with_rect_list(rect_list, city_name):
    for rect in rect_list:
        community_list = get_anjuke_2nd_community_list_with_rect(city_name, rect)
        for community in community_list:
            file_path = get_raw_data_file_path(city_name, source_name_anjuke, second_hand)
            save_raw_data_in_tsv_file(file_path, community)


def get_anjuke_2nd_community_list_url(city_name, rect):
    city_name_pinyin = ''.join(lazy_pinyin(city_name))
    url = anjuke_2nd_community_url_pattern.format(city_name_pinyin, rect[1], rect[3], rect[0], rect[2])
    return url


def get_anjuke_2nd_community_list_with_rect(city_name, rect):
    rect_url = get_anjuke_2nd_community_list_url(city_name, rect)
    response_text = get_response_text_with_url(rect_url)
    if response_text:
        content = json.loads(response_text)
        if content and 'val' in content:
            text = content['val']['comms']
            return text
    return []

