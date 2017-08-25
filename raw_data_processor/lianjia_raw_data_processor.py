import time
import pandas as pd

from crawler.crawler_enum import CrawlerSourceName, CrawlerDataLabel, CrawlerDataType
from util import get_file_path


def process_lianjia_new_community_raw_data(city_name):
    read_file_path = get_file_path(city_name,
                                   CrawlerDataType.RAW_DATA.value,
                                   CrawlerSourceName.LIANJIA.value,
                                   CrawlerDataLabel.NEW_COMMUNITY.value)
    save_file_path = get_file_path(city_name,
                                   CrawlerDataType.READY_DATA.value,
                                   CrawlerSourceName.LIANJIA.value,
                                   CrawlerDataLabel.NEW_COMMUNITY.value)
    raw_data = pd.read_table(read_file_path)
    ready_data = process_raw_data_to_ready(raw_data)
    ready_data.to_csv(path_or_buf=save_file_path, sep='\t', encoding='utf-8')


def process_raw_data_to_ready(raw_data):
    ready_data = raw_data[['resblock_name',
                           'house_type',
                           'resblock_id',
                           'latitude',
                           'longitude',
                           'average_price',
                           'rooms',
                           'resblock_frame_area',
                           'min_frame_area',
                           'max_frame_area']]
    return ready_data

#'''
if __name__ == '__main__':
    start = time.clock()
    process_lianjia_new_community_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''