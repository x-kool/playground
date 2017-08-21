import json
import re

import requests
import time
from requests import RequestException

class Crawler(object):
    base_url = 'http://{}.fang.lianjia.com/xinfang/mapsearchloupan?&&callback=speedupjsonpapi&_=1502246125390'


    def __init__(self, city_name):
        self.city_name = city_name


    def get_url(self):
        short_city_name = self.get_city_list()[self.city_name]
        url = self.base_url.format(short_city_name)
        return  url


    def get_city_list(self):
        url = 'http://cq.fang.lianjia.com/ditu/'
        response = requests.get(url)
        text = response.text
        pattern = re.compile('<li><a href="//(.*?).fang.lianjia.com/ditu/" data-xftrack="10140">(.*?)</a></li>')
        cities = re.findall(pattern, text)
        city_dict = {}
        for city in cities:
            city_dict[city[1]] = (city[0])
        city_dict['重庆'] = 'cq'
        return city_dict


    def get_html(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                html = response.text
                return html
            return None
        except RequestException:
            print('链接错误')
            return None


    def get_date(self):
        date = time.strftime("%Y_%m_%d", time.localtime())
        return date


    def save_and_write_resblock_info(self, resblock):
        with open('{}_链家_新房_小区_{}'.format(self.city_name, self.get_date()), 'a', encoding='utf-8') as file:
            print(u'正在写入：{}'.format(str(self.info_to_string(resblock))))
            file.write(self.info_to_string(resblock))


    def parse_info(self, html):
        if html:
            data = json.loads(html[20:-1])
            if data and 'data' in data.keys():
                return data['data']
        return None


    def info_to_string(self, resblock):
        line = '\t'.join(
                         [resblock['resblock_name'],
                          '%-s' % (resblock['district_id']),
                          '%-s' % (resblock['house_type']),
                          '%-.6f' % (resblock['latitude']),
                          '%-.6f' % (resblock['longitude']),
                          '%-s'  % (resblock['average_price']),
                          '%-s'  % (resblock['show_price']),
                          '%-s' % (resblock['rooms']),
                          '%-s' % (resblock['resblock_frame_area']),
                          '%-s'  % (resblock['min_frame_area']),
                          '%-s'  % (resblock['max_frame_area'])]
                         )
        return line + '\n'


    def get_all_resblock_info(self):
        url = self.get_url()
        html = self.get_html(url)
        text = self.parse_info(html)
        for resblock_list in text.values():
            for res in resblock_list:
                self.save_and_write_resblock_info(res)


    def main(self):
        self.get_all_resblock_info()


city_list = ['中山', '佛山', '北京', '南京', '厦门',
             '合肥', '大连', '天津', '太原', '广州',
             '廊坊', '惠州', '成都', '无锡', '杭州',
             '武汉', '沈阳', '济南', '深圳', '烟台',
             '石家庄','西安','重庆', '长沙', '青岛']

'''
if __name__ == '__main__':
    for city in city_list:
        crawler = Crawler(city)
        crawler.main()
'''
if __name__ == '__main__':
    crawler = Crawler('重庆')
    crawler.main()