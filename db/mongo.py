# coding = utf-8

import requests
import json
import time
import traceback
from pymongo import MongoClient
from cfg import COOKIE as cookie
from ml.captcha_crack_baidu.logger import log


class Query:
    def __init__(self, cookie):
        self.cookie = cookie

        self.client = MongoClient()

        db = self.client['lai_ci_gou']

        self.pet_coll = db['pet']

        self.headers_template = {
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6',
            'Content-Type': 'application/json',
            'Cookie': self.cookie,
            'Host': 'pet-chain.baidu.com',
            'Origin': 'https://pet-chain.baidu.com',
            'Referer': 'https://pet-chain.baidu.com/chain/dogMarket?appId=1&tpl=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }

    def get_paging_pets(self, page_no):
        url = 'https://pet-chain.baidu.com/data/market/queryPetsOnSale'
        headers = self.headers_template
        data = {
            "pageNo": page_no,
            "pageSize": 10,
            "lastAmount": "",
            "lastRareDegree": "",
            "filterCondition": "{}",
            "querySortType": "AMOUNT_ASC",
            "petIds": [],
            "requestId": 1522208927587,
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
            "requestId": 1521513963266,
            "appId": 1,
            "tpl": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        return response['data']

    # 获取狗狗并保存
    def get_save_pets(self):
        i = 1
        while True:
            try:
                log('第{0}页'.format(i))
                pets = self.get_paging_pets(i)
                for pet in pets:
                    pet_id = pet['petId']
                    count = self.pet_coll.find({"petId": pet_id}).count()
                    if count != 0:
                        continue

                    info = self.get_pet_info(pet_id)
                    pet = {
                        'id': info['id'],
                        'petId': info['petId'],
                        'generation': info['generation'],
                        'rareDegree': info['rareDegree'],
                        'bgColor': info['bgColor'],
                        'petUrl': info['petUrl'],
                        'attributes': info['attributes'],
                        'father_id': info['father']['petId'] if info['father'] else None,
                        'mother_id': info['mother']['petId'] if info['father'] else None,
                    }
                    self.pet_coll.insert(pet)
                    log('保存狗狗{0}'.format(info['id']))
                i = i + 1
                time.sleep(5)
            except:
                traceback.print_exc()
                time.sleep(5)


if __name__ == '__main__':
    query = Query(cookie)
    query.get_save_pets()
    pass
