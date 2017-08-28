import requests
import time

from constant import BAIDU_POI_CATEGORIES, TIMEOUT, baidu_poi_url_pattern, BAIDU_API_AK, THREAD_NUM, \
    BAIDU_POI_RAW_DATA_HEADER_LIST
from crawler.base_crawler import BaseCrawler
from crawler.crawler_enum import CrawlerDataType, CrawlerSourceName, CrawlerDataLabel
from util import get_file_path

class BaiduCrawler(BaseCrawler):
    def __init__(self, city_name):
        super(BaiduCrawler, self).__init__(city_name)
        self.stored_poi_uid_list = []
        self.lng, self.lat = self.get_city_center_lng_lat_by_city_name(self.city_name)
        self.rect_list = self.new_get_rect_list_by_lng_lat(self.lng, self.lat)

    def crawl_baidu_raw_data(self):
        self.crawl_with_thread_pool(THREAD_NUM,
                                    self.crawl_poi_raw_data_with_rect,
                                    self.rect_list,
                                    self.write_poi_raw_data_in_rect_to_file)

    def crawl_poi_raw_data_with_rect(self, rect):
        data_dict_list_for_poi = []
        for category in BAIDU_POI_CATEGORIES:
            poi_list = self.get_baidu_poi_list(category, rect)
            for poi in poi_list:
                if poi['uid'] not in self.stored_poi_uid_list:
                    self.stored_poi_uid_list.append(poi['uid'])
                    data_dict_list_for_poi.append(poi)
        return data_dict_list_for_poi

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

    def write_poi_raw_data_in_rect_to_file(self, raw_data_list):
        write_file_path = get_file_path(self.city_name,
                                        CrawlerDataType.RAW_DATA.value,
                                        CrawlerSourceName.BAIDU.value,
                                        CrawlerDataLabel.BAIDU_POI.value)
        self.write_to_file(BAIDU_POI_RAW_DATA_HEADER_LIST, write_file_path, raw_data_list)

#'''
if __name__ == '__main__':
    start = time.clock()
    crawler = BaiduCrawler('重庆')
    crawler.crawl_baidu_raw_data()
    end = time.clock()
    print('运行时间：%-.2f s' % (end - start))
    print('poi信息数量：%s' % (len(crawler.stored_poi_uid_list)))
#'''