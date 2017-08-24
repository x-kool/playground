import json
import os
import re

import tablib
import time

from crawler.base_crawler import CrawlerSourceName, CrawlerDataType
from util import get_raw_data_file_path, get_date, isWindowsSystem


def process_anjuke_new_community_raw_data(city_name):
    line_list = get_line_list(city_name)
    for line in line_list:
        data = filter_for_anjuke_new_community_raw_data(line)
        file_path = get_ready_data_file_path(city_name, CrawlerSourceName.ANJUKE.value, CrawlerDataType.NEW_COMMUNITY.value)
        save_ready_data_in_tsv_file(file_path, data)


def filter_for_anjuke_new_community_raw_data(raw_data_line):
    residence_info = raw_data_line[33]
    pattern = re.compile("'alias': '(.*?)'.*?'area': '(.*?)',")
    residence_info_ready = re.findall(pattern, residence_info)
    data = {'loupan_name': raw_data_line[8],
            'loupan_id': raw_data_line[6],
            'build_type': raw_data_line[16],
            'lat': raw_data_line[18],
            'lng': raw_data_line[19],
            'address': raw_data_line[10],
            'fitment_type': raw_data_line[15],
            'new_price': raw_data_line[4],
            'is_sales_promotion': raw_data_line[32],
            'kaipan_new_date': raw_data_line[23],
            'residence_info': str(residence_info_ready)
            }
    return data


def get_line_list(city_name):
    file_path = get_raw_data_file_path(city_name, CrawlerSourceName.ANJUKE.value, CrawlerDataType.NEW_COMMUNITY.value)
    with open(file_path, 'r', encoding='utf-8') as file:
    #with open(file_path, 'r') as file:
        line_list = []
        for line in file.readlines():
            if line != '\n':
                line_list.append(line)
    new_line_list = [line.split('\t') for line in line_list]
    return new_line_list


def get_ready_data_file_path(city_name, source_name, data_type_label):
    date = get_date()
    path = os.path.join(os.path.dirname(os.getcwd()), 'ready_data', city_name, str(date))
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = path + '\{}_{}_{}_{}.txt'.format(city_name, source_name, data_type_label, date)
    if not isWindowsSystem():
        Linux_file_path = file_path.replace('\\', '/')
        return Linux_file_path
    return file_path


def save_ready_data_in_tsv_file(file_path, data):
    formed_data = tablib.Dataset(data.values())
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(formed_data.tsv)

if __name__ == '__main__':
    start = time.clock()

    process_anjuke_new_community_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))