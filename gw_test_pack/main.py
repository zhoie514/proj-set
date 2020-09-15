#!/usr/bin/python 
# -*- coding: utf-8 -*-
# 有变化的实例可以copy并进行修改
import sys
from mytools import CreateLogger

if len(sys.argv) == 1:
    print("说明:",
          "第1个参数 - sourceCode | 不区分大小写| 必须",
          "第2个参数 - 是否启用网关| 0:否; 1:是| 必须",
          "第3个参数 - 调用单个cmdid接口 | eg: 50001 | 非必须",
          "eg: python xxx.py tpjf 0 50001\r\n python xxx.py tpjf 1 50002",
          # "第4个参数 - 是否依赖上一次调用的返回值 | eg: 50001| 单接口使用|配合前者使用",
          sep="\n")
    sys.exit(99)

PROD = sys.argv[1].upper()
if len(sys.argv) > 2:
    USE_GW = bool(int(sys.argv[2]))
else:
    USE_GW = False
try:
    SIN_CMDID = sys.argv[3]
except IndexError:
    SIN_CMDID = ""

# 将产品编号临时添加进环境变量
sys.path.append(f"./cases/{PROD}")
import sub_main
import CONST_ARGS

main_logging = CreateLogger(f'cases/{PROD}/main_logging.log', level=CONST_ARGS.LOG_LEVEL)
# 是否通过网关 决定是否需要rsa加解密
myrsa = None

if USE_GW:
    from mytools import MyRSA, CreateLogger

    try:
        myrsa = MyRSA(partner_pub_key=f"./cases/{PROD}/KEYS/partner_pub_key",
                      partner_pri_key=f"./cases/{PROD}/KEYS/partner_priv_key",
                      jinke_pub_key=f"./cases/{PROD}/KEYS/jinke_pub_key",
                      jinke_priv_key=f"./cases/{PROD}/KEYS/jinke_priv_key")
    except Exception as e:
        main_logging.info(f"log|rsa key load Error:{e}")
    main_logging.info(f"log|rsa key load Success")


def run(use_gw, sin_cmdid, rsa=myrsa, **kwargs):
    if SIN_CMDID != "":
        # 单步运行
        code, msg = sub_main.single_run(use_gw, sin_cmdid, rsa, **kwargs)
    else:
        # 按设定的cmd流程依次运行
        code, msg = sub_main.sub_main_run(use_gw, rsa, **kwargs)
    return code, msg


code, msg = run(USE_GW, SIN_CMDID, myrsa, logging=main_logging)
print("Process Result:", code, msg)
