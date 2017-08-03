# coding=utf-8
import requests
import json
import threading
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
    categories = ['中餐厅$外国餐厅$小吃快餐店$蛋糕甜品店$咖啡厅$茶座$酒吧$酒店$超市','购物中心$便利店$家居建材$家电数码$集市$宿舍$园区$农林园艺$厂矿','商铺$生活服务$交通设施$金融$住宅区','丽人$休闲娱乐$旅游景点$运动健身$教育培训$文化传媒$医疗$政府机构$汽车服务$写字楼','公司']
    distance_unit = 0.005
    steps = 40
    rects = []
    poi_ids=[]
    location = {}
    city_name = ''
    timeout = 5
    process_number = 4
    total_num = 0    
    # logger obj
    logger = FinalLogger.getLogger()


    def __init__(self,
                 city_name,
                 process_number,
                 ):

        self.city_name = city_name
        self.process_number = process_number
        self.stop_unit_num = 0

    def get_city_center(self):
        city_url = self.city_center_url.format(self.city_name, self.ak)
        try:
            r = requests.get(city_url, timeout=self.timeout).json()
            if r['status'] != 0:
                msg = r['message'] if 'message' in r.keys() else r['msg'] 
                # self.logger.warning(self.city_name+':'+str(self.stop_unit_num)+':'+msg)
                self.logger.warning('can not get  [{}] city center with {}'.format(self.city_name, msg))
                print (msg)
                raise ValueError
            else:
                self.location = r['result']['location']
        except requests.exceptions.RequestException:
            self.logger.warning('can not get  [{}] city center with Response Error'.format(self.city_name))
            print ('Response Error')            
            raise ConnectionError

    def get_rects_by_center(self):
        lng = self.location['lng']  # city center [lat, lng]
        lat = self.location['lat'] 
        # 经纬度+-1.2度范围
        for units_lng in range(self.steps):
            dist_lng = units_lng * self.distance_unit
            for units_lat in range(self.steps):
                dist_lat = units_lat * self.distance_unit
                self.rects.append('{:.3f},{:.3f},{:.3f},{:.3f}'.format(lat - dist_lat - self.distance_unit,   # rect 左下，右上 2个点坐标
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
            print(category,rect)
            # TODO(Ke) page 这部分有问题，需要修改 [total] 参数是有问题的，并不准确
            try:
                r = requests.get(poi_url, timeout=self.timeout).json()
                if r['results'] and r['total']:
                    self.save_and_write_pois(r['results'])
                    pages = round(r['total'] / 20) + 1
                    if pages > 1:
                        #for page_num in range(1, pages):
                        total = 1
                        page_num = 1
                        while total != 0:
                            other = requests.get(self.poi_base_url.format(category, page_num, rect, self.ak), timeout=self.timeout).json()
                            self.save_and_write_pois(other['results'])
                            page_num += 1
                            total = other['total']
            except requests.exceptions.RequestException:
                # self.logger.warning(self.city_name+':'+str(self.stop_unit_num)+':Response Error')
                self.logger.warning('stop at [{}] rect unit in [{}] city with Response Error'.format(self.stop_unit_num, self.city_name))
                print ('Response Error')    
                raise ConnectionError

    def save_and_write_pois(self, new_pois):
        with open(self.city_name, 'a') as file:
            for poi in new_pois:
                if poi['uid'] not in self.poi_ids:
                    self.poi_ids.append(poi['uid'])
                    file.write(self.poi_to_string(poi))
        self.total_num += len(new_pois)     

    def poi_to_string(self, poi):
        line = '\t'.join([poi['name'],
                          str(poi['location']['lat']),
                          str(poi['location']['lng']),
                          poi.get('address', ' '),
                          poi.get('telephone', ' '),
                          poi['uid']])
        if poi.get('detail_info'):
            tags = poi['detail_info'].get('tag', '其他;其他').split(';')
            line += '\t' + '\t'.join([tags[0],
                                      tags[1] if len(tags) > 1 else '其他',
                                      poi['detail_info'].get('price', ' '),
                                      poi['detail_info'].get('overall_rating', ' '),
                                      poi['detail_info'].get('service_rating', ' '),
                                      poi['detail_info'].get('environment_rating', ' ')])
        return line + '\n'

    def get_poi_in_rect_list(self,rect_list):
        for rect in rect_list:
            self.get_poi_in_rect(rect)
        
    # TODO   全部获取以后才同一写到文件里面，不够安全，需要断点保护
    # 流程： 获取城市中心点=》中心点开始划分小方块=》对每个方块的poi循环一次category=》保存所有poi
    def get_all_pois(self, start_unit_num):
        if start_unit_num == 0:
            self.get_city_center()
            self.get_rects_by_center()
        len_rects = int(len(self.rects)/self.process_number)
        print('len',len_rects)
        process_list = []
        for i in range(start_unit_num, self.process_number):
            self.stop_unit_num = i
            process = threading.Thread(target=self.get_poi_in_rect_list, args=(self.rects[i*len_rects:(i+1)*len_rects],))
            process.start()
            process_list.append(process)
        for process in process_list:
            process.join()
        print('total',self.total_num)




'''
cities = ['深圳市','重庆市','广州市','北京市','上海市']
crawler = PoiCrawler(cities[0],4)

for idx, city in enumerate(cities[0:]):
    crawler.city_name = city
    crawler.get_all_pois(0)

'''



if __name__ == '__main__':
    crawler = PoiCrawler('重庆市',4)
    crawler.get_all_pois(0)





