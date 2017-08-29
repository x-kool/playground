import json
import time
from pypinyin import lazy_pinyin
from requests import RequestException

from constant import anjuke_new_community_url_pattern, anjuke_2nd_community_url_pattern, THREAD_NUM, \
    ANJUKE_NEW_COMMUNITY_RAW_DATA_HEADER_LIST, ANJUKE_SECOND_COMMUNITY_RAW_DATA_HEADER_LIST
from crawler.base_crawler import BaseCrawler
from crawler.crawler_enum import CrawlerDataType, CrawlerSourceName, CrawlerDataLabel
from util import get_file_path


class AnjukeCrawler(BaseCrawler):
    def __init__(self, city_name):
        super(AnjukeCrawler, self).__init__(city_name)
        self.lng, self.lat = self.get_city_center_lng_lat_by_city_name(self.city_name)
        self.rect_list = self.new_get_rect_list_by_lng_lat(self.lng, self.lat)

    def crawl_anjuke_raw_data(self):
        self.crawl_anjuke_second_hand_community_raw_data()
        self.crawl_anjuke_new_community_raw_data()

    def crawl_anjuke_new_community_raw_data(self):
        self.crawl_with_thread_pool(THREAD_NUM,
                                    self.crawl_new_community_raw_data_with_rect,
                                    self.rect_list,
                                    self.write_new_community_raw_data_in_rect_to_file)

    def crawl_anjuke_second_hand_community_raw_data(self):
        self.crawl_with_thread_pool(THREAD_NUM,
                                    self.crawl_second_community_raw_data_with_rect,
                                    self.rect_list,
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
        try:
            response_text = self.get_response_text_with_url(rect_url)
            if response_text:
                content = json.loads(response_text[43:-1])
                if content and 'result' in content:
                    text = content['result']['rows']
                    return text
            return []
        except RequestException as msg:
            self.logger.warning('[city name:{0}][exception:{1}][rect:{2}]'.format(self.city_name, msg, rect))

    def get_anjuke_second_hand_community_list_with_rect(self, rect):
        rect_url = self.get_anjuke_second_hand_community_list_url(rect)
        try:
            response_text = self.get_response_text_with_url(rect_url)
            if response_text:
                content = json.loads(response_text)
                if content and 'val' in content:
                    text = content['val']['comms']
                    return text
            return []
        except RequestException as msg:
            self.logger.warning('[city name:{0}][exception:{1}][rect:{2}]'.format(self.city_name, msg, rect))

    def get_anjuke_second_hand_community_list_url(self, rect):
        city_name_pinyin = ''.join(lazy_pinyin(self.city_name))
        url = anjuke_2nd_community_url_pattern.format(city_name_pinyin, rect[1], rect[3], rect[0], rect[2])
        return url

    def write_new_community_raw_data_in_rect_to_file(self, raw_data_list):
        write_file_path = get_file_path(self.city_name,
                                        CrawlerDataType.RAW_DATA.value,
                                        CrawlerSourceName.ANJUKE.value,
                                        CrawlerDataLabel.NEW_COMMUNITY.value)
        self.write_to_file(ANJUKE_NEW_COMMUNITY_RAW_DATA_HEADER_LIST, write_file_path, raw_data_list)

    def write_second_community_raw_data_in_rect_to_file(self, raw_data_list):
        write_file_path = get_file_path(self.city_name,
                                        CrawlerDataType.RAW_DATA.value,
                                        CrawlerSourceName.ANJUKE.value,
                                        CrawlerDataLabel.SECOND_HAND_COMMUNITY.value)
        self.write_to_file(ANJUKE_SECOND_COMMUNITY_RAW_DATA_HEADER_LIST, write_file_path, raw_data_list)

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
