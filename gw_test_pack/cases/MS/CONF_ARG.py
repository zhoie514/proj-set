#!/usr/bin/python 
# -*- coding: utf-8 -*-
import time

import faker
import CONST_ARGS
from mytools import gen_normal_serial


# 各种接口的参数信息
# 使用网关的参数
class Custom:
    def __init__(self):
        __fake = faker.Faker("zh_CN")
        self.idNo = "" or __fake.ssn()
        self.custName = "" or __fake.name()
        self.mobilNo = "" or __fake.phone_number()
        self.address_all = "" or __fake.address()
        self.address = "" or self.address_all.split(" ")[0]
        self.addCode = "" or self.address_all.split(" ")[1]
        # 准入年龄限制
        while not 1998 > int(self.idNo[6:10]) > 1970:
            self.idNo = __fake.ssn()
        self.birthDay = "" or self.idNo[6:10] + "-" + self.idNo[10:12] + "-" + self.idNo[12:14]
        self.companyName = "" or __fake.company()


# 通用参数
appId = CONST_ARGS.APPID
sourceCode = CONST_ARGS.SOURCE_CODE
pbocNo = "" or gen_normal_serial(sourceCode)
loanDate = "2020-01-01 12:30:00"  # 核心时间
cust = Custom()
contact = Custom()
# 通过网关的请求参数
_gw_reqData_50001 = {"appId": appId, "sourceCode": sourceCode, "birthday": cust.birthDay,
                     "applyTime": "2020-09-10 12:12:12", "companyName": cust.companyName,
                     "contactCell": contact.mobilNo, "contactName": contact.custName, "contactRel": "3",
                     "custName": cust.custName,
                     "deviceInfo": "{\"deviceId\":\"123-id\",\"model\":\"iPhone XS\",\"osType\":\"IOS12.3\"}",
                     "faceCompareScore": "99", "gender": "男", "idAddress": cust.address, "idNo": cust.idNo,
                     "idType": "1", "industry": "F", "issuedBy": "时间管理局", "latitude": 31.2881, "longitude": 121.59673,
                     "mobileNo": cust.mobilNo, "pbocQueryNo": pbocNo, "queryReason": "01", "race": "汉",
                     "resAddress": cust.address, "validFrom": "20200901", "validTo": "20301212",
                     "materials": "{\"card_back\":\"eyJmaWxlbmFtZSI6IjVlNDYxMDc2ODIwMjNmMDAwY2EyMTc4MCIsInNpZ24iOiI1ZGM0YmFiYWQ4MzVjNjIzNWUxYWI4MzBjYWU3MzcyNyIsInRpbWUiOjE1ODE2NTAwMzh9\",\"card_front\":\"eyJmaWxlbmFtZSI6IjVlNDYxMDc3ODIwMjNmMDAwY2EyMTc4MSIsInNpZ24iOiJhNTg1YWRjMjczMTQzNzI3NDQ1Njg2NTYyYmJhMTAzYiIsInRpbWUiOjE1ODE2NTAwMzl9\",\"photo\":\"eyJmaWxlbmFtZSI6IjVlNDYxMDc4ODIwMjNmMDAwY2EyMTc4MiIsInNpZ24iOiJkMDJlNDg2YWVjNDZmZjVmNWY2ODJlMmViNDRjY2JiNyIsInRpbWUiOjE1ODE2NTAwNDF9\"}"
                     }
_gw_reqData_50002 = {"appId": appId, "pbocQueryNo": pbocNo, "sourceCode": sourceCode}
_gw_reqData_50003 = {"appId": appId, "pbocQueryNo": pbocNo, "sourceCode": sourceCode, "creditStatus": "00",
                     "creditAmt": 50000, "creditRate": 0.072}
_gw_reqData_50004 = {"appId": appId, "pbocQueryNo": pbocNo, "sourceCode": sourceCode}
# time.sleep(1)
loanReq = "" or gen_normal_serial(sourceCode + "_loan")
_gw_reqData_50005 = {"loanReqNo": loanReq, "sourceCode": sourceCode, "appId": appId, "custName": cust.custName,
                     "idType": "1", "id": cust.idNo, "sex": "F", "dbAcct": "622021001012157571",
                     "dbAcctName": cust.custName, "loanDate": loanDate, "loanAmt": 1000, "inTerm": 6, "reundMode": "3",
                     "prodId": "PROD0000004500004", "latitude": 31.2881, "longitude": 121.59673, "refundDay": 25,
                     "policyId": "test-policy", "mobileNo": cust.mobilNo,
                     "deviceInfo": "{\"deviceId\":\"123-id\",\"model\":\"iPhone XS\",\"osType\":\"IOS12.3\"}"}
_gw_reqData_50006 = {"loanReqNo": loanReq, "sourceCode": sourceCode, "appId": appId}

# 通过网关时使用的参数
GW_PARAM = {
    "51060": _gw_reqData_50001,
}

# 不通过网关的请求
_reqData_50001 = {"appId": appId, "sourceCode": sourceCode}
_reqData_50002 = {"appId": appId, "pbocqueryNo": "123", "sourceCode": sourceCode}
_reqData_50003 = {}
_reqData_50004 = {}
_reqData_50005 = {}
_reqData_50006 = {}

# 不通过网关要使用的参数
LO_PARAM = {"50001": _reqData_50001,
            "50002": _reqData_50002,
            "50003": _reqData_50003,
            "50004": _reqData_50004,
            "50005": _reqData_50005,
            "50006": _reqData_50006,
            }

if __name__ == '__main__':
    c = Custom()
    print(c.idNo)
    print(c.birthDay)
    print(c.companyName)
    print(cust.custName, contact.custName)
    print(cust.address)
    print(pbocNo)
    print(loanReq)
