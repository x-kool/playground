import time
import pandas as pd

from crawler.crawler_enum import CrawlerSourceName, CrawlerDataLabel, CrawlerDataType
from util import get_file_path

def process_fangtianxia_parcel_raw_data(city_name):
    read_file_path = get_file_path(city_name,
                                   CrawlerDataType.RAW_DATA.value,
                                   CrawlerSourceName.FANGTIANXIA.value,
                                   CrawlerDataLabel.PARCEL.value)
    save_file_path = get_file_path(city_name,
                                   CrawlerDataType.READY_DATA.value,
                                   CrawlerSourceName.FANGTIANXIA.value,
                                   CrawlerDataLabel.PARCEL.value)
    raw_data = pd.read_table(read_file_path, error_bad_lines=False)
    ready_data = process_raw_data_to_ready(raw_data)
    ready_data.to_csv(path_or_buf=save_file_path, sep='\t', encoding='utf-8')

def process_raw_data_to_ready(raw_data):
    ready_data = raw_data[['地区',
                           '总面积',
                           '建设用地面积',
                           '规划建筑面积',
                           '容积率',
                           '绿化率',
                           '商业比例',
                           '建筑密度',
                           '限制高度',
                           '出让形式',
                           '出让年限',
                           '位置',
                           '规划用途',
                           '起始日期',
                           '起始价',
                           '成交价',
                           '楼面地价',
                           '溢价率',
                           'lng',
                           'lat',
                           '地块编号']]
    return ready_data

    # '''
if __name__ == '__main__':
    start = time.clock()
    # process_anjuke_new_community_raw_data('重庆')
    process_fangtianxia_parcel_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
    # '''