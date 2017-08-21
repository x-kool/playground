# -*- coding: utf-8 -*-
import re

building_type = {'': 0,
                 '高层': 1,
                 '超高层': 2,
                 '多层': 3,
                 '小高层': 4,
                 '标准写字楼': 5,
                 '联排别墅': 6,
                 '双拼别墅': 7,
                 '叠加别墅': 8,
                 '独栋别墅': 9,
                 '花园洋房': 10,
                 '创意园区': 11,
                 '企业独栋': 12,
                 '商住': 13,
                 }


fitment_list = {'毛坯': 0,
                '精装修': 1,
                '简装': 2}

def building_type_transfer(strings):
    table = str.maketrans(',', ' ')
    line = strings.translate(table).split()
    tmp_list = []
    for k in line:
        if k in building_type:
            tmp_list.append(building_type[k])
        else:
            building_type[k] = len(building_type)
    return str(tmp_list)


def fitment_transfer(fitment):
    table = str.maketrans(',', ' ')
    line = fitment.translate(table).split()
    tmp_list = []

    for fit in line:
        if fit in fitment_list:
            tmp_list.append(fitment_list[fit])
        else:
            fitment_list[fit] = len(fitment_list)
    return str(tmp_list)


# 户型转换for 安居客楼盘
def residence_transfer(residence):
    tmp_list = []
    for k in residence[9:]:
        if k:
            pattern = re.compile('户型: (.*?)面积')
            res = re.findall(pattern, k)
            if res:

                int_res = re.findall('\d', res[0])
                if int_res:
                    tmp_list.append([int(i) for i in int_res])
                else:
                    tmp_list.append([0])
    return str(tmp_list)


# 楼型转换 for 安居客楼盘
def building_type_transfer(strings):
    table = str.maketrans(',', ' ')
    line = strings.translate(table).split()
    tmp_list = []
    for k in line:
        if k in building_type:
            tmp_list.append(building_type[k])
        else:
            building_type[k] = len(building_type)
    return str(tmp_list)


# 面积转换 for 安居客
def area_transfer(residence):
    tmp_list = []
    for k in residence[9:]:
        if k:
            pattern = re.compile('面积: (.*?) ]')
            res = re.findall(pattern, k)
            if res:
                tmp_list.append(int(res[0]))
    return str(tmp_list)


def line_form(line):
    new_line = '\t'.join([line[0],
                          line[1],
                          building_type_transfer(line[2]),
                          line[3],
                          line[4],
                          line[5],
                          fitment_transfer(line[6]),
                          line[7],
                          area_transfer(line),
                          residence_transfer(line)])
    return new_line + '\n'


def read_file():
    file_name = '重庆_安居客_新房_小区_2017_08_21'
    with open(file_name, 'r+', encoding='utf-8') as file:
        text = file.readlines()
        for line in text:
            l = line.split('\t')
            with open(file_name+'_transfer', 'a', encoding='utf-8') as file:
                file.write(line_form(l))


if __name__ == '__main__':
    read_file()
    print(building_type)
    print(fitment_list)
