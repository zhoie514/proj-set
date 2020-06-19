#!/usr/bin/python 
# -*- coding: utf-8 -*-

# cros_log Excel存放位置
EXCEL_TAR_PATH = "./source_data"
# cros_log Excel下载保存位置
EXCEL_SOURCE_PATH = "C:\\Users\\zhoie\\Downloads"

# 产品对应码
PROD_CODE = ["1600000050", "1600000051", "1600000054", "1600000055", "1600000062", "160069010045X01"]
PROD_NAME = ["QH", "XL", "HB", "TPJF", "LX", "SQC"]
# 复制excel后是否把原excel删掉
CLEAR_SOURCE_EXCEL = 0

OFFSET_DAY = -1
# excel 输出路径
EXCEL_OUT = "./excels_out"
# 放款网络错误 err list
REQUEST_FAILED = ["网络错误", "该手机号已注册当前产品", "can not apply credit", "非解耦用户没查询到相应用户信息",
                  "该用户发现从其他助贷方已有注册信息", "call audit_task service timeout", "该微信已经注册当前产品",
                  "逆地理位置查询失败", "call prism service timeout"]

# zip 文件的输出
ZIP_OUT = "./zip_out"

# 对内，对外的发送统计的产品
SELFY_FILES = ["QH", "XL", "HB", "TPJF", "LX", "SQC"]
OUT_FILES = ["HB", "TPJF", "LX"]

MAIL_HOST = "smtp.exmail.qq.com"
MAIL_USER = "publica@xwfintech.com"
MAIL_PWD = "Passw0rd@PA"

# 内部人员邮箱
# EMAIL_SELFY = ["joshuazhao@xwfintech.com", "yang.gui1@pactera.com", "jiangyongjie@xwfintech.com",
#                "jordan@xwfintech.com",
#                "belenbei@xwfintech.com", "291958900@QQ.COM", ]
EMAIL_SELFY = ['291958900@qq.com']
EMAIL_SRCB = ['291958900@qq.com']
# 上农的人员的邮箱 ，不给他们发数据源
# EMAIL_SRCB = ["chenzheng1@srcb.com", "yangcl@srcb.com", "bianzheng@srcb.com"]

# 以下为修正放款成功的数量,及成功率  相关的配置
