import json
import threading
import requests
import time
from requests import RequestException
from retrying import retry
from logger import FinalLogger


from constant import ak, city_center_base_url, timeout, process_num, steps, headers, distance_unit













# ======
# 這裡需要的rect的格式： lat_min,lat_max,lng_min,lng_max
def get_anjuke_rect_form(rect):
    formed_rect = [rect[1], rect[3],rect[0],rect[2]]
    return formed_rect


def get_anjuke_2nd_hand_community_rect_url(rect):
    base_url = 'https://chongqing.anjuke.com/v3/ajax/map/sale/facet/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p=1&zoom=19&' \
               'lat={}_{}&lng={}_{}&kw=&maxp=99'
    url = base_url.format(*rect)
    return url


def save_and_write_community_info(self, resblock):
    with open('{}_安居客_二手_小区_{}'.format(self.city_name, self.get_date()), 'a', encoding='utf-8') as file:
        print(u'正在写入：{}'.format(str(self.info_to_string(resblock))))
        file.write(self.info_to_string(resblock))


def get_anjuke_community_info(self, html):
    if html:
        content = json.loads(html)
        if content and 'val' in content:
            text = content['val']['comms']
            return text
    return None


def info_to_string(self, community):
        line = '\t'.join(
            [community['truncate_name'],
             '%-.6f' % float(community['lat']),
             '%-.6f' % float(community['lng']),
             '%-s' % community['address'],
             '%-s' % community['mid_price'],
             '%-s' % community['id'],
             '%-s' % community['prop_num']]
        )
        if community['mid_change']:
            line += '\t' + '%-.3f' % (float(community['mid_change']))
        return line + '\n'


# ================================================================
def get_all_community_price_info(self):
    self.get_rects_by_center()
    for rect in self.rect_list:
        rect_url = self.get_url(rect)
        html = self.get_html(rect_url)
        data = self.parse_info(html)
        if data:
            for community in data:
                self.save_and_write_community_info(community)

# =================================================================

    @retry(stop_max_attempt_number=10)
    def get_info_in_rect(self, rect):
        rect_url = self.get_url(rect)
        html = self.get_html(rect_url)
        data = self.parse_info(html)
        if data:
            for community in data:
                self.save_and_write_community_info(community)


    def get_info_in_rect_list(self, rect_list):
        l = len(rect_list)
        for idx,rect in enumerate(rect_list):
            self.get_info_in_rect(rect)
            print (str(idx) + '/' + str(l))


    def get_all_community_price_info_with_Thread(self):
        self.get_rects_by_center()
        len_rects = int(len(self.rect_list) / self.process_num)
        process_list = []
        for i in range(self.process_num):
            process = threading.Thread(target=self.get_info_in_rect_list,
                                       args=(self.rect_list[i * len_rects : (i+1) * len_rects ], ))
            process.start()
            process_list.append(process)
        for process in process_list:
            process.join()

    def main(self, Thread):
        start = time.clock()

        if Thread == 0:
            self.get_all_community_price_info()
        elif Thread == 1:
            self.get_all_community_price_info_with_Thread()

        end = time.clock()
        print ('运行时间：%-.2f s' % (end-start))


if __name__ == '__main__':
    crawler = AJK2ndCommunityCrawler('重庆',4)
    crawler.main(1)
