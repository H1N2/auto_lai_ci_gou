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


class Breed:
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

    # 获取繁殖母亲列表
    def get_mother_pets(self):
        url = 'https://pet-chain.baidu.com/data/breed/petList'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/chooseMyDog?appId=1&tpl='
        data = {
            "pageNo": 1,
            "pageSize": 10,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)

        return response['data']['dataList']

    # 获取母亲狗狗，如无可选，则等待5秒后继续查询，直到找到可用为止
    def select_mother(self):
        while True:
            mothers = self.get_mother_pets()
            # 选第一个狗狗作为母亲狗狗
            if len(mothers) > 0:
                return mothers[0]

            interval = 5
            log('无可用母亲狗狗, {0}秒钟后再次查询'.format(interval))
            time.sleep(interval)

    # 获取验证码和种子
    def get_captcha_and_seed(self):
        url = 'https://pet-chain.baidu.com/data/captcha/gen'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/chooseMyDog?appId=1&tpl='
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

    # 繁殖请求
    def create(self, father_pet_id, mother_pet_id, amount, captcha, seed):
        url = 'https://pet-chain.baidu.com/data/txn/breed/create'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/chooseMyDog?appId=1&tpl='
        data = {
            "petId": father_pet_id,
            "senderPetId": mother_pet_id,
            "amount": amount,
            "captcha": captcha,
            "seed": seed,
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('下单失败: {0}'.format(response['errorMsg']))

        return response

    def confirm(self, order_id, nonce):
        url = 'https://pet-chain.baidu.com/data/order/confirm'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/chooseMyDog?appId=1&tpl='
        secret = sha256(password) + '|' + order_id + '|' + nonce
        secret = rsa_encrypt(baidu_pub_key, secret)
        data = {
            "appId": 1,
            'confirmType': 4,
            "s": secret,
            "requestId": int(time.time() * 1000),
            "tpl": "",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)
        if response['errorNo'] != '00':
            log('繁育失败: {0}'.format(response['errorMsg']))

        return response

    # 机器学习破解验证码自动繁育
    def breed(self, father, mother):
        father_id = father['petId']
        mother_id = mother['petId']
        price = father['amount']

        count = 1
        while True:
            log('第{0}次尝试繁殖，父亲狗狗ID：{1}, 母亲狗狗ID: {2}，价格 {3}'.format(count, father_id, mother_id, price))
            count += 1

            seed, img = self.get_captcha_and_seed()
            if not seed:
                time.sleep(3)
                continue

            captcha = self.crack.predict(img)
            response = self.create(father_id, mother_id, price, captcha, seed)

            if response['errorNo'] == '00':
                order_id = response['data']['orderId']
                nonce = response['data']['nonce']
                response = self.confirm(order_id, nonce)
                if response['errorNo'] == '00':
                    return response

            # 10002: 有人抢先下单啦
            # 10018：您今日交易次数已超限，明天再试试吧
            #      : 狗狗已经下架啦
            # TODO 添加错误码到列表
            errors = ['10002', '10018']
            if response['errorNo'] in errors:
                return response

            time.sleep(1)

    # 狗狗内部繁殖，直到达到当日最大交易次数为止
    def breed_until_max_trade_times(self, rare_degree=0):
        while True:
            try:
                page_size = 10
                total_count = self.get_pets_count(page_size)
                page_total = total_count // page_size if total_count % page_size == 0 else (
                    total_count // page_size + 1)
                for i in range(page_total):
                    fathers = self.get_pets(i + 1, page_size, page_total, total_count)
                    for father in fathers:
                        if father['shelfStatus'] != 2 or father['rareDegree'] != rare_degree:
                            continue

                        mother = self.select_mother()
                        response = self.breed(father, mother)

                        # 10018：您今日交易次数已超限，明天再试试吧
                        if response['errorNo'] == '10018':
                            return
                        time.sleep(5)
                    time.sleep(5)
            except:
                traceback.print_exc()


if __name__ == '__main__':
    breed = Breed(cookie)
    breed.breed_until_max_trade_times(2)
