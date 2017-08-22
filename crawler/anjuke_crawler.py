import json
import threading
import tablib
from pypinyin import lazy_pinyin

from constant import process_num, source_name_anjuke, second_hand
from util import save_raw_data_in_tsv_file, get_response_text_with_url, get_rect_list_with_city_name, \
    get_raw_data_file_path


def crawl_anjuke_raw_data(city_name):
    crawl_anjuke_new_apt_raw_data()
    crawl_anjuke_second_hand_apt_raw_data(city_name)


def crawl_anjuke_new_apt_raw_data():
    pass


def crawl_anjuke_second_hand_apt_raw_data(city_name):
    rect_list = get_rect_list_with_city_name(city_name)
    len_of_sub_rect_list_for_thread = int(len(rect_list) / process_num)

    process_list = []

    for i in range(process_num):
        process = threading.Thread(target=crawl_raw_data_with_rect_list,
                                   args=(rect_list[i * len_of_sub_rect_list_for_thread: (
                                                                                            i + 1) * len_of_sub_rect_list_for_thread],
                                         city_name))
        process.start()
        process_list.append(process)
    for process in process_list:
        process.join()


def crawl_raw_data_with_rect_list(rect_list, city_name):
    for rect in rect_list:
        community_list = get_anjuke_2nd_community_list_with_rect(city_name, rect)
        for data in community_list:
            formed_data = get_formed_tsv_data_with_community_raw_data(data)
            file_path = get_raw_data_file_path(city_name, source_name_anjuke, second_hand)

            save_raw_data_in_tsv_file(file_path, formed_data)


# == helper ==
def get_anjuke_2nd_community_list_url(city_name, rect):
    rect0 = rect[0]
    rect1 = rect[1]
    rect2 = rect[2]
    rect3 = rect[3]
    city_name_pinyin = ''.join(lazy_pinyin(city_name))
    base_url = 'https://{}.anjuke.com/v3/ajax/map/sale/facet/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p=1&zoom=19&' \
               'lat={}_{}&lng={}_{}&kw=&maxp=99'
    url = base_url.format(city_name_pinyin, rect0, rect1, rect2, rect3)
    return url


def get_anjuke_2nd_community_list_with_rect(city_name, rect):
    rect_url = get_anjuke_2nd_community_list_url(city_name, rect)
    response_text = get_response_text_with_url(rect_url)
    if response_text:
        content = json.loads(response_text)
        if content and 'val' in content:
            text = content['val']['comms']
            return text
    return []


def get_formed_rect_list(rect_list):
    for idx, rect in enumerate(rect_list):
        rect_list[idx] = [rect[1], rect[3], rect[0], rect[2]]
    return rect_list


def get_formed_tsv_data_with_community_raw_data(community):
    raw_data = [community['truncate_name'],
                '%-.6f' % float(community['lat']),
                '%-.6f' % float(community['lng']),
                '%-s' % community['address'],
                '%-s' % community['mid_price'],
                '%-s' % community['id'],
                '%-s' % community['prop_num']]
    if community['mid_change']:
        raw_data.append('%-.3f' % (float(community['mid_change'])))
    data = tablib.Dataset(*[raw_data])
    return data
