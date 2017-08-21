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


class AJKXFCrawler(object):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    ak = 'GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'
    city_name = '重庆'
    city_center_url = 'https://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'
    timeout = 5
    steps = 100
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
                self.rect_list.append(['%.6f' % (lng - dist_lng - self.distance_unit),
                                       '%.6f' % (lat - dist_lat - self.distance_unit),
                                       '%.6f' % (lng - dist_lng),
                                       '%.6f' % (lat - dist_lat)])

                self.rect_list.append(['%.6f' % (lng + dist_lng),
                                       '%.6f' % (lat - dist_lat - self.distance_unit),
                                       '%.6f' % (lng + dist_lng + self.distance_unit),
                                       '%.6f' % (lat - dist_lat)])

                self.rect_list.append(['%.6f' % (lng - dist_lng - self.distance_unit),
                                       '%.6f' % (lat + dist_lat),
                                       '%.6f' % (lng - dist_lng),
                                       '%.6f' % (lat + dist_lat + self.distance_unit)])

                self.rect_list.append(['%.6f' % (lng + dist_lng),
                                       '%.6f' % (lat + dist_lat),
                                       '%.6f' % (lng + dist_lng + self.distance_unit),
                                       '%.6f' % (lat + dist_lat + self.distance_unit)])


    def get_url(self, rect):
        base_url = 'https://api.fang.anjuke.com/web/loupan/mapNewlist/?city_id=20&callback=jQuery1113006248457428238563_1502272365154&zoom=16&' \
                   'swlng={}&swlat={}&nelng={}&nelat={}&' \
                   'order=rank&order_type=asc&region_id=0&sub_region_id=0&house_type=0&property_type=0&price_id=0&bunget_id=0&status_sale=3%2C4%2C6%2C7%2C5&price_title=%E5%85%A8%E9%83%A8&keywords=&page=1&page_size=500&timestamp=29&_=1502272365159'
        url = base_url.format(*rect)
        return url

    @retry(stop_max_attempt_number=10)
    def get_html(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException as msg:
            self.logger.warning('in [{0}] city with [{1}]'.format(self.city_name, msg))
            print('链接错误')
            return None


    def get_date(self):
        date = time.strftime("%Y_%m_%d", time.localtime())
        return date


    def save_and_write_community_info(self, community):
        with open('{}_安居客_新房_小区_{}'.format(self.city_name, self.get_date()), 'a', encoding='utf-8') as file:
            # print('正在写入：{}'.format(str(self.info_to_string(community))))
            file.write(self.info_to_string(community))


    def parse_info(self, html):
        if html:
            content = json.loads(html[43:-1])
            if content and 'result' in content:
                text = content['result']['rows']
                return text
        return None


    def info_to_string(self, community):
        residence_info = '\t'.join(['[户型: %-s  面积: %-2.f ]' % (i['alias'], float(i['area'])) for i in community['house_types']])
        line = '\t'.join(
            [community['loupan_name'],
             '%-s' % community['loupan_id'],
             '%-s' % community['build_type'],
             '%-f' % (float(community['baidu_lat'])),
             '%-f' % (float(community['baidu_lng'])),
             '%-s' % community['address'],
             '%-s' % community['fitment_type'],
             '%-s' % community['new_price'],
             '%-s' % community['is_sales_promotion'],
             '%-s' % residence_info]
        )
        print('正在写入：{}'.format(str(community['loupan_name'])))
        return line + '\n'


    def data_form(self):
        with open('{}_安居客_新房_小区_{}'.format(self.city_name, self.get_date()), 'r+', encoding='utf-8') as file:
            file.readlines()
# =============================================================
    def get_all_community_price_info(self):
        self.get_rects_by_center()
        for rect in self.rect_list:
            rect_url = self.get_url(rect)
            html = self.get_html(rect_url)
            data = self.parse_info(html)
            if data:
                for community in data:
                    self.save_and_write_community_info(community)
# ============================================================
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
        for idx,rect in enumerate(rect_list):
            self.get_info_in_rect(rect)
            print (str(idx) + '/' + str(l))


    def get_all_community_price_info_with_Thread(self):
        self.get_rects_by_center()
        len_rects = int(len(self.rect_list) / self.process_num)
        process_list = []
        for i in range(self.process_num):
            process = threading.Thread(target=self.get_info_in_rect_list,
                                       args=(self.rect_list[i * len_rects : (i+1) * len_rects ], ))
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
        print ('运行时间：%-.2f s' % (end-start))


if __name__ == '__main__':
    crawler = AJKXFCrawler('重庆')
    crawler.main(1)
