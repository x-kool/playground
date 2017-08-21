# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 14:03:06 2017

@author: xcsliu
"""

import re
import threading

import requests
import time
from bs4 import BeautifulSoup
from requests import RequestException
from retrying import retry
import logging.handlers


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


class FtxParcelCrawler(object):
    city_name = '重庆'
    page_base_url = 'http://land.fang.com/market/500100________1_0_{}.html'
    parcel_base_url = 'http://land.fang.com'
    parcel_url_list = []
    process_num = 4

    logger = FinalLogger.getLogger()


    def __init__(self, city_name='重庆',process_num=4):
        self.city_name = city_name
        self.process_num = process_num


    def get_page_size(self):
        url = self.page_base_url.format('1')
        text = self.get_html(url)
        pattern = re.compile('</a><span>1/(.*?)</span><a class="paga28')
        page_size = re.findall(pattern, text)[0]
        return int(page_size)



    @retry(stop_max_attempt_number=10)
    def get_html(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException as msg:
            self.logger.warning('in [{0}] city with [{1}]'.format(self.city_name, msg))
            print('链接错误')
            return None


    def get_parcel_url_list(self):
        page_size = self.get_page_size()
        for page_num in range(1, page_size+1):
            url = self.page_base_url.format(page_num)
            text = self.get_html(url)
            soup = BeautifulSoup(text)
            # 得到该页面内的 parcel 的 url
            for i in soup.select('h3'):
                parcel_url = self.parcel_base_url + i.contents[1]['href']
                self.parcel_url_list.append(parcel_url)


    def get_parcel_data(self, parcel_url):
        text = self.get_html(parcel_url)
        soup = BeautifulSoup(text)
        parcel_data = {}
        # parcel 基础信息
        for i in soup.select('table[class="tablebox02 mt10"]')[0].select('td'):
            key = i.contents[0].string[:-1]
            value = i.contents[1].string
            parcel_data[key] = value
        # parcel 交易信息
        for i in soup.select('table[class="tablebox02 mt10"]')[1].select('td'):
            key = i.contents[0].string[:-1]
            value = i.contents[1].string
            parcel_data[key] = value
        # 经纬度信息 + 地块编号信息
        pattern = re.compile('pointX = "(.*?)";')
        lng = re.findall(pattern, text)[0]
        pattern = re.compile('pointY = "(.*?)";')
        lat = re.findall(pattern, text)[0]
        pattern = re.compile('地块编号：(.*?)</span>')
        num_of_parcel = re.findall(pattern, text)[0]
        parcel_data['lat'] = lat
        parcel_data['lng'] = lng
        parcel_data['地块编号'] = num_of_parcel
        return parcel_data


    def get_date(self):
        date = time.strftime("%Y_%m_%d", time.localtime())
        return date


    def save_and_write_parcel_data(self, parcel_data):
        with open('{}_房天下_地块_{}'.format(self.city_name, self.get_date()), 'a', encoding='utf-8') as file:
            # print('正在写入：{}'.format(str(info_to_string(parcel_data))))
            file.write(self.info_to_string(parcel_data))


    def info_to_string(self, parcel_data):
        line = '\t'.join(
            ['%-s' % (parcel_data['位置']),
             '%-s' % (parcel_data['地区']),
             '%-s' % (parcel_data['所在地']),
             '%-s' % (parcel_data['lat']),
             '%-s' % (parcel_data['lng']),
             '%-s' % (parcel_data['地块编号']),
             '%-s' % (parcel_data['总面积']),
             '%-s' % (parcel_data['建设用地面积']),
             '%-s' % (parcel_data['规划建筑面积']),
             '%-s' % (parcel_data['代征面积']),
             '%-s' % (parcel_data['容积率']),
             '%-s' % (parcel_data['绿化率']),
             '%-s' % (parcel_data['商业比例']),
             '%-s' % (parcel_data['建筑密度']),
             '%-s' % (parcel_data['限制高度']),
             '%-s' % (parcel_data['出让形式']),
             '%-s' % (parcel_data['出让年限']),
             '%-s' % (parcel_data['四至']),
             '%-s' % (parcel_data['规划用途']),
             '%-s' % (parcel_data['交易状况']),
             '%-s' % (parcel_data['竞得方']),
             '%-s' % (parcel_data['起始日期']),
             '%-s' % (parcel_data['截止日期']),
             '%-s' % (parcel_data['成交日期']),
             '%-s' % (parcel_data['起始价']),
             '%-s' % (parcel_data['成交价']),
             '%-s' % (parcel_data['楼面地价']),
             '%-s' % (parcel_data['溢价率']),
             '%-s' % (parcel_data['咨询电话']),
             '%-s' % (parcel_data['保证金']),
             '%-s' % (parcel_data['最小加价幅度'])]
        )
        print ('%-s' % (parcel_data['位置']))
        return line + '\n'

# ====================================================
    def get_all_parcel_info(self):
        self.get_parcel_url_list()
        parcel_num = len(self.parcel_url_list)
        for parcel_url_num in range(parcel_num):
            parcel_data = self.get_parcel_data(self.parcel_url_list[parcel_url_num])
            self.save_and_write_parcel_data(parcel_data)
            print (str(parcel_url_num+1) + '/' + str(parcel_num))

# ====================================================

    def get_parcel_info_in_url_list(self, parcel_url_sub_list):
        l = len(parcel_url_sub_list)
        for idx,url in enumerate(parcel_url_sub_list):
            parcel_data = self.get_parcel_data(url)
            self.save_and_write_parcel_data(parcel_data)
            print (str(idx) + '/' + str(l))


    def get_all_parcel_info_with_Thread(self):
        self.get_parcel_url_list()
        len_url_list = int( len(self.parcel_url_list) / self.process_num )
        process_list = []
        for i in range(self.process_num):
            process = threading.Thread(target=self.get_parcel_info_in_url_list,
                                       args=(self.parcel_url_list[i * len_url_list : (i+1) * len_url_list], ))
            process.start()
            process_list.append(process)

        for process in process_list:
            process.join()


    def main(self, Thread):
        start = time.clock()

        if Thread == 0:
            self.get_all_parcel_info()
        elif Thread == 1:
            self.get_all_parcel_info_with_Thread()

        end = time.clock()
        print ('运行时间：%-.2f s' % (end-start))


if __name__ == '__main__':
    crawler = FtxParcelCrawler('重庆',4)
    crawler.main(1)
