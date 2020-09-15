#!/usr/bin/python 
# -*- coding: utf-8 -*-
import base64
import time

import mytools
import requests
import json
import CONF_NET
import CONST_ARGS
import CONF_ARG
from mytools import MyRSA
import logging

req_logger = mytools.CreateLogger(f'cases/{CONST_ARGS.SOURCE_CODE.upper()}/req_logger.log',
                                  level=CONST_ARGS.LOG_LEVEL)
const_logger = mytools.CreateLogger(f'cases/{CONST_ARGS.SOURCE_CODE.upper()}/const_logger.log',
                                    fmt="%(asctime)s|%(levelname)s|%(message)s", level=logging.INFO)


# 单个cmdid的调用
def single_run(use_gw, sin_cmdid, gw_rsa: MyRSA, **kwargs):
    # 0. 基本变量
    sub_logging = kwargs['logging']
    req_data = {}
    code = 0
    #  1. 组织入参
    if use_gw:
        url = CONF_NET.GW_DOMAIN + CONF_NET.URL_MAPPING.get(sin_cmdid)
        data = json.dumps(CONF_ARG.GW_PARAM.get(sin_cmdid, {}))
        en_data = gw_rsa.encrypt(data.encode())
        sign = gw_rsa.sign(en_data)
        req_data['appId'] = CONST_ARGS.APPID
        req_data['data'] = en_data.decode()
        req_data["sign"] = sign.decode()

        print("发送明文: ", json.dumps(CONF_ARG.GW_PARAM.get(sin_cmdid)))
        print("发送后密文: ", req_data)
        sub_logging.debug(f"{CONF_NET.URL_MAPPING[sin_cmdid]}|gateway|encrypt|reqData|{json.dumps(req_data)}")
        sub_logging.info(f"{sin_cmdid}|gateway|decrypt|reqData|{CONF_ARG.GW_PARAM.get(sin_cmdid)}")
        req_logger.info(f"{sin_cmdid}|reqData|{CONF_ARG.GW_PARAM.get(sin_cmdid)}")

        requset_info = CONF_ARG.GW_PARAM.get(sin_cmdid, {})
        # #修改2#
        serialNo = requset_info.get("pbocQueryNo") or requset_info.get('loanReqNo') or requset_info.get(
            'creditNo') or requset_info.get('registerNo') or requset_info.get('reqNo')
        phone = requset_info.get('mobileNo') or requset_info.get('phone') or requset_info.get('mobile')
        name = requset_info.get('custName') or requset_info.get('name')
        id = requset_info.get('idNo') or requset_info.get('id')
        card = requset_info.get('dbAcct')
        if name or card:
            const_logger.info(f"{sin_cmdid}|serialNo: {serialNo}|name: {name}|phone: {phone}|id: {id}|card: {card}")
    else:
        url = CONF_NET.LO_DOMAIN + sin_cmdid
        data = CONF_ARG.LO_PARAM.get(sin_cmdid, {})
        req_data = data
        print("发送前明文: ", req_data)
        sub_logging.info(f"{sin_cmdid}|gateway|orign|reqData|{data}")
        req_logger.info(f"{sin_cmdid}|reqData|{data}")

    # 2. 发送请求
    try:
        headers = {'content-type': "application/json"}
        res = requests.post(url, data=json.dumps(req_data), timeout=60, headers=headers)
        sub_logging.info(f"{sin_cmdid}|{url.split('/')[-1]}|Send Request Success...")
    except Exception as e:
        print("连接超时")
        sub_logging.error(f"{sin_cmdid}|{url.split('/')[-1]}|Send Request Failed")
        req_logger.error(f"{sin_cmdid}|{url.split('/')[-1]}|Send Request Failed")
        code = 1
        msg = "请求发送失败"
        return code, msg

    # 3. 处理返回值
    if use_gw:  # 经过网关的话,需要解密
        res_obj = json.loads(res.text)
        if not isinstance(res_obj, dict):  # 返回值非json
            sub_logging.info(f"{sin_cmdid}|gateway|orign|resData|{res_obj}")
            req_logger.info(f"{sin_cmdid}|resData|{res_obj}")
            print("返回的错误信息: ", res_obj)
            code = 10001
            msg = res_obj
            return code, msg
        encrypt_data = res_obj.get('data')
        sign = res_obj.get('sign')
        decrypt_data = gw_rsa.decrypt(encrypt_data)
        sign_flag = gw_rsa.verify_sign(encrypt_data.encode(), sign.encode())
        print("返回密文: ", res_obj)
        print("返回明文: ", decrypt_data.decode())
        sub_logging.debug(f"{sin_cmdid}|gateway|encrypt|resData|{res_obj}")
        sub_logging.info(f"{sin_cmdid}|gateway|decrypt|resData|{decrypt_data.decode()}")
        req_logger.info(f"{sin_cmdid}|resData|{decrypt_data.decode()}")
        assert sign_flag  # 断言验签是否成功, 先解密返回值再说,所以放到最后
        msg = json.loads(decrypt_data.decode())
        return code, msg
    else:  # 不经过网关的话不用解密
        res_obj = json.loads(res.text)
        sub_logging.info(f"{sin_cmdid}|gateway|orign|resData|{res_obj}")
        req_logger.info(f"{sin_cmdid}|resData|{res_obj}")
        print("返回明文: ", res_obj)
        if not isinstance(res_obj, dict):  # 返回值非json
            code = 10002
        msg = res_obj
        return code, msg


# 系列的cmdid调用
def sub_main_run(use_gw, gw_rsa, **kwargs):
    out_code = 0
    out_msg = ""
    sub_logging = kwargs['logging']
    if not CONF_NET.ORDERED_REQ:
        return 10003, "没有序列cmdid"
    if not isinstance(CONF_NET.ORDERED_REQ, (list, tuple)):
        return 10004, "ORDERED_REQ 类型错误"
    # 按相应顺序依次访问cmd id
    cycle_flag = True  # 是否正确调用并返回业务正常的标志
    for cmdid in CONF_NET.ORDERED_REQ:
        while cycle_flag:
            # 如果上一次调用正常则,进行下一次的调用
            code, msg = single_run(use_gw=use_gw, gw_rsa=gw_rsa, sin_cmdid=cmdid, logging=sub_logging)
            Business_code = msg.get("status") or msg.get("loanResult")
            if code != 0:
                cycle_flag = False
                out_msg = msg
                return code, msg
            else:
                # #修改# 下面判断条件要自己写,上一个流程反回什么代表成功
                if Business_code == "00":
                    # 业务成功
                    cycle_flag = True
                    time.sleep(20)
                    break
                elif Business_code in ("01", "99"):
                    # 处理中 重试
                    cycle_flag = True
                    time.sleep(60)
                else:
                    # 失败 报错
                    cycle_flag = False
                    return Business_code, msg.get("msg", f"{cmdid} 反回结果失败")
        else:
            return out_code, out_msg
    return 0, "success"
