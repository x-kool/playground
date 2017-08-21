"""
作为安居客二手房信息的有效补充，可以提供 [户型-面积-楼层总数] 等信息
通过楼盘id可以和二手房信息一一对应，有待整合
"""
import json
import threading

import requests
import time
from requests import RequestException
import logging.handlers

from retrying import retry


class FinalLogger:
    logger = None
    levels = {"n": logging.NOTSET,
              "d": logging.DEBUG,
              "i": logging.INFO,
              "w": logging.WARN,
              "e": logging.ERROR,
              "c": logging.CRITICAL}

    log_level = "w"
    log_file = "LJ_2nd_Com.log"
    log_max_byte = 10 * 1024 * 1024
    log_backup_count = 5

    @staticmethod
    def getLogger():
        if FinalLogger.logger is not None:
            return FinalLogger.logger
        # log conf
        FinalLogger.logger = logging.Logger("poi_log")
        # backup nothing mush
        log_handler = logging.handlers.RotatingFileHandler(filename=FinalLogger.log_file,
                                                           maxBytes=FinalLogger.log_max_byte,
                                                           backupCount=FinalLogger.log_backup_count)
        # format
        log_fmt = logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s][%(funcName)s][%(message)s]")
        log_handler.setFormatter(log_fmt)
        FinalLogger.logger.addHandler(log_handler)
        FinalLogger.logger.setLevel(FinalLogger.levels.get(FinalLogger.log_level))
        return FinalLogger.logger


class AJKSinglePropCrawler(object):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}

    ak = 'GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'
    city_center_url = 'https://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'
    timeout = 5

    steps = 5
    distance_unit = 0.005
    rect_list = []
    process_num = 4

    logger = FinalLogger.getLogger()


    def __init__(self, city_name='重庆',process_num=4):
        self.city_name = city_name
        self.process_num = process_num


    def get_city_center(self):
        city_url = self.city_center_url.format(self.city_name, self.ak)
        try:
            r = requests.get(city_url, timeout=self.timeout).json()
            return r['result']['location']
        except:
            raise ConnectionError


    def get_rects_by_center(self):
        location = self.get_city_center()
        lng = location['lng']  # city center [lat, lng]
        lat = location['lat']
        # 经纬度+-1.2度范围
        for units_lng in range(self.steps):
            dist_lng = units_lng * self.distance_unit
            for units_lat in range(self.steps):
                dist_lat = units_lat * self.distance_unit
                self.rect_list.append(['%.6f' % (lat - dist_lat - self.distance_unit),
                                        '%.6f' % (lat - dist_lat),
                                        '%.6f' % (lng - dist_lng - self.distance_unit),
                                        '%.6f' % (lng - dist_lng)])

                self.rect_list.append(['%.6f' % (lat - dist_lat - self.distance_unit),
                                       '%.6f' % (lat - dist_lat),
                                       '%.6f' % (lng + dist_lng),
                                       '%.6f' % (lng + dist_lng + self.distance_unit)])

                self.rect_list.append(['%.6f' % (lat + dist_lat),
                                       '%.6f' % (lat + dist_lat + self.distance_unit),
                                       '%.6f' % (lng - dist_lng - self.distance_unit),
                                       '%.6f' % (lng - dist_lng)])

                self.rect_list.append(['%.6f' % (lat + dist_lat),
                                       '%.6f' % (lat + dist_lat + self.distance_unit),
                                       '%.6f' % (lng + dist_lng),
                                       '%.6f' % (lng + dist_lng + self.distance_unit)])


    def get_url(self, rect):  # 这个base_url 区别于 facet 的小区信息，这个是该区域内在售的单套信息
        base_url = 'https://chongqing.anjuke.com/v3/ajax/map/sale/prop_list/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p=1&zoom=16&' \
                   'lat={}_{}&lng={}_{}&kw=&maxp=99'
        url = base_url.format(*rect)
        return url


    def get_html(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException:
            print('链接错误')
            return None


    def get_date(self):
        date = time.strftime("%Y_%m_%d", time.localtime())
        return date


    def save_and_write_community_info(self, community):
        with open('{}_安居客_二手_单套_{}'.format(self.city_name, self.get_date()), 'a', encoding='utf-8') as file:
            print('正在写入：{}'.format(str(self.info_to_string(community))))
            file.write(self.info_to_string(community))


    def parse_info(self, html):
        if html:
            content = json.loads(html)
            if content and 'val' in content:
                text = content['val']['props']
                return text
        return None


    def info_to_string(self, community):
        line = '\t'.join(
            [community['comm_name'],
             '%-s' % community['comm_id'],
             '%-s' % community['area'],
             '%-s' % community['rhval'],
             '%-s' % community['floor_tag']]
        )
        return line + '\n'


    def get_all_community_price_info(self):
        self.get_rects_by_center()
        for rect in self.rect_list:
            rect_url = self.get_url(rect)
            html = self.get_html(rect_url)
            data = self.parse_info(html)
            if data:
                for single_prop in data:
                    self.save_and_write_community_info(single_prop)

 # == == == == == == == == == == == == == == == == == == == == == == == == == =

    @retry(stop_max_attempt_number=10)
    def get_info_in_rect(self, rect):
        rect_url = self.get_url(rect)
        html = self.get_html(rect_url)
        data = self.parse_info(html)
        if data:
            for community in data:
                self.save_and_write_community_info(community)

    def get_info_in_rect_list(self, rect_list):
        l = len(rect_list)
        for idx, rect in enumerate(rect_list):
            self.get_info_in_rect(rect)
            print(str(idx) + '/' + str(l))

    def get_all_community_price_info_with_Thread(self):
        self.get_rects_by_center()
        len_rects = int(len(self.rect_list) / self.process_num)
        process_list = []
        for i in range(self.process_num):
            process = threading.Thread(target=self.get_info_in_rect_list,
                                       args=(self.rect_list[i * len_rects: (i + 1) * len_rects],))
            process.start()
            process_list.append(process)
        for process in process_list:
            process.join()

    # 如果面积较小，可以选择不启动多线程
    def main(self, Thread):
        start = time.clock()

        if Thread == 0:
            self.get_all_community_price_info()
        elif Thread == 1:
            self.get_all_community_price_info_with_Thread()

        end = time.clock()
        print('运行时间：%-.2f s' % (end - start))


if __name__ == '__main__':
    crawler = AJKSinglePropCrawler('重庆',4)
    crawler.main(1)
