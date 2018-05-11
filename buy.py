# coding = utf-8

import requests
import json
import time
import traceback

from cfg import COOKIE as cookie
from cfg import PASSWORD as password
from cfg import BAIDU_PUBLIC_KEY as baidu_pub_key
from encrypt import sha256
from encrypt import rsa_encrypt
from ml.captcha_crack_baidu.logger import log
# from ml.captcha_crack_baidu.captcha_crack import Crack
from ml.captcha_recognize.captcha_recognize_new import Crack


class Buy:
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

        self.crack = Crack()

    def get_pets(self):
        url = 'https://pet-chain.baidu.com/data/market/queryPetsOnSale'
        headers = self.headers_template
        data = {
            "pageNo": 1,
            "pageSize": 10,
            "lastAmount": "",
            "lastRareDegree": "",
            "filterCondition": "{}",
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

    def get_pets_with_condition(self, rare_degree):
        url = 'https://pet-chain.baidu.com/data/market/queryPetsOnSale'
        headers = self.headers_template
        data = {
            "pageNo": 1,
            "pageSize": 10,
            "lastAmount": "",
            "lastRareDegree": "",
            "filterCondition": "{\"1\":" + str(rare_degree) + ",\"3\":\"0-1\"}",
            # "filterCondition": "{\"1\":" + str(rare_degree) + ",\"3\":\"0-1\",\"5\":\"0-1000\"}",
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

    def get_pet_info(self, pet_id, valid_code):
        url = 'https://pet-chain.baidu.com/data/pet/queryPetById'
        headers = self.headers_template
        headers[
            'Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=market&petId=' + pet_id + '&validCode=' + valid_code + '&appId=1&tpl='
        data = {
            "petId": pet_id,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        return response['data']

    def get_attribute(self, attributes, name):
        for attribute in attributes:
            if attribute['name'] == name:
                return attribute['value']

    def get_captcha_and_seed(self, pet_id, valid_code):
        url = 'https://pet-chain.baidu.com/data/captcha/gen'
        headers = self.headers_template
        headers[
            'Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=market&petId=' + pet_id + '&validCode=' + valid_code + '&appId=1&tpl='
        data = {
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('获取验证码失败：{0}'.format(response['errorMsg']))
            return None, None

        return response['data']['seed'], response['data']['img']

    def create(self, pet_id, valid_code, seed, captcha, price):
        url = 'https://pet-chain.baidu.com/data/txn/sale/create'
        headers = self.headers_template
        headers[
            'Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=market&petId=' + pet_id + '&validCode=' + valid_code + '&appId=1&tpl='
        data = {
            "petId": pet_id,
            "amount": price,
            "seed": seed,
            "captcha": captcha,
            "validCode": valid_code,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('创建单子失败：{0}'.format(response['errorMsg']))

        return response

    def confirm(self, pet_id, order_id, nonce, valid_code):
        url = 'https://pet-chain.baidu.com/data/order/confirm'
        headers = self.headers_template
        headers[
            'Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=market&petId=' + pet_id + '&validCode=' + valid_code + '&appId=1&tpl='
        secret = sha256(password) + '|' + order_id + '|' + nonce
        secret = rsa_encrypt(baidu_pub_key, secret)
        data = {
            "appId": 1,
            'confirmType': 2,
            "s": secret,
            "requestId": int(time.time() * 1000),
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('买入失败: {0}'.format(response['errorMsg']))

        return response

    # 机器学习破解验证码自动购买
    def buy(self, pet):
        pet_id, price, valid_code, generation = pet['petId'], pet["amount"], pet['validCode'], pet['generation']
        count = 1
        while True:
            log('第{0}次尝试购买，狗狗ID：{1}, 代数 {2}, 价格 {3}'.format(count, pet_id, generation, price))
            count += 1

            seed, img = self.get_captcha_and_seed(pet_id, valid_code)
            if not seed:
                time.sleep(3)
                continue

            captcha = self.crack.predict(img)
            response = self.create(pet_id, valid_code, seed, captcha, price)
            if response['errorNo'] == '00':
                order_id = response['data']['orderId']
                nonce = response['data']['nonce']
                response = self.confirm(pet_id, order_id, nonce, valid_code)
                if response['errorNo'] == '00':
                    return response

            # 10002: 有人抢先下单啦
            # 10018：您今日交易次数已超限，明天再试试吧
            errors = ['10002', '10018']
            if response['errorNo'] in errors:
                return response

            time.sleep(3)

    # 购买低于指定价格的天使狗，直到达到当日最大交易次数为止
    def buy_angel_pets_until_max_trade_times(self, price_limit):
        while True:
            try:
                pets = self.get_pets()
                for pet in pets:
                    price = float(pet["amount"])
                    if price > price_limit:
                        continue

                    pet_info = self.get_pet_info(pet['petId'], pet['validCode'])
                    physique = self.get_attribute(pet_info['attributes'], '体型')
                    log("{:\u3000<10} {:>8}".format('体型：' + physique, '价格：' + str(price)))

                    if physique != '天使':
                        continue

                    response = self.buy(pet)
                    # 10018：您今日交易次数已超限，明天再试试吧
                    if response['errorNo'] == '10018':
                        return
            except:
                traceback.print_exc()

    # 购买符合条件的狗狗，直到达到当日最大交易次数为止
    def buy_pets_until_max_trade_times(self, price_limit, rare_degree, max_generation, max_count):
        count = 0
        while True:
            try:
                pets = self.get_pets_with_condition(rare_degree)
                for pet in pets:
                    price = float(pet["amount"])
                    if price > price_limit:
                        continue

                    generation = pet['generation']
                    if generation > max_generation:
                        continue

                    response = self.buy(pet)
                    if response['errorNo'] == '00':
                        count = count + 1
                        log('已购买 {0} 条'.format(count))

                    # 购买已达最大数量限制
                    if count == max_count:
                        return

                    # 10018：您今日交易次数已超限，明天再试试吧
                    if response['errorNo'] == '10018':
                        log('达到最大交易次数时已购买 {0} 条'.format(count))
                        return
                time.sleep(5)
            except:
                traceback.print_exc()


if __name__ == '__main__':
    buy = Buy(cookie)
    # 购买卓越狗 价格不高于200
    # buy.buy_angel_pets_until_max_trade_times(200)
    # 购买卓越狗 价格不高于160， 代数不高于2代，数量不超过10条
    # buy.buy_pets_until_max_trade_times(150, 2, 2, 10)
    # 购买史诗狗 价格不高于2500， 代数不高于3代，数量不超过5条
    buy.buy_pets_until_max_trade_times(2500, 3, 3, 5)
