import threading
import time

from constant import process_num
from util import get_anjuke_2nd_community_url, get_anjuke_2nd_community_info, get_tsv_formed_data, save_and_write_info, \
                 get_response_text_with_url, get_rect_list


def get_formed_rect_list(rect_list):
    for idx,rect in enumerate(rect_list):
        rect_list[idx] = [rect[1], rect[3], rect[0], rect[2]]
    return rect_list


def get_and_write_info_in_rect(rect, city_name, source, service_life):
    rect_url = get_anjuke_2nd_community_url(city_name, rect)
    html = get_response_text_with_url(rect_url)
    text = get_anjuke_2nd_community_info(html)
    if text:
        for data in text:
            formed_data = get_tsv_formed_data(data, source, service_life)
            save_and_write_info(city_name, source, service_life, formed_data)


def get_info_in_rect_list(rect_list, city_name, source, service_life):
    l = len(rect_list)
    for idx,rect in enumerate(rect_list):
        get_and_write_info_in_rect(rect, city_name, source, service_life)
        print (str(idx) + '/' + str(l))


def get_all_community_price_info_with_Thread(city_name, source, service_life):
    rect_list = get_rect_list(city_name)
    rect_list = get_formed_rect_list(rect_list)
    len_rect_list = int(len(rect_list) / process_num)
    process_list = []
    for i in range(process_num):
        process = threading.Thread(target=get_info_in_rect_list,
                                   args=(rect_list[i * len_rect_list : (i+1) * len_rect_list ],
                                         city_name,
                                         source,
                                         service_life))
        process.start()
        process_list.append(process)
    for process in process_list:
        process.join()


def get_anjuke_2nd_hand_community_info(city_name, source, service_life):

    start = time.clock()
    get_all_community_price_info_with_Thread(city_name, source, service_life)
    end = time.clock()
    print ('运行时间：%-.2f s' % (end-start))


if __name__ == '__main__':
    get_anjuke_2nd_hand_community_info('重庆','安居客','二手')

