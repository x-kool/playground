import requests
import json
import threading
import logging.handlers
from retrying import retry

def myAlign(string, length=0):
    if length == 0:
        return string
    slen = len(string)
    re = string
    if isinstance(string, str):
        placeholder = ' '
    else:
        placeholder = u'　'
    while slen < length:
        re += placeholder
        slen += 1
    return re

class FinalLogger:
    logger = None
    levels = {"n": logging.NOTSET,
              "d": logging.DEBUG,
              "i": logging.INFO,
              "w": logging.WARN,
              "e": logging.ERROR,
              "c": logging.CRITICAL}

    log_level = "w"
    log_file = "poi_log.log"
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


class PoiCrawler(object):
    ak = 'GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'
    poi_base_url = 'https://api.map.baidu.com/place/v2/search?query={}&page_size=20&page_num={}&scope=2&coord_type=1&bounds={}&output=json&ak={}'
    city_center_url = 'https://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'
    # categories 这样设置主要是为了在每次请求返回的poi total都尽量小于但接近400
    #categories = ['中餐厅$外国餐厅$小吃快餐店$蛋糕甜品店$咖啡厅$茶座$酒吧$酒店$超市', '购物中心$便利店$家居建材$家电数码$集市$宿舍$园区$农林园艺$厂矿', '商铺$生活服务$交通设施$金融$住宅区',
    #              '丽人$休闲娱乐$旅游景点$运动健身$教育培训$文化传媒$医疗$政府机构$汽车服务$写字楼', '公司$学校']
    categories = ['美食$餐厅$超市$酒店$公园$酒吧$咖啡厅$小吃$茶座', '购物中心$便利店$园区$厂矿', '商铺$地铁$公交$轻轨$停车场$火车站$机场', '金融$住宅$美容$娱乐$健身',
                  '幼儿园$小学$中学$大学$教育$学校', '医疗$政府机构$公司$文化$数码$银行$写字楼$汽车']
    distance_unit = 0.005
    steps = 100
    rects = []
    poi_ids = []
    location = {}
    city_name = ''
    timeout = 5
    process_number = 4
    total_num = 0

    rect_candidate = []
    rect_error_candidate = []
    initial = 1
    # logger obj
    logger = FinalLogger.getLogger()


    def __init__(self,
                 city_name,
                 process_number):

        self.city_name = city_name
        self.process_number = process_number

    def get_city_center(self):
        city_url = self.city_center_url.format(self.city_name, self.ak)
        try:
            r = requests.get(city_url, timeout=self.timeout).json()
            if r['status'] != 0:
                msg = r['message'] if 'message' in r.keys() else r['msg']
                self.logger.warning('can not get  [{}] city center with [{}]'.format(self.city_name, msg))
                print(msg)
                raise ConnectionError
            else:
                self.location = r['result']['location']
        except requests.exceptions.RequestException as msg:
            self.logger.warning('can not get  [{}] city center with [{}]'.format(self.city_name, msg))
            print(msg)
            raise ConnectionError

    def get_rects_by_center(self):
        lng = self.location['lng']  # city center [lat, lng]
        lat = self.location['lat']
        # 经纬度+-1.2度范围
        for units_lng in range(self.steps):
            dist_lng = units_lng * self.distance_unit
            for units_lat in range(self.steps):
                dist_lat = units_lat * self.distance_unit
                self.rects.append('{:.3f},{:.3f},{:.3f},{:.3f}'.format(lat - dist_lat - self.distance_unit,  # rect 左下，右上 2个点坐标
                                                                       lng - dist_lng - self.distance_unit,
                                                                       lat - dist_lat,
                                                                       lng - dist_lng))
                self.rects.append('{:.3f},{:.3f},{:.3f},{:.3f}'.format(lat - dist_lat - self.distance_unit,
                                                                       lng + dist_lng,
                                                                       lat - dist_lat,
                                                                       lng + dist_lng + self.distance_unit))
                self.rects.append('{:.3f},{:.3f},{:.3f},{:.3f}'.format(lat + dist_lat,
                                                                       lng - dist_lng - self.distance_unit,
                                                                       lat + dist_lat + self.distance_unit,
                                                                       lng - dist_lng))
                self.rects.append('{:.3f},{:.3f},{:.3f},{:.3f}'.format(lat + dist_lat,
                                                                       lng + dist_lng,
                                                                       lat + dist_lat + self.distance_unit,
                                                                       lng + dist_lng + self.distance_unit))

    @retry(stop_max_attempt_number=10)
    def get_poi_in_rect(self, rect):
        for category in self.categories:
            poi_url = self.poi_base_url.format(category, 0, rect, self.ak)
            print(category, rect)
            try:
                r = requests.get(poi_url, timeout=self.timeout).json()
                if r['results'] and r['total']:
                    self.save_and_write_pois(r['results'])
                    pages = round(r['total'] / 20) + 1
                    if pages > 1:
                        # for page_num in range(1, pages):
                        total = 1
                        page_num = 1
                        while total != 0:
                            other = requests.get(self.poi_base_url.format(category, page_num, rect, self.ak),
                                                 timeout=self.timeout).json()
                            self.save_and_write_pois(other['results'])
                            page_num += 1
                            total = other['total']
            except requests.exceptions.RequestException as msg:
                stop_rect_num = self.rects.index(rect)
                self.rect_error_candidate.append(rect)
                self.logger.warning(
                    'stop at [{0:5}] rect num in [{1}] city with [{2}]'.format(stop_rect_num, self.city_name, msg))
                print(msg)
                raise ConnectionError

    def save_and_write_pois(self, new_pois):
        with open('{}poi信息'.format(self.city_name), 'a') as file:
            for poi in new_pois:
                if poi['uid'] not in self.poi_ids:
                    self.poi_ids.append(poi['uid'])
                    file.write(self.poi_to_string(poi))
        self.total_num += len(new_pois)

    def poi_to_string(self, poi):
        line = '\t'.join([myAlign(poi['name'], 30),
                          myAlign('%-.6f' % (poi['location']['lat']), 20),
                          myAlign('%-.6f' % (poi['location']['lng']), 20),
                          myAlign('%-30s' % (poi.get('address', ' ')), 20),
                          myAlign('%-15s' % (poi.get('telephone', ' ')), 20),
                          myAlign('%-20s' % (poi['uid']), 20)])
        # [[name][location][address][telephone][uid][category][detail_info][price][overall_rating][service_rating][environment_rating]]
        if poi.get('detail_info'):
            tags = poi['detail_info'].get('tag', '其他;其他').split(';')
            line += '\t' + '\t'.join([tags[0],
                                      tags[1] if len(tags) > 1 else '其他',
                                      poi['detail_info'].get('price', ' '),
                                      poi['detail_info'].get('overall_rating', ' '),
                                      poi['detail_info'].get('service_rating', ' '),
                                      poi['detail_info'].get('environment_rating', ' ')])
        return line + '\n'

    def get_poi_in_rect_list(self, rect_list):
        for rect in rect_list:
            self.get_poi_in_rect(rect)

    # TODO   全部获取以后才同一写到文件里面，不够安全，需要断点保护
    # 流程： 获取城市中心点=》中心点开始划分小方块=》对每个方块的poi循环一次category=》保存所有poi
    def get_all_pois(self, mini_num_rect_left):
        if len(self.rect_candidate) == 0:
            self.get_city_center()
            self.get_rects_by_center()
            self.rect_candidate = [k for k in self.rects]

        while len(self.rect_candidate) > mini_num_rect_left:
            process_num = self.process_number if len(self.rect_candidate) > 20 else 1
            len_rects = int((len(self.rect_candidate) / process_num))
            print('len', len_rects)
            process_list = []
            for i in range(process_num):
                process = threading.Thread(target=self.get_poi_in_rect_list,
                                           args=(self.rect_candidate[i * len_rects:(i + 1) * len_rects],))
                process.start()
                process_list.append(process)
            for process in process_list:
                process.join()
            self.rect_candidate = [k for k in self.rect_error_candidate]
            self.rect_error_candidate = []
        print('total', self.total_num)
        print('{} rects left to search in all {} rects'.format(len(self.rect_candidate), len(self.rects)))


'''
cities = ['深圳市','重庆市','广州市','北京市','上海市']
crawler = PoiCrawler(cities[0],4)

for idx, city in enumerate(cities[0:]):
    crawler.city_name = city
    crawler.get_all_pois(0)

'''
if __name__ == '__main__':
    crawler = PoiCrawler('重庆市', 4)
    crawler.get_all_pois(10)
