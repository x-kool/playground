import re
import pypinyin
from pypinyin import pinyin
import requests


from Logger import FinalLogger


class CommunityCrawler():
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    ak = 'GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'

    city_name = '重庆'
    city_center_base_url = 'https://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'

    timeout = 5
    steps = 100
    distance_unit = 0.005
    rect_list = []
    source = '安居客' # 链家
    source_type = 'prop_list'  # ershoufang / loupan

    logger = FinalLogger.getLogger()


    def get_city_center(self, city_name):
        city_url = self.city_center_base_url.format(city_name, self.ak)
        try:
            r = requests.get(city_url, timeout=self.timeout).json()
            return r['result']['location']
        except:
            raise ConnectionError

    def get_rects_by_center(self):
        location = self.get_city_center(self.city_name)
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


    def get_url(self, source, source_type, city_name, rect):
        if self.validate_city(source, city_name):
            if source == '链家' and source_type == 'xinfang':
                base_url = 'http://{}.fang.lianjia.com/xinfang/mapsearchloupan?&&callback=speedupjsonpapi&_=1502246125390'
                # short_city_name = ''.join([i[0] for i in pinyin('{}'.format(city_name), style=pypinyin.INITIALS)])
                short_city_name = self.get_city_list(source)[city_name][0]
                url = base_url.format(short_city_name)
                return url


            elif source == '链家' and source_type == 'ershoufang':
                base_url = 'https://ajax.lianjia.com/ajax/mapsearch/area/community?' \
                       'min_longitude={}&max_longitude={}&min_latitude={}&max_latitude={}' \
                       '&&city_id={}&callback=jQuery1111026263228440180875_1502180579317&_=1502180579330'
                city_id = ''


            elif source == '' and source_type == 'xinfang':
                pass

            elif source == '' and source_type == 'ershoufang':
                pass

            elif source == '' and  source_type == 'prop_list':
                pass

        else:
            msg = '该网站该类型信息目前不支持{}市'.format(city_name)
            self.logger.warning(msg)
            print (msg)
            raise ValueError


    def get_city_list(self, source):
        if source == '链家':
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



    def validate_city(self, source, city_name):
        if source == '链家':
            # 通过链家新房地图找房城市目录验证当前城市是否可用
            city_list = self.get_city_list(source)
            return True if city_name in city_list.keys() else False
        pass
    pass