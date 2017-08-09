import json

import requests
from requests import RequestException

url = 'http://cq.fang.lianjia.com/xinfang/mapsearchloupan?&&callback=speedupjsonpapi&_=1502246125390'
city_name = '重庆'


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


def get_info(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            return html
        return None
    except RequestException:
        print('链接错误')
        return None


def save_and_write_resblock_info(resblock):
    with open('%s新楼盘信息' % city_name, 'a') as file:
        print('正在写入：{}'.format(str(info_to_string(resblock))))
        file.write(info_to_string(resblock))


def parse_info(html):
    data = json.loads(html[20:-1])
    if data and 'data' in data.keys():
        return data['data']


def info_to_string(resblock):
    space_num = 21 if len(resblock['name']) == 3 else 20
    line = '\t'.join(
                     [myAlign(resblock['resblock_name'], space_num),
                      myAlign('%-20s' % (resblock['district_id']), 20),
                      myAlign('%-10s' % (resblock['district_type']), 10),
                      myAlign('%-.6f' % (resblock['latitude']), 20),
                      myAlign('%-.6f' % (resblock['longitude']), 20),
                      myAlign('%-6s' % (resblock['average_price']), 20),
                      myAlign('%-6s' % (resblock['show_price']), 20),
                      myAlign('%-20s' % (resblock['rooms']), 20),
                      myAlign('%-20s' % (resblock['resblock_frame_area']), 20),
                      myAlign('%-5s' % (resblock['min_frame_area']), 20),
                      myAlign('%-5s' % (resblock['max_frame_area']), 20)]
                     )
    return line + '\n'


def get_all_resblock_info():
    html = get_info(url)
    text = parse_info(html)
    for resblock_list in text.values():
        for res in resblock_list:
            save_and_write_resblock_info(res)


def main():
    get_all_resblock_info()


if __name__ == '__main__':
    main()
