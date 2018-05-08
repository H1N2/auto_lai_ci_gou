# coding = utf-8

# pycrypto 已经废弃，使用 pycryptodome 代替： https://www.pycryptodome.org

import base64
import hashlib
from Crypto.PublicKey import RSA as rsa
from Crypto.Cipher import PKCS1_v1_5 as cipher_PKCS1_v1_5

from cfg import BAIDU_PUBLIC_KEY

from ml.captcha_crack_baidu.logger import log


def sha256(d):
    hash = hashlib.sha256()
    hash.update(d.encode('utf-8'))
    return hash.hexdigest()


def rsa_encrypt(pub_key, msg):
    rsa_key = rsa.importKey(pub_key)
    cipher = cipher_PKCS1_v1_5.new(rsa_key)
    msg = msg.encode('utf8')
    cipher_text = base64.b64encode(cipher.encrypt(msg)).decode()
    return cipher_text


def rsa_decrypt(pub_key, msg):
    rsa_key = rsa.importKey(pub_key_str)
    cipher = cipher_PKCS1_v1_5.new(rsa_key)
    msg = msg.encode('utf8')
    cipher_text = base64.b64encode(cipher.encrypt(msg)).decode()
    return cipher_text


if __name__ == '__main__':
    password = '000000'

    log(sha256(password))
    # print("91b4d142823f7d20c5f08df69122de43f35f057a988d9619f6d3138485c9a203")

    # pub_key_str = """-----BEGIN RSA PUBLIC KEY-----
    # MIIBCgKCAQEAuw4T755fepEyXTM66pzf6nv8NtnukQTMGnhmBFIFHp/P2vEpxjXU
    # BBDUpzKkVFR3wuK9O1FNmRDAGNGYC0N/9cZNdhykA1NixJfKQzncN31VJTmNqJNZ
    # W0x7H9ZGoh2aE0zCCZpRlC1Rf5rL0SVlBoQkn/n9LnYFwyLLIK5/d/y/NZVL6Z6L
    # cyvga0zRajamLIjY0Dy/8YIwVV6kaSsHeRv2cOB03eam6gbhLGIz/l8wuJhIn1rO
    # yJLQ36IOJymbbNmcC7+2hEQJP40qLvH7hZ1LaAkgQUHjfi8RvH2T1Jmce7XGPxCo
    # Ed0yfeFz+pL1KeSWNey6cL3N5hJZE8EntQIDAQAB
    # -----END RSA PUBLIC KEY-----"""

    # 参考https://segmentfault.com/q/1010000004495221
    pub_key_str = """-----BEGIN RSA PUBLIC KEY-----
    """ + BAIDU_PUBLIC_KEY + """
    -----END RSA PUBLIC KEY-----"""

    message = "91b4d142823f7d20c5f08df69122de43f35f057a988d9619f6d3138485c9a203|2098831667234045845|1119866306807917546"
    cipher_text = rsa_encrypt(pub_key_str, message)
    log(cipher_text)
