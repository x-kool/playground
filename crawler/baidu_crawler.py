import requests
import time

from constant import BAIDU_POI_CATEGORIES, STEP_NUM, TIMEOUT, baidu_poi_url_pattern, BAIDU_API_AK
from crawler.base_crawler import BaseCrawler
from crawler.crawler_enum import CrawlerDataType, CrawlerSourceName, CrawlerDataLabel
from util import get_file_path, save_raw_data_in_tsv_file


class BaiduCrawler(BaseCrawler):
    data_dict_list_for_poi = []
    stored_poi_uid_list = []

    def crawl_baidu_raw_data(self):
        self.crawl_raw_data_by_thread_with_rect_list_func_and_city_name(self.crawl_poi_raw_data_with_rect_list,
                                                                        self.city_name)
        file_path = get_file_path(self.city_name,
                                  CrawlerDataType.RAW_DATA.value,
                                  CrawlerSourceName.BAIDU.value,
                                  CrawlerDataLabel.BAIDU_POI.value)
        save_raw_data_in_tsv_file(file_path, self.data_dict_list_for_poi)

    def crawl_poi_raw_data_with_rect_list(self, rect_list):
        for idx, rect in enumerate(rect_list):
            for category in BAIDU_POI_CATEGORIES:
                poi_list = self.get_baidu_poi_list(category, rect)
                for poi in poi_list:
                    if poi['uid'] not in self.stored_poi_uid_list:
                        self.stored_poi_uid_list.append(poi['uid'])
                        self.data_dict_list_for_poi.append(poi)
            print(str(idx) + '/' + str(STEP_NUM ** 2))

    def get_baidu_poi_list(self, category, rect):
        poi_url = self.get_baidu_poi_url(category, rect)
        try:
            response = requests.get(poi_url, timeout=TIMEOUT)
            response_json = response.json()
            return response_json['results']
        except:
            raise ConnectionError

    def get_baidu_poi_url(self, category, rect):
        formed_rect = self.get_baidu_poi_rect_form(rect)
        poi_url = baidu_poi_url_pattern.format(category, formed_rect, BAIDU_API_AK)
        return poi_url

    def get_baidu_poi_rect_form(self, rect):
        formed_rect = ','.join([rect[1], rect[0], rect[3], rect[2]])
        return formed_rect

#'''
if __name__ == '__main__':
    start = time.clock()
    crawler = BaiduCrawler('重庆')
    # crawler.crawl_anjuke_new_community_raw_data()
    # crawler.crawl_anjuke_second_hand_community_raw_data()
    crawler.crawl_baidu_raw_data()
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
#'''