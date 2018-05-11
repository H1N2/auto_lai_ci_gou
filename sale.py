# coding = utf-8
import requests
import json
import time

from cfg import COOKIE as cookie
from cfg import PASSWORD as password
from cfg import BAIDU_PUBLIC_KEY as baidu_pub_key
from encrypt import sha256
from encrypt import rsa_encrypt
from ml.captcha_crack_baidu.logger import log


class Sale:
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

    # 获取宠物狗总数
    def get_pets_count(self, page_size):
        url = 'https://pet-chain.baidu.com/data/user/pet/list'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/personal?appId=1&tpl='
        data = {
            "pageNo": 1,
            "pageSize": page_size,
            "pageTotal": -1,
            "totalCount": 0,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        return response['data']['totalCount']

    # 分页获取宠物狗
    def get_pets(self, page_no, page_size, page_total, total_count):
        url = 'https://pet-chain.baidu.com/data/user/pet/list'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/personal?appId=1&tpl='
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
        info = response['data']
        return info

    def get_attribute(self, attributes, name):
        for attribute in attributes:
            if attribute['name'] == name:
                return attribute['value']

    # 创建卖出单子
    def create(self, pet_id, price):
        log('创建卖出狗狗单子 {0}，价格{1}'.format(pet_id, price))
        url = 'https://pet-chain.baidu.com/data/market/sale/shelf/create'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=center&petId=' + pet_id + '&appId=1&tpl='
        data = {
            "petId": pet_id,
            "amount": price,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('创建单子失败：{0}'.format(response['errorMsg']))

        return response

    # 确认卖出
    def confirm(self, pet_id, order_id, nonce):
        url = 'https://pet-chain.baidu.com/data/order/confirm'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=center&petId=' + pet_id + '&appId=1&tpl='
        secret = sha256(password) + '|' + order_id + '|' + nonce
        secret = rsa_encrypt(baidu_pub_key, secret)
        data = {
            "appId": 1,
            'confirmType': 1,
            "s": secret,
            "requestId": int(time.time() * 1000),
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('卖出单子确认失败: {0}'.format(response['errorMsg']))

        return response

    # 按条件卖出所有狗狗
    def sale_all(self, price=100, rare_degree=0, include_angel=False):
        page_size = 10
        total_count = self.get_pets_count(page_size)
        page_total = total_count // page_size if total_count % page_size == 0 else (total_count // page_size + 1)
        for i in range(page_total):
            pets = self.get_pets(i + 1, page_size, page_total, total_count)
            for pet in pets:
                if pet['rareDegree'] != rare_degree:
                    continue

                pet_id = pet['petId']
                if not include_angel:
                    info = self.get_pet_info(pet_id)
                    physique = self.get_attribute(info['attributes'], '体型')
                    if physique == '天使':
                        log('天使狗狗不卖： {0}'.format(pet_id))
                        continue

                response = self.create(pet['petId'], price)
                if response['errorNo'] == '00':
                    order_id = response['data']['orderId']
                    nonce = response['data']['nonce']
                    self.confirm(pet_id, order_id, nonce)

            time.sleep(5)


if __name__ == '__main__':
    sale = Sale(cookie)
    sale.sale_all(100, 0)
