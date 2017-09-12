
import time
import pandas as pd
import requests
import json
import re


city_name = 'guangzhou'
read_file_path = 'E:\\PycharmPrjects\\playground\\poi_data\\2017_09_01\\{}\\ready_data\\{}_baidu_poi_2017_09_01.tsv'.format(city_name, city_name )
raw_data = pd.read_table(read_file_path, error_bad_lines=False)



def get_ready(strs):
    num = 0
    new_strs = []
    for i in strs:
        if i == ',' and num & 1 == 1:
            new_strs.append(';')
            num += 1
        elif i == ',':
            new_strs.append(',')
            num += 1
        else:
            new_strs.append(i)
    return ''.join(new_strs)
'''
geo_list = []
raw_data = raw_data[:100]

def get_geo_list():
    try:
        for idx,uid in enumerate(raw_data['uid'][len(geo_list):]):
            url_lunkuo_pattern = 'http://map.baidu.com/?pcevaname=pc4.1&qt=ext&uid={}&ext_ver=new&l=12'
            url = url_lunkuo_pattern.format(uid)
            res = requests.get(url,timeout=5)
            text = res.text
            res= json.loads(text)
            geo = res['content']['geo']
            geo_list.append(geo)
            print (idx)
    except:
        if len(geo_list) == len(raw_data['uid']):
            return
        else:
            get_geo_list()

get_geo_list()
#print (geo_list)

'''
geo = '12560234.3076,2626632.86557,12560258.4116,2626687.92069,12560290.1798,2626740.67123,12560325.0037,2626772.38272,12560396.2821,2626811.31984,12560437.9104,2626829.80731,12560470.4169,2626856.73542,12560467.7473,2626843.31059,12560452.7711,2626798.92938,12560438.6876,2626755.30124,12560418.01,2626688.11758,12560393.0563,2626603.30219,12560397.3664,2626577.23818,12560416.5505,2626500.08651,12560427.4906,2626450.99524,12560425.5387,2626432.35995,12560399.0873,2626431.68829,12560360.8246,2626452.01748,12560293.1617,2626532.27676,12560234.8195,2626579.03285,12560255.8955,2626622.32811,12560234.3076,2626632.86557'
transfer_url_pattern = 'http://api.map.baidu.com/geoconv/v1/?coords={}&from=6&to=5&ak=GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'
ready_geo = get_ready(geo)
transfer_url = transfer_url_pattern.format(ready_geo)
res = requests.get(transfer_url)
text = res.text
content = json.loads(text)
points = content['result']
points_dumps = json.dumps(points)
print (geo)
print (points_dumps)


