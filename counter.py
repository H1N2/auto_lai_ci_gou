# coding = utf-8
import requests
import json
import time

from cfg import COOKIE as cookie
from ml.captcha_crack_baidu.logger import log


class Counter:
    def __init__(self, cookie):
        self.cookie = cookie

        self.headers_template = {
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6',
            'Content-Type': 'application/json',
            'Cookie': self.cookie,
            'Host': 'pet-chain.baidu.com',
            'Origin': 'https://pet-chain.baidu.com',
            'Referer': 'https://pet-chain.baidu.com/chain/dogMarket?appId=1&tpl=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }

        self.rare_degree_data = {}

        self.rare_degree_dic = {0: '普通', 1: '稀有', 2: '卓越', 3: '史诗', 4: '神话', 5: '传说'}

        self.attributes_names = ['体型', '花纹', '眼睛', '眼睛色', '嘴巴', '肚皮色', '身体色', '花纹色']

        self.types = []

    # 获取宠物狗总数
    def get_pets_count(self, page_size):
        url = 'https://pet-chain.baidu.com/data/user/pet/list'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/personal'
        data = {
            "pageNo": 1,
            "pageSize": page_size,
            "pageTotal": -1,
            "totalCount": 0,
            "requestId": int(time.time() * 1000),
            "appId": 1, "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        return response['data']['totalCount']

    # 分页获取宠物狗
    def get_pets(self, page_no, page_size, page_total, total_count):
        url = 'https://pet-chain.baidu.com/data/user/pet/list'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/personal'
        data = {
            "pageNo": page_no,
            "pageSize": page_size,
            "pageTotal": page_total,
            "totalCount": total_count,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        log(response)
        return response['data']['dataList']

    # 获取狗狗详细信息
    def get_pet_info(self, pet_id):
        url = 'https://pet-chain.baidu.com/data/pet/queryPetByIdWithAuth'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=center&petId=' + pet_id + '&appId=1&tpl='
        data = {
            "petId": pet_id,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        return response['data']

    # 按稀有等级统计狗狗数量
    def count_pets_amount_by_rare_degree(self):
        page_size = 10
        total_count = self.get_pets_count(page_size)
        page_total = total_count // page_size if total_count % page_size == 0 else (total_count // page_size + 1)
        for i in range(page_total):
            pets = self.get_pets(i + 1, page_size, page_total, total_count)
            for pet in pets:
                rare_degree = self.rare_degree_dic[pet['rareDegree']]
                if rare_degree in self.rare_degree_data:
                    self.rare_degree_data[rare_degree] = self.rare_degree_data[rare_degree] + 1
                else:
                    self.rare_degree_data[rare_degree] = 1
            log(self.rare_degree_data)
            time.sleep(5)

    # 按属性统计狗狗，所有属性完全相同的才算是同一类狗狗
    # 此方法主要是为了统计出双胞胎、三胞胎...狗狗
    def sort_pets_by_attributes(self):
        page_size = 10
        total_count = self.get_pets_count(page_size)
        page_total = total_count // page_size if total_count % page_size == 0 else (total_count // page_size + 1)
        for i in range(page_total):
            pets = self.get_pets(i + 1, page_size, page_total, total_count)
            for pet in pets:
                info = self.get_pet_info(pet['petId'])
                self.check_attributes(info)
            time.sleep(5)
        log(self.types)

    def get_attribute_value(self, attributes, name):
        for attribute in attributes:
            if attribute['name'] == name:
                return attribute['value']

    # 对比狗狗属性信息，归类保存到self.types数据集
    def check_attributes(self, info):
        for exist_type in self.types:
            flag = True
            for attribute_name in self.attributes_names:
                exist_value = self.get_attribute_value(exist_type['attributes'], attribute_name)
                value = self.get_attribute_value(info['attributes'], attribute_name)
                if exist_value != value:
                    flag = False
                    break

            if flag:
                exist_type['petIds'].append(info['petId'])
                log('有相同类型的狗狗')
                return

        log('没有相同类型的狗狗')
        t = {
            'petIds': [info['petId']],
            'attributes': info['attributes']
        }
        self.types.append(t)

    def get_pets_of_rare_degree(self, rare_degree):
        pets_list = []
        page_size = 10
        total_count = self.get_pets_count(page_size)
        page_total = total_count // page_size if total_count % page_size == 0 else (total_count // page_size + 1)
        for i in range(page_total):
            pets = self.get_pets(i + 1, page_size, page_total, total_count)
            for pet in pets:
                if rare_degree == pet['rareDegree']:
                    pets_list.append(pet['petId'])
            log(pets_list)
            time.sleep(5)


if __name__ == '__main__':
    counter = Counter(cookie)
    counter.count_pets_amount_by_rare_degree()
    # counter.sort_pets_by_attributes()
    #counter.get_pets_of_rare_degree(3)
