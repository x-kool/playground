import json
import os
import tablib
import time
from pypinyin import lazy_pinyin

from constant import anjuke_new_community_url_pattern, anjuke_2nd_community_url_pattern, THREAD_NUM
from crawler.base_crawler import BaseCrawler
from crawler.crawler_enum import CrawlerDataType, CrawlerSourceName, CrawlerDataLabel
from util import get_file_path


class AnjukeCrawler(BaseCrawler):
    def crawl_anjuke_raw_data(self):
        self.crawl_anjuke_second_hand_community_raw_data()
        self.crawl_anjuke_new_community_raw_data()

    def crawl_anjuke_new_community_raw_data(self):
        lng, lat = self.get_city_center_lng_lat_by_city_name(self.city_name)
        rect_list = self.new_get_rect_list_by_lng_lat(lng, lat)
        self.thread_for_crawler(THREAD_NUM,
                                self.crawl_new_community_raw_data_with_rect,
                                rect_list,
                                self.write_new_community_raw_data_in_rect_to_file)

    def crawl_anjuke_second_hand_community_raw_data(self):
        lng, lat = self.get_city_center_lng_lat_by_city_name(self.city_name)
        rect_list = self.new_get_rect_list_by_lng_lat(lng, lat)
        self.thread_for_crawler(THREAD_NUM,
                                self.crawl_second_community_raw_data_with_rect,
                                rect_list,
                                self.write_second_community_raw_data_in_rect_to_file)

    def crawl_new_community_raw_data_with_rect(self, rect):
        res = []
        community_list = self.get_anjuke_new_community_list_with_rect(rect)
        for community in community_list:
            res.append(community)
        return res

    def crawl_second_community_raw_data_with_rect(self, rect):
        res = []
        community_list = self.get_anjuke_second_hand_community_list_with_rect(rect)
        for community in community_list:
            res.append(community)
        return res

    def get_anjuke_new_community_list_with_rect(self, rect):
        rect_url = anjuke_new_community_url_pattern.format(*rect)
        response_text = self.get_response_text_with_url(rect_url)
        if response_text:
            content = json.loads(response_text[43:-1])
            if content and 'result' in content:
                text = content['result']['rows']
                return text
        return []

    def get_anjuke_second_hand_community_list_with_rect(self, rect):
        rect_url = self.get_anjuke_second_hand_community_list_url(rect)
        response_text = self.get_response_text_with_url(rect_url)
        if response_text:
            content = json.loads(response_text)
            if content and 'val' in content:
                text = content['val']['comms']
                return text
        return []

    def get_anjuke_second_hand_community_list_url(self, rect):
        city_name_pinyin = ''.join(lazy_pinyin(self.city_name))
        url = anjuke_2nd_community_url_pattern.format(city_name_pinyin, rect[1], rect[3], rect[0], rect[2])
        return url

    def write_new_community_raw_data_in_rect_to_file(self, raw_data_list):
        write_file_path = get_file_path(self.city_name,
                                        CrawlerDataType.RAW_DATA.value,
                                        CrawlerSourceName.ANJUKE.value,
                                        CrawlerDataLabel.NEW_COMMUNITY.value)
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

    # 线程池通过回调函数(callback)同步线程写入同一文件的问题
    def write_second_community_raw_data_in_rect_to_file(self, raw_data_list):
        write_file_path = get_file_path(self.city_name,
                                        CrawlerDataType.RAW_DATA.value,
                                        CrawlerSourceName.ANJUKE.value,
                                        CrawlerDataLabel.SECOND_HAND_COMMUNITY.value)
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
    crawler = AnjukeCrawler('重庆')
    # crawler.crawl_anjuke_new_community_raw_data()
    # crawler.crawl_anjuke_second_hand_community_raw_data()
    crawler.crawl_anjuke_raw_data()
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''
