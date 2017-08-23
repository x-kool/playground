import threading
import requests
from retrying import retry

from constant import process_num, baidu_poi_categories, ak, baidu_poi_url_pattern, timeout, source_name_baidu, baidu_poi
from util import get_rect_list_with_city_name, get_raw_data_file_path, save_raw_data_in_tsv_file

# global variable to recognise whether poi is stored
stored_poi_uid_list = []

def crawl_baidu_raw_data(city_name):
    global stored_poi_uid_list
    rect_list = get_rect_list_with_city_name(city_name)
    len_of_sub_rect_list_for_thread = int(len(rect_list) / process_num)

    process_list = []
    for i in range(process_num):
        process = threading.Thread(target=crawl_poi_raw_data_with_rect_list,
                                   args=(rect_list[i*len_of_sub_rect_list_for_thread : (i+1)*len_of_sub_rect_list_for_thread],
                                         city_name))
        process.start()
        process_list.append(process)
    for process in process_list:
        process.join()


# == helper ==
def crawl_poi_raw_data_with_rect_list(rect_list, city_name):
    for rect in rect_list:
        for category in baidu_poi_categories:
            poi_list = get_baidu_poi_list(category, rect)
            for poi in poi_list:
                    file_path = get_raw_data_file_path(city_name, source_name_baidu, baidu_poi)
                    if poi['uid'] not in stored_poi_uid_list:
                        save_raw_data_in_tsv_file(file_path, poi)


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


