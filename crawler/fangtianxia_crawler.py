import os
import re
import tablib
import time
from bs4 import BeautifulSoup

from constant import fangtianxia_page_url_pattern, FANGTIANXIA_CITY_NUM_TRANSFER, fangtianxia_parcel_url_pattern, \
    THREAD_NUM
from crawler.base_crawler import BaseCrawler
from crawler.crawler_enum import CrawlerDataType, CrawlerSourceName, CrawlerDataLabel
from util import get_file_path


class FangtianxiaCrawler(BaseCrawler):

    def crawl_fangtianxia_parcel_raw_data(self):
        url_list = self.get_parcel_url_list()
        self.thread_for_crawler(THREAD_NUM,
                                self.get_parcel_raw_data_with_parcel_url,
                                url_list,
                                self.write_parcel_raw_data_in_rect_to_file)

    def get_parcel_raw_data_with_parcel_url(self, parcel_url):
        text = self.get_response_text_with_url(parcel_url)
        if text:
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
            return [parcel_data]

    def get_parcel_url_list(self):
        page_size = self.get_page_size(self.city_name)
        parcel_url_list = []
        for page_num in range(1, page_size + 1):
            url = fangtianxia_page_url_pattern.format(FANGTIANXIA_CITY_NUM_TRANSFER[self.city_name], page_num)
            text = self.get_response_text_with_url(url)
            soup = BeautifulSoup(text)
            for i in soup.select('h3'):
                parcel_url = fangtianxia_parcel_url_pattern + i.contents[1]['href']
                parcel_url_list.append(parcel_url)
        return parcel_url_list

    def get_page_size(self, city_name):
        city_name_num = FANGTIANXIA_CITY_NUM_TRANSFER[city_name]
        url = fangtianxia_page_url_pattern.format(str(city_name_num), '1')
        text = self.get_response_text_with_url(url)
        pattern = re.compile('</a><span>1/(.*?)</span><a class="paga28')
        page_size = re.findall(pattern, text)[0]
        return int(page_size)

    def write_parcel_raw_data_in_rect_to_file(self, raw_data_list):
        write_file_path = get_file_path(self.city_name,
                                        CrawlerDataType.RAW_DATA.value,
                                        CrawlerSourceName.FANGTIANXIA.value,
                                        CrawlerDataLabel.PARCEL.value)
        for raw_data in raw_data_list:
            res_value = list(raw_data.values())
            data_value = tablib.Dataset(res_value)

            res_key = list(raw_data.keys())
            data_key = tablib.Dataset(res_key)

            if not os.path.exists(write_file_path):
                with open(write_file_path, 'a+', encoding='utf-8') as f:
                    f.write(str(data_key.tsv))
                    f.write(str(data_value.tsv))
            else:
                with open(write_file_path, 'a+', encoding='utf-8') as f:
                    f.write(str(data_value.tsv))

#'''
if __name__ == '__main__':
    start = time.clock()
    crawler = FangtianxiaCrawler('重庆')
    crawler.crawl_fangtianxia_parcel_raw_data()
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''