import time

category_list = {'': 0,
                 '美食': 1,
                 '购物': 2,
                 '交通设施' : 3,
                 '房地产' : 4

                 }

sub_category_list = {'' : 0,
                     '中餐厅': 1,
                     '火车站': 2
                     }


def category_transfer(category):
    if category in category_list:
        return str(category_list[category])
    else:
        category_list[category] = len(category_list)
        return str(category_list[category])


def sub_category_transfer(sub_category):
    if sub_category in sub_category_list:
        return str(sub_category_list[sub_category])
    else:
        sub_category_list[sub_category] = len(sub_category_list)
        return str(sub_category_list[sub_category])


def line_form(line):
    new_line = '\t'.join([line[0], # name
                          line[1], # lat
                          line[2], # lng
                          line[3], # address
                          line[5]]) # uid
    if len(line) > 6:
        new_line = '\t'.join([new_line, category_transfer(line[6]), sub_category_transfer(line[7])]) # category
        return new_line + '\n'
    else:
        return new_line


def get_date():
    date = time.strftime("%Y_%m_%d", time.localtime())
    return date


def read_file():
    file_name = '重庆市poi信息'
    with open(file_name, 'r+') as file:
        text = file.readlines()
        for line in text:
            l = line.split('\t')
            with open(file_name+'_transfer', 'a', encoding='utf-8') as file:
                file.write(line_form(l))


if __name__ == '__main__':
    read_file()
    print(category_list)
    print(sub_category_list)
