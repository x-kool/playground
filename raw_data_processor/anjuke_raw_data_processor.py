import re
import time
import pandas as pd

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
    raw_data = pd.read_table(read_file_path)
    ready_data = process_raw_data_to_ready(raw_data)
    ready_data.to_csv(path_or_buf=save_file_path, sep='\t', encoding='utf-8')


def process_raw_data_to_ready(raw_data):
    transfer_house_type(raw_data)
    ready_data = raw_data[['address',
                           'baidu_lat',
                           'baidu_lng',
                           'build_type',
                           'developer',
                           'fitment_type',
                           'house_types',
                           'kaipan_new_date',
                           'loupan_id',
                           'loupan_name',
                           'metro_info',
                           'new_price',
                           'prop_num',
                           'region_title',
                           'sub_region_title']]
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
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''