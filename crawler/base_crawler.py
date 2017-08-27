import threading
from multiprocessing.pool import ThreadPool
import requests
from retrying import retry

from constant import THREAD_NUM, STEP_NUM, UNIT_DISTANCE, city_center_url_pattern, BAIDU_API_AK, TIMEOUT, HEADERS


class BaseCrawler(object):
    def __init__(self, city_name, thread_num=THREAD_NUM, step_num=STEP_NUM, unit_distance=UNIT_DISTANCE):
        self.city_name = city_name
        self.thread_num = thread_num
        self.step_num = step_num
        self.unit_distance = unit_distance


    def get_city_center_lng_lat_by_city_name(self, city_name):
        city_url = city_center_url_pattern.format(city_name, BAIDU_API_AK)
        try:
            response = requests.get(city_url, timeout=TIMEOUT)
            response_dict = response.json()
            location = response_dict['result']['location']
            return location['lng'], location['lat']
        except:
            raise ConnectionError

    @retry(stop_max_attempt_number=10)
    def get_response_text_with_url(self, url):
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.text
        return None

    def crawl_raw_data_by_thread_with_rect_list_func_and_city_name(self, func_name, city_name):
        lng, lat = self.get_city_center_lng_lat_by_city_name(city_name)
        rect_list = self.get_rect_list_by_lng_lat(lng, lat)
        len_of_sub_rect_list_for_thread = int(len(rect_list) / self.thread_num)
        thread_list = []
        for i in range(self.thread_num):
            thread = threading.Thread(target=func_name,
                                      args=(rect_list[i * len_of_sub_rect_list_for_thread: (i + 1) * len_of_sub_rect_list_for_thread],
                                            ))
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()

    def get_rect_list_by_lng_lat(self, lng, lat):
        # 经纬度+-1.2度范围
        rect_list = []
        for units_lng in range(self.step_num):
            dist_lng = units_lng * self.unit_distance
            for units_lat in range(self.step_num):
                dist_lat = units_lat * self.unit_distance
                rect_list.append(['%.6f' % (lng - dist_lng - self.unit_distance),
                                  '%.6f' % (lat - dist_lat - self.unit_distance),
                                  '%.6f' % (lng - dist_lng),
                                  '%.6f' % (lat - dist_lat)])

                rect_list.append(['%.6f' % (lng + dist_lng),
                                  '%.6f' % (lat - dist_lat - self.unit_distance),
                                  '%.6f' % (lng + dist_lng + self.unit_distance),
                                  '%.6f' % (lat - dist_lat)])

                rect_list.append(['%.6f' % (lng - dist_lng - self.unit_distance),
                                  '%.6f' % (lat + dist_lat),
                                  '%.6f' % (lng - dist_lng),
                                  '%.6f' % (lat + dist_lat + self.unit_distance)])

                rect_list.append(['%.6f' % (lng + dist_lng),
                                  '%.6f' % (lat + dist_lat),
                                  '%.6f' % (lng + dist_lng + self.unit_distance),
                                  '%.6f' % (lat + dist_lat + self.unit_distance)])
        return rect_list

    def new_get_rect_list_by_lng_lat(self, center_lng, center_lat):
        rect_list = []
        start_point_lng = center_lng - self.step_num * self.unit_distance / 2
        start_point_lat = center_lat - self.step_num * self.unit_distance / 2
        for idx_in_lng in range(self.step_num):
            lower_left_lng = start_point_lng + idx_in_lng * self.unit_distance
            for idx_in_lat in range(self.step_num):
                lower_left_lat = start_point_lat + idx_in_lat * self.unit_distance
                rect_list.append(['%.6f' % (lower_left_lng),
                                  '%.6f' % (lower_left_lat),
                                  '%.6f' % (lower_left_lng + self.unit_distance),
                                  '%.6f' % (lower_left_lat + self.unit_distance)])
        return rect_list

    def thread_for_crawler(self, thread_num, func_in_thread, input_list, func_to_callback):
        pool = ThreadPool(processes=thread_num)
        for i in range( len(input_list) ):
            async_result = pool.apply_async(func_in_thread, (input_list[i],), callback=func_to_callback)
        pool.close()
        pool.join()