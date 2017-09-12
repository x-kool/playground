import re
import time
import pandas as pd
from shapely.geos import TopologicalError

from constant import ANJUKE_NEW_COMMUNITY_READY_DATA_HEADER_LIST, ANJUKE_SECOND_COMMUNITY_READY_DATA_HEADER_LIST
from crawler.crawler_enum import CrawlerSourceName, CrawlerDataLabel, CrawlerDataType
from util import get_file_path


def process_anjuke_new_community_raw_data(city_name):
    read_file_path = get_file_path(city_name,
                                   CrawlerDataType.RAW_DATA.value,
                                   CrawlerSourceName.ANJUKE.value,
                                   CrawlerDataLabel.NEW_COMMUNITY.value)
    save_file_path = get_file_path(city_name,
                                   CrawlerDataType.READY_DATA.value,
                                   CrawlerSourceName.ANJUKE.value,
                                   CrawlerDataLabel.NEW_COMMUNITY.value)
    raw_data = pd.read_table(read_file_path, error_bad_lines=False)
    ready_data = process_new_community_raw_data_to_ready(raw_data)
    ready_data.to_csv(path_or_buf=save_file_path, sep='\t', encoding='utf-8')

def process_anjuke_second_hand_community_raw_data(city_name):
    read_file_path = get_file_path(city_name,
                                   CrawlerDataType.RAW_DATA.value,
                                   CrawlerSourceName.ANJUKE.value,
                                   CrawlerDataLabel.SECOND_HAND_COMMUNITY.value)
    save_file_path = get_file_path(city_name,
                                   CrawlerDataType.READY_DATA.value,
                                   CrawlerSourceName.ANJUKE.value,
                                   CrawlerDataLabel.SECOND_HAND_COMMUNITY.value)
    raw_data = pd.read_table(read_file_path, error_bad_lines=False)
    ready_data = process_second_community_raw_data_to_ready(raw_data)
    ready_data.to_csv(path_or_buf=save_file_path, sep='\t', encoding='utf-8')

def process_second_community_raw_data_to_ready(raw_data):
    ready_data = raw_data[ANJUKE_SECOND_COMMUNITY_READY_DATA_HEADER_LIST]
    return ready_data

def process_new_community_raw_data_to_ready(raw_data):
    transfer_house_type(raw_data)
    ready_data = raw_data[ANJUKE_NEW_COMMUNITY_READY_DATA_HEADER_LIST]
    return ready_data

def transfer_house_type(raw_data):
    house_types = raw_data['house_types']
    pattern = re.compile("'alias': '(.*?)'.*?'area': '(.*?)',")
    for idx, house_type in enumerate(house_types):
        residence_info_ready = re.findall(pattern, house_type)
        house_types.loc[idx] = str(residence_info_ready)
        print(idx, str(residence_info_ready))

#'''
if __name__ == '__main__':
    start = time.clock()
    process_anjuke_new_community_raw_data('重庆')
    process_anjuke_second_hand_community_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''


TopologicalError