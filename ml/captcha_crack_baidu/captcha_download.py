# coding = utf-8

import requests
import json
import base64
import time
import os
import traceback

from logger import log
from cfg import COOKIE as cookie


class Download:
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

        self.amount_file = 'original_captcha_amount.txt'

        if os.path.exists(self.amount_file):
            file = open(self.amount_file, 'r')
            amount = file.read()
            log('当前验证码数量：{}'.format(amount))
            file.close()

            self.captcha_id = int(amount)
        else:
            self.captcha_id = 0

        self.captcha_dir = './data/original_captcha/'

        if not os.path.exists(self.captcha_dir):
            os.makedirs(self.captcha_dir)
            log('创建文件夹：' + self.captcha_dir)

    def get(self, pet_id):
        """
        获取验证码
        :param pet_id: 狗狗ID
        :return: base64格式的验证码图片
        """
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
        log(response)
        return response['data']['img']

    def save(self, base64_img_str):
        """
        保存验证码
        :param base64_img_str: base64格式的验证码图片
        :return:
        """
        self.captcha_id = self.captcha_id + 1
        file_name = str(self.captcha_id) + '.jpg'
        file = open(self.captcha_dir + file_name, 'wb')
        img = base64.b64decode(base64_img_str)
        file.write(img)
        file.close()
        log('保存验证码：' + file_name)

    def download_captchas(self, amount):
        """
        批量下载验证码
        :param amount: 要下载的数量
        :return:
        """
        for i in range(0, amount):
            try:
                img_str = self.get('1967611895120556792')
                self.save(img_str)

                file = open(self.amount_file, 'w')
                file.write(str(self.captcha_id))
                file.flush()
                file.close()
            except:
                traceback.print_exc()

            time.sleep(3)


if __name__ == '__main__':
    download = Download(cookie)
    download.download_captchas(1)
