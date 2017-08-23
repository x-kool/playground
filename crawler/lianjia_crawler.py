import json
import threading

from constant import process_num, lianjia_2nd_community_url_pattern, source_name_lianjia, second_hand
from util import get_rect_list_with_city_name, get_response_text_with_url, get_raw_data_file_path, \
    save_raw_data_in_tsv_file


def crawl_lianjia_raw_data(city_name):
    crawl_lianjia_second_hand_community_raw_data(city_name)
    crawl_lianjia_new_community_raw_data()


def crawl_lianjia_new_community_raw_data():
    pass


def crawl_lianjia_second_hand_community_raw_data(city_name):
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
        community_list = get_lianjia_2nd_community_list_with_rect(rect)
        for community in community_list:
            file_path = get_raw_data_file_path(city_name, source_name_lianjia, second_hand)
            save_raw_data_in_tsv_file(file_path, community)


def get_lianjia_2nd_community_list_with_rect(rect):
    rect_url = get_lianjia_2nd_community_list_url(rect)
    response_text = get_response_text_with_url(rect_url)
    if response_text:
        text_json = json.loads(response_text[43:-1])
        if text_json and 'data' in text_json.keys():
            return text_json['data']
    return []


def get_lianjia_2nd_community_list_url(rect):
    url = lianjia_2nd_community_url_pattern.format(rect[0],rect[2],rect[1],rect[3])
    return url

if __name__ == '__main__':
    crawl_lianjia_second_hand_community_raw_data('重庆')