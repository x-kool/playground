import time
import pandas as pd
import requests
import json
import re


def get_date(format="%Y_%m_%d"):
    date = time.strftime(format, time.localtime())
    return date


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


def get_geo_list(raw_data):
    l_raw_data = len(raw_data)
    try:
        l = len(geo_list)
        for idx, uid in enumerate(raw_data['uid'][l:]):
            url_lunkuo_pattern = 'http://map.baidu.com/?pcevaname=pc4.1&qt=ext&uid={}&ext_ver=new&l=12'
            url = url_lunkuo_pattern.format(uid)
            res = requests.get(url, timeout=5)
            text = res.text
            res = json.loads(text)
            geo = res['content']['geo']
            geo_list.append(geo)
            print('get_geo_list : ' + str(l + idx) + '/' + str(l_raw_data))
    except:
        if len(geo_list) == len(raw_data['uid']):
            num_geo = 0
            for i in geo_list:
                if i != '':
                    num_geo += 1
            print('total with border : {}'.format(num_geo))
            return
        else:
            get_geo_list(raw_data)


def get_transfer_location(processed_geo_list, num):
    transfer_url_pattern = 'http://api.map.baidu.com/geoconv/v1/?coords={}&from=6&to=5&ak=GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'
    l = len(processed_geo_list)
    try:
        for idx, geo in enumerate(processed_geo_list[num:]):
            print('get_transfer_location : ' + str(num) + '/' + str(l))
            num += 1
            if len(geo) > 1:
                ready_geo = get_ready(geo[1])
                single_community_point_list = ready_geo.split(',')
                if len(single_community_point_list) < 90:
                    transfer_url = transfer_url_pattern.format(ready_geo)
                    res = requests.get(transfer_url)
                    text = res.text
                    content = json.loads(text)
                    points = content['result']
                    points_dumps = json.dumps(points)
                    points_list.append([geo[0], points_dumps])
                else:
                    tmp_point_list = []
                    split_num = 90
                    single_community_point_list = geo[1].split(',')
                    num_transfer = int(len(single_community_point_list) / split_num)
                    geo_list = [single_community_point_list[i * split_num:(i + 1) * split_num] for i in
                                range(num_transfer)] + [single_community_point_list[num_transfer * split_num:]]
                    str_geo_list = [','.join(geo) for geo in geo_list]
                    for temp_geo in str_geo_list:
                        ready_geo = get_ready(temp_geo)
                        transfer_url = transfer_url_pattern.format(ready_geo)
                        res = requests.get(transfer_url)
                        text = res.text
                        content = json.loads(text)
                        points = content['result']
                        tmp_point_list.extend(points)
                    points_dumps = json.dumps(tmp_point_list)
                    points_list.append([geo[0], points_dumps])
    except:
        if num == len(processed_geo_list):
            return
        else:
            get_transfer_location(processed_geo_list, num)


def get_processed_geo_list(geo_list):
    pattern = re.compile('1-(.*?);')
    processed_geo_list = []
    for idx, geo in enumerate(geo_list):
        processed_geo = re.findall(pattern, geo)
        res = [raw_data['name'][idx]] + processed_geo
        processed_geo_list.append(res)
    return processed_geo_list


# raw_data = raw_data[0:500]
# city_list = ['shenzhen','guangzhou','beijing','chongqing','shanghai','tianjin']
city_list = ['chongqing', 'beijing', 'shanghai', 'tianjin']
for city_name in city_list:
    # city_name = 'guangzhou'
    read_file_path = 'E:\\PycharmPrjects\\playground\\poi_data\\2017_09_01\\{}\\ready_data\\{}_baidu_poi_2017_09_01.tsv'.format(
        city_name, city_name)
    raw_data = pd.read_table(read_file_path, error_bad_lines=False)

    geo_list = []
    get_geo_list(raw_data)

    processed_geo_list = get_processed_geo_list(geo_list)

    points_list = []
    get_transfer_location(processed_geo_list, 0)

    # save
    date = get_date()

    save_file_path = 'E:\\building_processed_data\\{}_community_border_{}.tsv'.format(city_name, date)

    points_list_pd = pd.DataFrame(points_list)

    points_list_pd.to_csv(path_or_buf=save_file_path, sep='\t', encoding='utf-8')
