# headers
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}

# ak for baidu poi
ak = 'GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'

# city center base url for baidu api
city_center_url_pattern = 'https://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'
baidu_poi_url_pattern =  'https://api.map.baidu.com/place/v2/search?query={}&scope=2&coord_type=1&bounds={}&output=json&ak={}'
lianjia_2nd_community_url_pattern = 'https://ajax.lianjia.com/ajax/mapsearch/area/community?' \
                                    'min_longitude={}&max_longitude={}&min_latitude={}&max_latitude={}' \
                                    '&&city_id=500000&callback=jQuery1111026263228440180875_1502180579317&_=1502180579330'
anjuke_2nd_community_url_pattern = 'https://{}.anjuke.com/v3/ajax/map/sale/facet/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p=1&zoom=19&' \
                                   'lat={}_{}&lng={}_{}&kw=&maxp=99'

# baidu poi
baidu_poi_categories = ['美食$餐厅$超市$酒店$公园$酒吧$咖啡厅$小吃$茶座', '购物中心$便利店$园区$厂矿', '商铺$地铁$公交$轻轨$停车场$火车站$机场', '金融$住宅$美容$娱乐$健身',
                        '幼儿园$小学$中学$大学$教育$学校', '医疗$政府机构$公司$文化$数码$银行$写字楼$汽车']

# crawler config
timeout = 5
steps = 100
distance_unit = 0.005
process_num = 4

# source name
source_name_anjuke = '安居客'
source_name_lianjia= '链家'
source_name_baidu= '百度'
source_name_fangtianxia= '房天下'

# data type label
second_hand = '小区_二手'
first_hand = '小区_一手'
baidu_poi = 'poi'
parcel = '地块'
apartment = '单套_二手'

