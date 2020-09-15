#!/usr/bin/python 
# -*- coding: utf-8 -*-
# 网络相关的配置参数

# with gateway
GW_DOMAIN = "http://union-general-gw.xwfintech.com"
# without gateway
LO_DOMAIN = "http://172.16.1.115:10070?cmdid="
# url-cmdid mapping
URL_MAPPING = {"50008": "/loan-api/v1/file/upload",
               "51060": "/loan-api/ms/loan/apply",
               "51048": "/loan-api/ms/loan/result"}

# collate the request ,standard procedure
ORDERED_REQ = ["51060", "50002"]
