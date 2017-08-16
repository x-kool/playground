import re

import requests
from bs4 import BeautifulSoup
from requests import RequestException

city_name = '重庆'
page_size = 33
page_base_url = 'http://land.fang.com/market/500100________1_0_{}.html'
parcel_base_url = 'http://land.fang.com'
parcel_url_list = []


def myAlign(string, length=0):
    if length == 0:
        return string
    slen = len(string)
    res = string
    if isinstance(string, str):
        placeholder = ' '
    else:
        placeholder = u'　'
    while slen < length:
        res += placeholder
        slen += 1
    return res


def get_info(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('链接错误')
        return None


def get_parcel_url_list():
    for page_num in range(1, page_size+1):
        url = page_base_url.format(page_num)
        text = get_info(url)
        soup = BeautifulSoup(text)
        # 得到该页面内的 parcel 的 url
        for i in soup.select('h3'):
            parcel_url = parcel_base_url + i.contents[1]['href']
            parcel_url_list.append(parcel_url)


def get_parcel_data(parcel_url):
    text = get_info(parcel_url)
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


def save_and_write_parcel_data(parcel_data, name=city_name):
    with open('%s地块信息（房天下）' % name, 'a', encoding='utf-8') as file:
        # print('正在写入：{}'.format(str(info_to_string(parcel_data))))
        file.write(info_to_string(parcel_data))
        

def info_to_string(parcel_data):
    line = '\t'.join(
        [myAlign('%-100s' % (parcel_data['位置']), 100),
         myAlign('%-10s' % (parcel_data['地区']), 10),
         myAlign('%-10s' % (parcel_data['所在地']), 10),
         myAlign('%-10s' % (parcel_data['lat']), 10),
         myAlign('%-10s' % (parcel_data['lng']), 10),         
         myAlign('%-50s' % (parcel_data['地块编号']), 50),
         myAlign('%-10s' % (parcel_data['总面积']), 10),
         myAlign('%-10s' % (parcel_data['建设用地面积']), 10),
         myAlign('%-10s' % (parcel_data['规划建筑面积']), 10),
         myAlign('%-10s' % (parcel_data['代征面积']), 10),
         myAlign('%-10s' % (parcel_data['容积率']), 10),
         myAlign('%-10s' % (parcel_data['绿化率']), 10),
         myAlign('%-10s' % (parcel_data['商业比例']), 10),
         myAlign('%-10s' % (parcel_data['建筑密度']), 10),
         myAlign('%-10s' % (parcel_data['限制高度']), 10),
         myAlign('%-10s' % (parcel_data['出让形式']), 10),
         myAlign('%-10s' % (parcel_data['出让年限']), 10),
         myAlign('%-100s' % (parcel_data['四至']), 100),
         myAlign('%-30s' % (parcel_data['规划用途']), 30),
         myAlign('%-6s' % (parcel_data['交易状况']), 6),
         myAlign('%-30s' % (parcel_data['竞得方']), 30),
         myAlign('%-20s' % (parcel_data['起始日期']), 20),
         myAlign('%-20s' % (parcel_data['截止日期']), 20),
         myAlign('%-20s' % (parcel_data['成交日期']), 20),
         myAlign('%-10s' % (parcel_data['起始价']), 10),
         myAlign('%-10s' % (parcel_data['成交价']), 10),
         myAlign('%-10s' % (parcel_data['楼面地价']), 10),
         myAlign('%-10s' % (parcel_data['溢价率']), 10),
         myAlign('%-20s' % (parcel_data['咨询电话']), 20),
         myAlign('%-10s' % (parcel_data['保证金']), 10),
         myAlign('%-10s' % (parcel_data['最小加价幅度']), 10)]
    )
    print (myAlign('%-100s' % (parcel_data['位置']), 100))
    return line + '\n'


def get_all_parcel_info():
    get_parcel_url_list()
    parcel_num = len(parcel_url_list)
    
    for parcel_url_num in range(parcel_num):
        parcel_data = get_parcel_data(parcel_url_list[parcel_url_num])
        save_and_write_parcel_data(parcel_data)
        print (str(parcel_url_num+1) + '/' + str(parcel_num))

def main():
    get_all_parcel_info()


if __name__ == '__main__':
    main()
