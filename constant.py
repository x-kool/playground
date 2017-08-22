




headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}

ak = 'GEPiAH9zkDx5oy4K1Vj7Znw8zmbGhY0M'
city_center_base_url = 'https://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'
timeout = 5

steps = 100
distance_unit = 0.005
rect_list = []
process_num = 4