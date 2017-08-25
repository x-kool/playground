import json
import time
from pypinyin import lazy_pinyin
from retrying import retry

from constant import anjuke_2nd_community_url_pattern, anjuke_new_community_url_pattern
from crawler.base_crawler import BaseCrawler
from crawler.crawler_enum import CrawlerSourceName, CrawlerDataLabel, CrawlerDataType

from util import save_raw_data_in_tsv_file, get_file_path


class AnjukeCrawler(BaseCrawler):
    data_dict_list_for_new_community = []
    data_dict_list_for_second_hand_community = []

    def crawl_anjuke_raw_data(self):
        self.crawl_anjuke_second_hand_community_raw_data()
        self.crawl_anjuke_new_community_raw_data()
        # self.crawl_anjuke_second_hand_single_apt_raw_data()


    def crawl_anjuke_second_hand_community_raw_data(self):
        self.crawl_raw_data_by_thread_with_rect_list_func_and_city_name(self.crawl_second_community_raw_data_with_rect_list,
                                                                        self.city_name)
        file_path = get_file_path(self.city_name,
                                  CrawlerDataType.RAW_DATA.value,
                                  CrawlerSourceName.ANJUKE.value,
                                  CrawlerDataLabel.SECOND_HAND_COMMUNITY.value)
        save_raw_data_in_tsv_file(file_path, self.data_dict_list_for_second_hand_community)


    def crawl_anjuke_new_community_raw_data(self):
        self.crawl_raw_data_by_thread_with_rect_list_func_and_city_name(self.crawl_new_community_raw_data_with_rect_list,
                                                                        self.city_name)
        file_path = get_file_path(self.city_name,
                                  CrawlerDataType.RAW_DATA.value,
                                  CrawlerSourceName.ANJUKE.value,
                                  CrawlerDataLabel.NEW_COMMUNITY.value)
        save_raw_data_in_tsv_file(file_path, self.data_dict_list_for_new_community)


    def crawl_new_community_raw_data_with_rect_list(self, rect_list):
        for idx, rect in enumerate(rect_list):
            community_list = self.get_anjuke_new_community_list_with_rect(rect)
            for community in community_list:
                self.data_dict_list_for_new_community.append(community)
            print(str(idx) + '/' + str(self.step_num ** 2))


    def crawl_second_community_raw_data_with_rect_list(self, rect_list):
        for idx, rect in enumerate(rect_list):
            community_list = self.get_anjuke_second_hand_community_list_with_rect(rect)
            for community in community_list:
                self.data_dict_list_for_second_hand_community.append(community)
            print(str(idx) + '/' + str(self.step_num ** 2))

    @retry(stop_max_attempt_number=10)
    def get_anjuke_second_hand_community_list_with_rect(self, rect):
        rect_url = self.get_anjuke_second_hand_community_list_url(rect)
        response_text = self.get_response_text_with_url(rect_url)
        if response_text:
            content = json.loads(response_text)
            if content and 'val' in content:
                text = content['val']['comms']
                return text
        return []


    def get_anjuke_new_community_list_with_rect(self, rect):
        rect_url = anjuke_new_community_url_pattern.format(*rect)
        response_text = self.get_response_text_with_url(rect_url)
        if response_text:
            content = json.loads(response_text[43:-1])
            if content and 'result' in content:
                text = content['result']['rows']
                return text
        return []


    def get_anjuke_second_hand_community_list_url(self, rect):
        city_name_pinyin = ''.join(lazy_pinyin(self.city_name))
        url = anjuke_2nd_community_url_pattern.format(city_name_pinyin, rect[1], rect[3], rect[0], rect[2])
        return url


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
