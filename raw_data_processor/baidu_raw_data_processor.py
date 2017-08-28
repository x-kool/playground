import time
import pandas as pd
import json

from constant import BAIDU_POI_READY_DATA_HEADER_LIST
from crawler.crawler_enum import CrawlerSourceName, CrawlerDataLabel, CrawlerDataType
from util import get_file_path

def process_baidu_poi_raw_data(city_name):
    read_file_path = get_file_path(city_name,
                                   CrawlerDataType.RAW_DATA.value,
                                   CrawlerSourceName.BAIDU.value,
                                   CrawlerDataLabel.BAIDU_POI.value)
    save_file_path = get_file_path(city_name,
                                   CrawlerDataType.READY_DATA.value,
                                   CrawlerSourceName.BAIDU.value,
                                   CrawlerDataLabel.BAIDU_POI.value)
    raw_data = pd.read_table(read_file_path, error_bad_lines=False)
    ready_data = process_raw_data_to_ready(raw_data)
    ready_data.to_csv(path_or_buf=save_file_path, sep='\t', encoding='utf-8')


def process_raw_data_to_ready(raw_data):
    add_category_column_from_detail_info(raw_data)
    add_type_column_from_detail_info(raw_data)
    add_lat_column_from_location(raw_data)
    add_lng_column_from_location(raw_data)
    ready_data = raw_data[BAIDU_POI_READY_DATA_HEADER_LIST]
    return ready_data


def add_category_column_from_detail_info(raw_data):
    new_column = list(map(transfer_detail_info_to_category, raw_data['detail_info']))
    raw_data['category'] = new_column


def add_type_column_from_detail_info(raw_data):
    new_column = list(map(transfer_detail_info_to_type, raw_data['detail_info']))
    raw_data['type'] = new_column


def add_lat_column_from_location(raw_data):
    new_column = list(map(transfer_lat_from_location, raw_data['location']))
    raw_data['lat'] = new_column


def add_lng_column_from_location(raw_data):
    new_column = list(map(transfer_lng_from_location, raw_data['location']))
    raw_data['lng'] = new_column


def transfer_lat_from_location(location):
    if type(location) == str:
        location_to_json_loads = location.replace("'", '"')
        try:
            location_dict = json.loads(location_to_json_loads)
            if 'lat' in location_dict.keys():
                return location_dict['lat']
        except:
            pass
    return ''


def transfer_lng_from_location(location):
    if type(location) == str:
        location_to_json_loads = location.replace("'", '"')
        try:
            location_dict = json.loads(location_to_json_loads)
            if 'lng' in location_dict.keys():
                return location_dict['lng']
        except:
            pass
    return ''


def transfer_detail_info_to_category(detail):
    if type(detail) == str:
        detail_to_json_loads = detail.replace("'", '"')
        try:
            detail_dict = json.loads(detail_to_json_loads)
            if 'tag' in detail_dict.keys():
                return detail_dict['tag']
        except:
            pass
    return ''


def transfer_detail_info_to_type(detail):
    if type(detail) == str:
        detail_to_json_loads = detail.replace("'", '"')
        try:
            detail_dict = json.loads(detail_to_json_loads)
            if 'type' in detail_dict.keys():
                return detail_dict['type']
        except:
            pass
    return ''

#'''
if __name__ == '__main__':
    start = time.clock()
    process_baidu_poi_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''