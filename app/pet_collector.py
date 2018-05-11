# coding = utf-8

import requests
import json
import time
import traceback
from pymongo import MongoClient
from cfg import COOKIE as cookie
from ml.captcha_crack_baidu.logger import log


class Collector:
    def __init__(self, cookie):
        self.cookie = cookie

        self.client = MongoClient()

        db = self.client['lai_ci_gou']

        self.pets = db['pets']

        self.pet_attributes = db['attributes']

        self.headers_template = {
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6',
            'Content-Type': 'application/json',
            'Cookie': self.cookie,
            'Host': 'pet-chain.baidu.com',
            'Origin': 'https://pet-chain.baidu.com',
            'Referer': 'https://pet-chain.baidu.com/chain/dogMarket?appId=1&tpl=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }

        self.rare_degree_dic = {0: '普通', 1: '稀有', 2: '卓越', 3: '史诗', 4: '神话', 5: '传说'}

    def get_paging_pets(self, page_no, rare_degree):
        url = 'https://pet-chain.baidu.com/data/market/queryPetsOnSale'
        headers = self.headers_template
        data = {
            "pageNo": page_no,
            "pageSize": 10,
            "lastAmount": "",
            "lastRareDegree": "",
            "filterCondition": "{\"1\":\"" + str(rare_degree) + "\"}",
            "querySortType": "AMOUNT_ASC",
            "petIds": [],
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        pets = response['data']['petsOnSale']
        return pets

    def get_pet_info(self, pet_id):
        url = 'https://pet-chain.baidu.com/data/pet/queryPetById'
        headers = self.headers_template
        headers[
            'Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=market&petId=' + pet_id + '&validCode=&appId=1&tpl='
        data = {
            "petId": pet_id,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        return response['data']

    # 保存狗狗到数据库
    def save_pet(self, pet_info):
        pet = {
            'id': pet_info['id'],
            'petId': pet_info['petId'],
            'generation': pet_info['generation'],
            'rareDegree': pet_info['rareDegree'],
            'fatherId': pet_info['father']['petId'] if pet_info['father'] else None,
            'motherId': pet_info['mother']['petId'] if pet_info['father'] else None,
            'bgColor': pet_info['bgColor'],
            'petUrl': pet_info['petUrl'],
            'attributes': pet_info['attributes'],
        }
        self.pets.insert(pet)
        log('保存狗狗{0}'.format(pet_info['petId']))

    # 保存或者更新属性数据
    def save_update_attributes(self, attributes):
        for attribute in attributes:
            exist = self.pet_attributes.find_one(attribute)
            if exist:
                self.pet_attributes.update_one({
                    '_id': exist['_id']
                }, {
                    '$inc': {
                        'amount': 1
                    }
                }, upsert=False)
            else:
                attribute['amount'] = 0
                self.pet_attributes.insert(attribute)

    # 查询并保存狗狗及其祖宗（如果有的话）
    def query_save_pet_and_ancestors(self, pet_id):
        info = self.get_pet_info(pet_id)
        self.save_pet(info)
        self.save_update_attributes(info['attributes'])

        if info['father']:
            log('狗狗父亲{0}'.format(info['father']['petId']))
            self.query_save_pet_and_ancestors(info['father']['petId'])
            log('狗狗母亲{0}'.format(info['mother']['petId']))
            self.query_save_pet_and_ancestors(info['mother']['petId'])
        else:
            return

    # 按指定稀有度查询狗狗
    def get_save_pets(self, rare_degree):
        page_no = 1
        while True:
            log('第{0}页{1}狗狗'.format(page_no, self.rare_degree_dic[rare_degree]))
            pets = self.get_paging_pets(page_no, rare_degree)
            for pet in pets:
                count = self.pets.find({"petId": pet['petId']}).count()
                if count != 0:
                    continue

                self.query_save_pet_and_ancestors(pet['petId'])

            page_no = page_no + 1
            time.sleep(5)

    # 按稀有度循环查询狗狗
    # 当前查询的稀有度出现异常时，进入下一个稀有度进行查询，否则将使用当前稀有度一直查询下去
    def get_save_all_pets(self):
        rare_degree = 0
        while True:
            try:
                self.get_save_pets(rare_degree)
            except:
                rare_degree = rare_degree + 1
                if rare_degree > 5:
                    rare_degree = 0
                traceback.print_exc()


if __name__ == '__main__':
    collector = Collector(cookie)
    collector.get_save_all_pets()
    pass
