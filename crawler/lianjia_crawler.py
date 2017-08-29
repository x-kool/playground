import json
import re
import time
from requests import RequestException

from constant import lianjia_new_community_url_pattern, cq_url_for_lianjia_city_list, \
    lianjia_second_hand_community_url_pattern, THREAD_NUM, LIANJIA_SECOND_COMMUNITY_RAW_DATA_HEADER_LIST
from crawler.base_crawler import BaseCrawler
from crawler.crawler_enum import CrawlerDataType, CrawlerSourceName, CrawlerDataLabel
from util import get_file_path, save_raw_data_in_tsv_file


class LianjiaCrawler(BaseCrawler):
    def __init__(self, city_name):
        super(LianjiaCrawler, self).__init__(city_name)
        self.lng, self.lat = self.get_city_center_lng_lat_by_city_name(self.city_name)
        self.rect_list = self.new_get_rect_list_by_lng_lat(self.lng, self.lat)

    def crawl_lianjia_raw_data(self):
        self.crawl_lianjia_second_hand_community_raw_data()
        self.crawl_lianjia_new_community_raw_data()

    def crawl_lianjia_new_community_raw_data(self):
        data_dict_list_for_new_community = []
        city_url = self.get_city_url_for_lianjia()
        community_data = self.get_lianjia_new_community_data_with_url(city_url)
        for community_list in community_data.values():
            for community in community_list:
                data_dict_list_for_new_community.append(community)

        file_path = get_file_path(self.city_name,
                                  CrawlerDataType.RAW_DATA.value,
                                  CrawlerSourceName.LIANJIA.value,
                                  CrawlerDataLabel.NEW_COMMUNITY.value)
        save_raw_data_in_tsv_file(file_path, data_dict_list_for_new_community)

    def crawl_lianjia_second_hand_community_raw_data(self):
        self.crawl_with_thread_pool(THREAD_NUM,
                                    self.crawl_second_community_raw_data_with_rect,
                                    self.rect_list,
                                    self.write_second_community_raw_data_in_rect_to_file)

    def crawl_second_community_raw_data_with_rect(self, rect):
        res = []
        community_list = self.get_lianjia_second_hand_community_list_with_rect(rect)
        for community in community_list:
            res.append(community)
        return res

    def get_lianjia_second_hand_community_list_with_rect(self, rect):
        rect_url = lianjia_second_hand_community_url_pattern.format(rect[0], rect[2], rect[1], rect[3])
        try:
            response_text = self.get_response_text_with_url(rect_url)
            if response_text:
                text_json = json.loads(response_text[43:-1])
                if text_json and 'data' in text_json.keys():
                    return text_json['data']
            return []
        except RequestException as msg:
            self.logger.warning('[city name:{0}][exception:{1}][rect:{2}]'.format(self.city_name, msg, rect))

    def write_second_community_raw_data_in_rect_to_file(self, raw_data_list):
        write_file_path = get_file_path(self.city_name,
                                        CrawlerDataType.RAW_DATA.value,
                                        CrawlerSourceName.LIANJIA.value,
                                        CrawlerDataLabel.SECOND_HAND_COMMUNITY.value)
        self.write_to_file(LIANJIA_SECOND_COMMUNITY_RAW_DATA_HEADER_LIST, write_file_path, raw_data_list)

    def get_lianjia_new_community_data_with_url(self, url):
        try:
            text = self.get_response_text_with_url(url)
            if text:
                data = json.loads(text[20:-1])
                if data and 'data' in data.keys():
                    return data['data']
            return []
        except RequestException as msg:
            self.logger.warning('[city name:{0}][exception:{1}][url:{2}]'.format(self.city_name, msg, url))

    def get_city_url_for_lianjia(self):
        short_city_name = self.get_short_city_name_for_lianjia_new_community()
        city_url = lianjia_new_community_url_pattern.format(short_city_name)
        return city_url

    def get_short_city_name_for_lianjia_new_community(self):
        try:
            text =self.get_response_text_with_url(cq_url_for_lianjia_city_list)
            pattern = re.compile('<li><a href="//(.*?).fang.lianjia.com/ditu/" data-xftrack="10140">(.*?)</a></li>')
            cities = re.findall(pattern, text)
            city_dict = {}
            for city in cities:
                city_dict[city[1]] = (city[0])
            city_dict['重庆'] = 'cq'
            return city_dict[self.city_name]
        except RequestException as msg:
            self.logger.warning('[city name:{0}][exception:{1}]'.format(self.city_name, msg))

# '''
if __name__ == '__main__':
    start = time.clock()
    crawler = LianjiaCrawler('重庆')
    # crawler.crawl_lianjia_second_hand_community_raw_data()
    # crawler.crawl_lianjia_new_community_raw_data()
    crawler.crawl_lianjia_raw_data()
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
    # '''