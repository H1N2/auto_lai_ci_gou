# coding = utf-8

import requests
import json
import base64
import time
import os
import traceback

from logger import log
from cfg import COOKIE as cookie
# from ml.captcha_crack_baidu.captcha_crack import Crack
from ml.captcha_recognize.captcha_recognize_new import Crack


class Gather:
    def __init__(self, cookie):
        self.cookie = cookie

        self.correct_amount_file = 'correct_amount.txt'

        self.fail_amount_file = 'fail_amount.txt'

        self.correct_captcha_folder = './data/recognized_captcha/correct/'

        self.fail_captcha_folder = './data/recognized_captcha/fail/'

        self.total = 0

        self.correct = 0

        self.fail = 0

        self.crack = Crack()

        if os.path.exists(self.correct_amount_file):
            file = open(self.correct_amount_file, 'r')
            amount = file.read()
            log('当前验证码数量：{}'.format(amount))
            file.close()

            self.correct_captcha_amount = int(amount)
        else:
            self.correct_captcha_amount = 0

        if os.path.exists(self.fail_amount_file):
            file = open(self.fail_amount_file, 'r')
            amount = file.read()
            log('当前验证码数量：{}'.format(amount))
            file.close()

            self.fail_captcha_amount = int(amount)
        else:
            self.fail_captcha_amount = 0

        if not os.path.exists(self.correct_captcha_folder):
            os.makedirs(self.correct_captcha_folder)
            log('创建文件夹：' + self.correct_captcha_folder)

        if not os.path.exists(self.fail_captcha_folder):
            os.makedirs(self.fail_captcha_folder)
            log('创建文件夹：' + self.fail_captcha_folder)

        self.headers_template = {
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6',
            'Content-Type': 'application/json',
            'Cookie': self.cookie,
            'Host': 'pet-chain.baidu.com',
            'Origin': 'https://pet-chain.baidu.com',
            'Referer': 'https://pet-chain.baidu.com/chain/dogMarket?appId=1&tpl=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }

    def get_captcha(self, pet_id):
        url = 'https://pet-chain.baidu.com/data/captcha/gen'
        headers = self.headers_template
        headers['Referer'] = 'https://pet-chain.baidu.com/chain/detail?channel=market&petId=' + pet_id + '&validCode='
        data = {
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)

        return response['data']['seed'], response['data']['img']

    def check_captcha(self, pet_id, amount, seed, captcha):
        """
        验证验证码识别是否正确
        :param pet_id: 狗狗ID
        :param amount: 狗狗价格
        :param seed: 狗狗验证码种子
        :param captcha: 验证码
        :return: 结果元组
                 第一个元素：此次验证是否有效
                 第二个元素：验证码是否正确
                 第三个元素：附加信息
        """
        url = 'https://pet-chain.baidu.com/data/txn/create'
        headers = self.headers_template
        data = {
            "petId": pet_id,
            "amount": amount,
            "seed": seed,
            "captcha": captcha,
            "validCode": "",
            "requestId": int(time.time() * 1000),
            "appId": 1,
            "tpl": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.content)

        # 验证码正确：errorMsg: '有人抢先下单啦'
        if response['errorNo'] == '10002':
            return True, True, None

        # 验证码正确：errorMsg: '您今日交易次数已超限，明天再试试吧'
        if response['errorNo'] == '10018':
            return True, True, None

        # 验证码错误: errorMsg: '验证码错误'
        if response['errorNo'] == '100':
            return True, False, None

        # 其它异常，如：网络繁忙等
        return False, None, response['errorMsg']

    def save_correct_captcha_amount(self):
        file = open(self.correct_amount_file, 'w')
        file.write(str(self.correct_captcha_amount))
        file.flush()
        file.close()

    def save_correct_captcha(self, predict_text, base64_img_str):
        self.correct_captcha_amount = self.correct_captcha_amount + 1
        file_name = str(self.correct_captcha_amount) + '_' + predict_text + '.jpg'
        file = open(self.correct_captcha_folder + file_name, 'wb')
        img = base64.b64decode(base64_img_str)
        file.write(img)

        file.close()
        log('保存正确验证码：' + file_name)

    def save_fail_captcha_amount(self):
        file = open(self.fail_amount_file, 'w')
        file.write(str(self.fail_captcha_amount))
        file.flush()
        file.close()

    def save_fail_captcha(self, predict_text, base64_img_str):
        self.fail_captcha_amount = self.fail_captcha_amount + 1
        file_name = str(self.fail_captcha_amount) + '_' + predict_text + '.jpg'
        file = open(self.fail_captcha_folder + file_name, 'wb')
        img = base64.b64decode(base64_img_str)
        file.write(img)

        file.close()
        log('保存错误验证码：' + file_name)

    def gather_captcha(self, pet_id, amount):
        seed, img = self.get_captcha(pet_id)
        captcha = self.crack.predict(img)

        log('输入预测验证码:' + captcha)
        valid, correct, err = self.check_captcha(pet_id, amount, seed, captcha)
        if not valid:
            log(err)
            return

        self.total += 1
        if correct:
            self.save_correct_captcha(captcha, img)
            self.save_correct_captcha_amount()
            self.correct += 1
        else:
            self.save_fail_captcha(captcha, img)
            self.save_fail_captcha_amount()
            self.fail += 1

        log('总数 ' + str(self.total) + " 正确 " + str(self.correct) + ' 准确率：' + str(self.correct / self.total))

    def gather_captchas(self, pet_id, amount, times=99999999999):
        for i in range(times):
            try:
                self.gather_captcha(pet_id, amount)
            except:
                traceback.print_exc()

            time.sleep(5)


if __name__ == '__main__':
    mark = Gather(cookie)
    mark.gather_captchas('2006556012862778442', 999999999.99)
