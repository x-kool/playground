import pandas as pd

from constant import FANGTIANXIA_READY_HEADER_LIST
from crawler.crawler_enum import CrawlerSourceName, CrawlerDataLabel, CrawlerDataType
from util import get_file_path

def process_fangtianxia_parcel_raw_data(city_name):
    read_file_path = get_file_path(city_name,
                                   CrawlerDataType.RAW_DATA.value,
                                   CrawlerSourceName.FANGTIANXIA.value,
                                   CrawlerDataLabel.PARCEL.value)
    raw_data = pd.read_table(read_file_path, error_bad_lines=False)
    ready_data = process_raw_data_to_ready(raw_data)
    return ready_data

def process_raw_data_to_ready(raw_data):
    ready_data = raw_data[FANGTIANXIA_READY_HEADER_LIST]
    return ready_data