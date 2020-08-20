#!/usr/bin/python 
# -*- coding: utf-8 -*-
import os

import rsa
from base64 import b64encode, b64decode
import uuid
import time

import CONST_ARGS


def gen_uuid() -> str:
    # 生成uuid流水号
    return str(uuid.uuid1())


def gen_normal_serial(prod: str = "prod") -> str:
    #     生成普通时间戳的流水号,可能 重复
    return prod + "_" + str(int(time.time() * 1000))


class rsaError(BaseException):
    pass


class MyRSA:
    """
    customize rsa tool
    """

    def __init__(self, partner_pub_key=None, partner_pri_key=None, jinke_pub_key=None, jinke_priv_key=None):
        # check each key is valid or not
        self.key_size = 2048
        if self.key_size % 8 != 0:
            raise rsaError('invalid length of key')
        try:
            with open(partner_pub_key, 'rb') as f:
                tmp = f.read()
                self.partner_pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(tmp)
        except Exception as e:
            print(e)
            # if key is invalid ,redirect origin func to errorFunc
            self.encrypt = self._pub_key_error
        try:
            with open(partner_pri_key, 'rb') as f:
                tmp = f.read()
                self.partner_pri_key = rsa.PrivateKey.load_pkcs1(tmp)
        except Exception as e:
            print(e)
            self.decrypt = self._pri_key_error
            self.sign = self._pri_key_error

        try:
            with open(jinke_pub_key, 'rb') as f:
                tmp = f.read()
                self.jinke_pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(tmp)
        except Exception as e:
            print(e)
            self.verify_sign = self._verify_key_error
        try:
            with open(jinke_priv_key, 'rb') as f:
                tmp = f.read()
                self.jinke_priv_key = rsa.PrivateKey.load_pkcs1(tmp)
        except Exception as e:
            print(e)
            self.decrypt = self._pri_key_error("金科私钥错误")

    def encrypt(self, data: bytes, pub_key=None) -> bytes:
        pub_key = pub_key or self.jinke_pub_key
        res = b''
        try:
            for data in self._encrypt_block_data(data):
                res += rsa.encrypt(data, pub_key)
            res = b64encode(res)
        except Exception as e:
            print(e)
        return res

    def decrypt(self, data: bytes, pri_key=None) -> bytes:
        pri_key = pri_key or self.partner_pri_key
        res = b''
        data = b64decode(data)
        try:
            for data in self._decrypt_block_data(data):
                res += rsa.decrypt(data, pri_key)
        except Exception as e:
            print(e)
        return res

    def sign(self, data: bytes, pri_key=None, hash_method='SHA-256') -> bytes:
        """Signs the message with the private key.
            :param data: data with MyRSA.encrypt
            :param pri_key: the :py:class:`rsa.PrivateKey` to sign with
            :param hash_method: 'MD5', 'SHA-1','SHA-224', SHA-256', 'SHA-384' or 'SHA-512'.
            :return: a message signature block.
        """
        pri_key = pri_key or self.partner_pri_key
        signature = rsa.sign(data, pri_key, hash_method)
        signature = b64encode(signature)
        return signature

    def verify_sign(self, data: bytes, signature: bytes, verify_key=None) -> bool:
        """
        verify sign which is send by client
        :param data:data字段
        :param signature: sign created with MyRSA.sign
        :param verify_key: client public key
        :return: bool
        """
        verify_key = verify_key or self.jinke_pub_key
        signature = b64decode(signature)

        try:
            rsa.verify(data, signature, verify_key)
            res = True  # 'verify succeed'
        except Exception as e:
            res = False  # 'verify failed'
        return res

    def _encrypt_block_data(self, data):
        #  encrypt data that longer than key's size
        reserve_size = 11
        block_size = int(self.key_size / 8) - reserve_size
        for i in range(0, len(data), block_size):
            yield data[i:i + block_size]

    def _decrypt_block_data(self, data):
        #  decrypt data wont be influence by reserve size,it depends on only key size
        block_size = int(self.key_size / 8)
        for i in range(0, len(data), block_size):
            yield data[i:i + block_size]

    def _pub_key_error(self, *args):
        raise rsaError('pub_key is invalid,can not do encrypt')

    def _pri_key_error(self, *args):
        raise rsaError('pri_key is invalid,can not do decrypt or signature')

    def _verify_key_error(self, *args):
        raise rsaError('public key is invalid,can not check its sign')


def gen_key_pairs():
    """
    生成的是pkcs1类型的  load_pkcs1_openssl_pem 解不开,这个需要pkcs8类型的
    :return:  0 : keys generate succeed
    """
    #  create keys directory
    try:
        os.mkdir(os.path.join(os.path.dirname(__file__), 'KEYS'))
    except OSError as e:
        # print(e)
        pass
    # generate the pair of keys
    pubkey, privkey = rsa.newkeys(2048)
    pub_key = pubkey.save_pkcs1(format="PEM")
    pri_key = privkey.save_pkcs1(format="PEM")
    with open(os.path.join(os.path.curdir, 'keys', 'pub_key.pem'), 'w+', encoding='utf-8') as f:
        f.write(pub_key.decode())
    with open(os.path.join(os.path.curdir, 'keys', 'priv_key.pem'), 'w+', encoding='utf-8') as f:
        f.write(pri_key.decode())
    return 0


def CreateLogger(logFile):
    import logging.handlers
    # handler = logging.handlers.RotatingFileHandler(str(logFile), maxBytes=1024 * 1024 * 500, backupCount=5)
    handler = logging.handlers.RotatingFileHandler(str(logFile))
    fmt = '%(asctime)s|%(levelname)s|%(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger = logging.getLogger(str(logFile))
    logger.addHandler(handler)
    logger.setLevel(CONST_ARGS.LOG_LEVEL)
    return logger


if __name__ == '__main__':
    sourceCode = "tpjf"
    #  测试公钥加密私钥解密是否可用
    myrsa = MyRSA(f"cases/{sourceCode.upper()}/KEYS/partner_pub_key",
                  f"cases/{sourceCode.upper()}/KEYS/partner_priv_key",
                  f"cases/{sourceCode.upper()}/KEYS/jinke_pub_key",
                  f"cases/{sourceCode.upper()}/KEYS/jinke_priv_key")
    ori = b'123'
    x = myrsa.encrypt(ori)
    print("公钥加密结果:", x)
    # x = b64encode(x)
    y = myrsa.decrypt(x)
    print("私钥解密结果:", y)

    # 测试私钥签名,公钥验签是否可用
    x1 = myrsa.sign(x)
    print("私钥签名结果:", x1)
    y1 = myrsa.verify_sign(x, x1)
    print("公钥验签结果:", y1)
    # print((str(uuid.uuid1())))
    d = b"OSIRs53bqNvRo3ea20I2J1ua/vPu24MESQ4AQZsOoKNg+Lpw63nBgAO2dY4EGsytG33yXBOhRc8yxfXiRw/duHxQUTsT7uCanI2pzjxc9pk9ExcxEh6gqriscOZKPz9Ja0Dnn25RR5FXypfi7UvlYMCDbtu+7zGa5cDth7s0tJ+rqiAj4mCmZHs/g6ZaL22FQu2Vtc4/CGX3oARqyZb2EUXTPbZBlz1+yKX5r8iEtfHhP6gUst/EK7uzuwmc28oWIfG6QRhpMuGmQIKXtYPs7ffFOvbJx40Lz0AjRVXw7YXTR2ijbec4BQyC0PsDc/+RdQbTkpe3YjEZ4aMpVAaVDg=="
    s = "fDkivKaqQT5bnguYb9nlOD75pXpVKashVptsZNGEtoVs01qxgnjAyi3KYvB2kTs9JoJz64xoCsKSC7CdSmjlK5HnfAPPv7npV5VKGap8vNhj2JycUEA1C3vEELLJ2/EFJ0JVJgsVROVqFx9HVv2aj4MgOLelrFZG4b1bbWH4xrZPnFFpYvzuLE1dwjbrTQhz/0sTz8+36LyFRHdxpw1skTZI3AYbwH4xu/su/nBUEEK09d+4pXYK/wlyPObHVo54FZLixMidnCU5hJYjIiwEHvkGtViJEOK9rqdVYLhUDthKW6xMSk2ToMioKZmyij3phloJUklMo+bgw20+toMELw=="
    s = s.encode()
    print(s)
    y2 = myrsa.verify_sign(d, s)
    print("xxx:", y2)
