

class PoiEvaluator(object):
    def eval(self, location):   # location: [lng,lat]
        pass


    def eval_traffic(self):

        pass


    def eval_poi(self):
        pass


    def eval_community(self):
        pass


    def eval_parcel(self):
        pass


    def get_poi_info(self, center, radius):
        # 配套的 银行，学校，公园，超市，饭店，医院
        # 商业类的信息：写字楼，公司 这个可以按照一类进行归纳
        # 输出： list：[num(银), num(学), num(医), num(购), num(吃), num(绿), ]
        pass


    def get_traffic_info(self, center, radius=2):
        # 输入中心点，输出 半小时和一小时到达范围数据
        # 输出 1km-2km-5km 范围内，公交站和地铁站的list
        # 最好有公交站和地铁站的具体信息
        # 停车场信息也应该有

        # 应该拆分成2个func，一个是传统范围内的点数据list
        # 另一个得到等时线
        pass

    def get_parcel_info(self, center, radius):
        # 一定范围内的地块信息 相对详细

        pass


    def get_community_info(self, center, radius):
        # 输入中心点-半径，输出范围内楼盘均价，户型种类，
        #
        pass

