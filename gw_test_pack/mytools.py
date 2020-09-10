#!/usr/bin/python 
# -*- coding: utf-8 -*-
import os

import rsa
from base64 import b64encode, b64decode
import uuid
import time
import logging


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


def CreateLogger(logFile, fmt='%(asctime)s|%(levelname)s|%(message)s', level=logging.DEBUG):
    import logging.handlers
    # handler = logging.handlers.RotatingFileHandler(str(logFile), maxBytes=1024 * 1024 * 500, backupCount=5)
    handler = logging.handlers.RotatingFileHandler(str(logFile))
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger = logging.getLogger(str(logFile))
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


if __name__ == '__main__':
    sourceCode = "tpjf"
    #  测试公钥加密私钥解密是否可用
    myrsa = MyRSA(f"cases/{sourceCode.upper()}/KEYS/partner_pub_key",
                  f"cases/{sourceCode.upper()}/KEYS/partner_priv_key",
                  f"cases/{sourceCode.upper()}/KEYS/jinke_pub_key",
                  f"cases/{sourceCode.upper()}/KEYS/jinke_priv_key")
    myrsa.jinke_pub_key
    myrsa.jinke_priv_key
    myrsa.partner_pri_key
    myrsa.partner_pub_key
    ori = b'123'
    x = myrsa.encrypt(ori, pub_key=myrsa.jinke_pub_key)
    print("公钥加密结果:", x)
    # x = b64encode(x)
    y = myrsa.decrypt(x, pri_key=myrsa.jinke_priv_key)
    print("私钥解密结果:", y)

    # 测试私钥签名,公钥验签是否可用
    x1 = myrsa.sign(data=x, pri_key=myrsa.jinke_priv_key)
    print("私钥签名结果:", x1)
    y1 = myrsa.verify_sign(data=x, signature=x1, verify_key=myrsa.jinke_pub_key)
    print("公钥验签结果:", y1)
