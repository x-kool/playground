import re
import threading
from bs4 import BeautifulSoup
import time

from constant import FANGTIANXIA_CITY_NUM_TRANSFER, fangtianxia_page_url_pattern, fangtianxia_parcel_url_pattern, THREAD_NUM, \
    FANGTIANXIA_SOURCE_NAME, PARCEL_LABEL
from util import get_response_text_with_url, get_raw_data_file_path, save_raw_data_in_tsv_file


def crawl_fangtianxia_parcel_raw_data(city_name):
    url_list = get_parcel_url_list(city_name)
    len_of_sub_url_list_for_thread = int(len(url_list) / THREAD_NUM)
    thread_list = []
    for i in range(THREAD_NUM):
        thread = threading.Thread(target=crawl_parcel_raw_data_with_parcel_url_list,
                                   args=(url_list[i * len_of_sub_url_list_for_thread: (i+1) * len_of_sub_url_list_for_thread],
                                         city_name))
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()


def crawl_parcel_raw_data_with_parcel_url_list(url_list, city_name):
    for parcel_url in url_list:
        parcel_raw_data = get_parcel_raw_data_with_parcel_url(parcel_url)
        file_path = get_raw_data_file_path(city_name, FANGTIANXIA_SOURCE_NAME, PARCEL_LABEL)
        save_raw_data_in_tsv_file(file_path, parcel_raw_data)


def get_parcel_raw_data_with_parcel_url(parcel_url):
    text = get_response_text_with_url(parcel_url)
    soup = BeautifulSoup(text)
    parcel_data = {}
    # 基础信息&交易信息
    for data_part_index in range(2):
        for detail_data in soup.select('table[class="tablebox02 mt10"]')[data_part_index].select('td'):
            key_content = detail_data.contents[0].string[:-1]
            value_content = detail_data.contents[1].string
            parcel_data[key_content] = value_content
    # 经纬度信息+地块编号
    pattern = re.compile('pointX = "(.*?)";')
    lng = re.findall(pattern, text)[0]
    parcel_data['lng'] = lng

    pattern = re.compile('pointY = "(.*?)";')
    lat = re.findall(pattern, text)[0]
    parcel_data['lat'] = lat

    pattern = re.compile('地块编号：(.*?)</span>')
    num_of_parcel = re.findall(pattern, text)[0]
    parcel_data['地块编号'] = num_of_parcel
    return parcel_data


def get_parcel_url_list(city_name):
    page_size = get_page_size(city_name)
    parcel_url_list = []
    for page_num in range(1, page_size+1):
        url = fangtianxia_page_url_pattern.format(FANGTIANXIA_CITY_NUM_TRANSFER[city_name], page_num)
        text = get_response_text_with_url(url)
        soup = BeautifulSoup(text)
        for i in soup.select('h3'):
            parcel_url = fangtianxia_parcel_url_pattern + i.contents[1]['href']
            parcel_url_list.append(parcel_url)
    return parcel_url_list


def get_page_size(city_name):
    city_name_num = FANGTIANXIA_CITY_NUM_TRANSFER[city_name]
    url = fangtianxia_page_url_pattern.format(str(city_name_num), '1')
    text = get_response_text_with_url(url)
    pattern = re.compile('</a><span>1/(.*?)</span><a class="paga28')
    page_size = re.findall(pattern, text)[0]
    return int(page_size)

'''
if __name__ == '__main__':
    start = time.clock()
    crawl_fangtianxia_parcel_raw_data('重庆')
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''