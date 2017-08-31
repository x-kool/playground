import platform
import time
import os
import pandas as pd
from pypinyin import lazy_pinyin


def save_raw_data_in_tsv_file(file_path, data_dict_list):
    data_dict_list_pd = pd.DataFrame(data_dict_list)
    data_dict_list_pd.to_csv(path_or_buf=file_path, sep='\t', encoding='utf-8')


def get_date(format="%Y_%m_%d"):
    date = time.strftime(format, time.localtime())
    return date


def is_windows_system():
    return 'Windows' in platform.system()


def get_file_path(city_name, data_type, source_name, data_label):
    date = get_date()
    city_name_pinyin = ''.join(lazy_pinyin(city_name))
    path = os.path.join(os.path.dirname(os.getcwd()), 'poi_data', str(date), city_name_pinyin, data_type)
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = path + '\{}_{}_{}_{}.tsv'.format(city_name_pinyin, source_name, data_label, date)
    if not is_windows_system():
        Linux_file_path = file_path.replace('\\', '/')
        return Linux_file_path
    return file_path
