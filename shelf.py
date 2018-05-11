# coding = utf-8
import requests
import json
import time

from cfg import COOKIE as cookie
from cfg import PASSWORD as password
from cfg import BAIDU_PUBLIC_KEY as baidu_pub_key
from encrypt import sha256
from encrypt import rsa_encrypt
from logger import log


class Shelf:
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

        self.rare_degree_dic = {0: '普通', 1: '稀有', 2: '卓越', 3: '史诗', 4: '神话', 5: '传说'}

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

    # 挂出繁育单条狗
    def create(self, pet_id, price):
        url = 'https://pet-chain.baidu.com/data/market/breed/shelf/create'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=center&petId=' + pet_id + '&appId=1&tpl='
        data = {
            "petId": pet_id,
            "amount": str(price),
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('创建单子失败：{0}'.format(response['errorMsg']))
            return None, None

        return response['data']['orderId'], response['data']['nonce']

    def confirm(self, pet_id, order_id, nonce):
        url = 'https://pet-chain.baidu.com/data/order/confirm'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=center&petId=' + pet_id + '&appId=1&tpl='
        secret = sha256(password) + '|' + order_id + '|' + nonce
        secret = rsa_encrypt(baidu_pub_key, secret)
        data = {
            "appId": 1,
            'confirmType': 3,
            "s": secret,
            "requestId": int(time.time() * 1000),
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('挂出繁育失败: {0}'.format(response['errorMsg']))

        return response

    # 按条件挂出繁育所有的狗
    def shelf_all(self, price=100, rare_degree=0):
        page_size = 10
        total_count = self.get_pets_count(page_size)
        page_total = total_count // page_size if total_count % page_size == 0 else (total_count // page_size + 1)
        for i in range(page_total):
            pets = self.get_pets(i + 1, page_size, page_total, total_count)
            for pet in pets:
                pet_id = pet['petId']
                if (not pet['isCooling']) and pet['shelfStatus'] == 0 and pet['rareDegree'] == rare_degree:
                    log('挂出繁育 {0}，等级 {1}，价格 {2}'.format(pet_id, self.rare_degree_dic[rare_degree], price))
                    order_id, nonce = self.create(pet['petId'], price)
                    if order_id:
                        self.confirm(pet_id, order_id, nonce)

            time.sleep(5)

    def shelf_all_once(self, price_dic=None):
        if price_dic is None:
            log('没有设置价格字典！')
            return

        page_size = 10
        total_count = self.get_pets_count(page_size)
        page_total = total_count // page_size if total_count % page_size == 0 else (total_count // page_size + 1)
        for i in range(page_total):
            pets = self.get_pets(i + 1, page_size, page_total, total_count)
            for pet in pets:
                pet_id, rare_degree = pet['petId'], pet['rareDegree']
                price = price_dic[rare_degree]
                if (not pet['isCooling']) and pet['shelfStatus'] == 0:
                    log('挂出繁育 {0}，等级 {1}，价格 {2}'.format(pet_id, self.rare_degree_dic[rare_degree], price))
                    order_id, nonce = self.create(pet_id, price)
                    if order_id:
                        self.confirm(pet_id, order_id, nonce)

            time.sleep(5)


if __name__ == '__main__':
    shelf = Shelf(cookie)
    # shelf.shelf_all(100, 0)
    # shelf.shelf_all(100, 1)
    # shelf.shelf_all(100, 2)
    rare_degree_price_dic = {0: 100, 1: 100, 2: 100, 3: 1000, 4: 100000, 5: 1000000}
    shelf.shelf_all_once(rare_degree_price_dic)
