import csv
import logging
import sys
from collections import defaultdict
from typing import List

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', level=logging.DEBUG, filename='log.txt')

"""一些错误静态变量"""
# csv 中的 log_type 类别
LOG_TYPE = ("credit", "realnameauth", "withdraw")


class WorkBookError(Exception):
    def __init__(self, msg):
        ...


# excel类
class MyWorkBook:
    def __init__(self, filename: str):
        self.workbook_name = filename
        self.workbook = load_workbook(filename)
        self.sheets_names = self.workbook.get_sheet_names

    def get_sheet_by_index(self, index: int) -> Worksheet:
        """根据索引获得工作表"""
        if index >= len(self.sheets_names()) or index < 0:
            logging.error("无法根据索引获得工作表.")
            raise WorkBookError("out of index")
        return self.workbook.get_sheet_by_name(self.sheets_names()[index])

    def save(self, filename=None):
        """保存文件"""
        if not filename:
            self.workbook.save(self.workbook_name)
            return
        self.workbook.save(filename)
        return


# csv封装
class CsvParser:
    def __init__(self, filename):
        self.csv_name = filename
        self.csv_content = list()

    def get_csv_content(self) -> [[], ]:
        with open(self.csv_name, "r", encoding="utf-8") as f:
            contents = csv.reader(f)
            for content in contents:
                self.csv_content.append(content)
        return self.csv_content

    def get_csv_head(self):
        """返回csv的头【第一行】"""
        return self.csv_content[0]


def csv_handler(my_csv: List) -> dict:
    """解析每一行的数据,返回一个字典{"credit": {"决策拒绝": 10, "反欺诈拒绝": 15, "成功": 100},"withdraw":{},...}"""
    #   解析旧日志数据要模块 不忍删掉
    # 初始化盛放结果的一个字典
    # res = {k:{},...}
    res = defaultdict(dict)
    index = 0
    for row in my_csv:
        index += 1
        # 二级字典 获取, 获取不到就使用一个默认值
        sub_res = res.get(row[0], defaultdict())
        #  第一列不属于设置的log_type的话略过,为空也略过
        if row[0].strip() not in LOG_TYPE:
            if row[0].strip() == '﻿log_type' or row[0].strip() == "":
                continue
            logging.critical(f"未知类型的log_type:{row[0]},LOG_TYPE中可添加.|csv的{index}行")
            continue
        # 第一列属于设置的log_type的话,会处理
        count = sub_res.get(row[2], 0)
        try:
            new_count = int(row[4])
        except ValueError as e:
            logging.critical(f"无法转换为数值类型的count:{row[4]}|csv的{index}行")
            new_count = 0
        sub_res[row[2]] = count + new_count
        res[row[0]].update(sub_res)
    logging.info("succ.")
    return res


import csv


class NewCsvHandler:
    """一个新的处理CSV的分析器"""
    # 2020-04-12
    def __init__(self, csv_path: str):
        """用一个csv路径初始化一个解析器
        并从路径中解析出sourceCode
        解析出 rows [[],[],],一行为一个内部列表"""
        self.rows = list()
        try:
            with open(csv_path, "r", encoding="GBK", newline="") as f:
                csv_content = csv.reader(f)
                for t in csv_content:
                    self.rows.append(t)
        except Exception as e:
            with open(csv_path, "r", encoding="UTF-8", newline="") as f:
                csv_content = csv.reader(f)
                for t in csv_content:
                    self.rows.append(t)
        finally:
            sourcecode = csv_path.split("-")[0].split("/")[-1]
        self.sourceCode = sourcecode
        # 放与excel中差不多对应的结果的
        self.result = []
        self.sum_realname = 0  # 征信总笔数
        self.realname_request_failed = 0  # 请求失败,比如姓名大于20啦,地址大于60或者等于0啦
        self.user_already_regist = 0  # 已在上农注册用户数
        self.user_unregist = 0  # 未注册笔数
        self.ocr_fail = 0  # ocr失败数
        self.ocr_succ = 0  # ocr成功笔数
        self.white_box_succ = 0  # 白盒子通过笔数    namelist=0 (太平)
        self.realname_succ = 0  # 其他的就是返回00 就算
        self.white_box_rate = 1  # 白盒子核准率

        self.sum_credit = 0  # 授信总数
        self.credit_request_failed = 0  # 授信请求出错
        self.credit_succ = 0  # 授信成功
        self.credit_reject = 0  # 信用拒绝
        self.credit_net_fail = 0  # 50003网络错误
        self.credit_antifraud_reject = 0  # 50003 反欺诈拒绝
        self.credit_rate = 1  # 授信核准率

        self.sum_withdraw = 0  # 提现总数
        self.withdraw_failed = 0  # 50005请求失败,网络错误或者啥的,好像用不上
        self.withdraw_succ = 0  # 提现成功笔数
        self.withdraw_antifraud_reject = 0  # 50005 报反欺诈
        self.withdraw_ilog_reject = 0  # 提现风控拒绝
        self.withdraw_pay_failed = 0  # 支付通道拒绝
        # self.total_amt = 0  # 当日提现总额
        self.withdraw_rate = 1  # 当日提现成功率

    def gen_result(self):
        """生成一个列表[,,,],对应相应产品的excel的行里面的数字,
        其实搞个sqlite会很方便,但算了吧"""
        # 太平金服有白盒核准率什么的,要单独算
        for row in self.rows:  # [[],[],...] 取出内部的 []
            # 征信
            if row[0] == "realnameauth":
                self.sum_realname += int(row[-1])
                if row[1] == "00":
                    ...
                if row[1] == "01":
                    self.realname_request_failed += int(row[-1])
                if row[1] == "03":
                    self.user_already_regist += int(row[-1])
                #     未注册用户数 = 总量-请求失败的-已注册的
                self.user_unregist = self.sum_realname - self.realname_request_failed - self.user_already_regist
            elif row[0] == "realnameauth_query":
                if row[1] == "08":
                    self.ocr_fail += int(row[-1])
                if row[1] == "00":
                    self.realname_succ += int(row[-1])
                if row[-2] == "0":
                    #  太平白盒子通过的
                    self.white_box_succ = int(row[-1])
                #   ocr 成功的  等于  总量 - 请求失败的 - 已注册的(未注册的) - ocr失败的
                self.ocr_succ = self.user_unregist - self.ocr_fail
                #  白盒子通过率 = 白盒子name list 0/ocr成功的
                if self.ocr_succ != 0 and self.sourceCode.upper() == "TPJF":
                    self.white_box_rate = self.white_box_succ / self.ocr_succ
                else:
                    self.white_box_rate = self.realname_succ / self.ocr_succ
            # 授信
            elif row[0] == "credit":
                self.sum_credit += int(row[-1])
                if row[2] == "unknow" and len(row[1]) > 2:
                    self.credit_net_fail += int(row[-1])
                if row[-2] == "antifraud reject":
                    self.credit_antifraud_reject += int(row[-1])
                if row[1] == "01" and row[-2] != "antifraud reject":
                    self.credit_request_failed += int(row[-1])
            elif row[0] == "credit_query":
                if row[1] == "02":
                    self.credit_reject += int(row[-1])
                if row[1] == "01":
                    self.credit_succ += int(row[-1])
                if self.sum_credit != 0:
                    self.credit_rate = self.credit_succ / self.sum_credit
            # 提现
            elif row[0] == "withdraw":
                self.sum_withdraw += int(row[-1])
                if row[1] == "01" and row[-2] == "网络错误":
                    self.withdraw_failed += int(row[-1])
                if row[1] == "01" and row[-2] == "antifraud reject":
                    self.withdraw_antifraud_reject += int(row[-1])
                if len(str(row[1])) > 2:
                    self.withdraw_failed += int(row[-1])
            elif row[0] == "withdraw_query":
                if row[2] == "处理成功":
                    self.withdraw_succ += int(row[-1])
                if row[-2] == "放款失败——ilog拒绝":
                    self.withdraw_ilog_reject += int(row[-1])
                if len(row[-2]) > 15:
                    self.withdraw_pay_failed += int(row[-1])
                if row[-2] == "原交易失败":
                    self.withdraw_pay_failed += int(row[-1])
                if self.sum_withdraw != 0:
                    self.withdraw_rate = self.withdraw_succ / self.sum_withdraw
        #  将结果组织到
        self.result.append(self.sum_realname or 0)
        self.result.append(self.realname_request_failed or 0)
        self.result.append(self.user_already_regist or 0)
        self.result.append(self.user_unregist or 0)
        self.result.append(self.ocr_fail or 0)
        self.result.append(self.ocr_succ or 0)
        self.result.append(self.white_box_rate)

        self.result.append(self.sum_credit or 0)
        self.result.append(self.credit_request_failed or 0)
        self.result.append(self.credit_succ or 0)
        self.result.append(self.credit_reject or 0)
        self.result.append(self.credit_net_fail or 0)
        self.result.append(self.credit_antifraud_reject or 0)
        self.result.append(self.credit_rate)

        self.result.append(self.sum_withdraw or 0)
        self.result.append(self.withdraw_failed or 0)
        self.result.append(self.withdraw_succ or 0)
        self.result.append(self.withdraw_antifraud_reject or 0)
        self.result.append(self.withdraw_ilog_reject or 0)
        self.result.append(self.withdraw_pay_failed or 0)
        self.result.append("总额")
        self.result.append(self.withdraw_rate)
        if self.sourceCode.upper() == "TPJF":
            self.result.insert(6, self.white_box_succ)
        else:
            self.result.insert(6, self.realname_succ)
            ...

    def get_result(self):
        return self.result
    def x(self):
        # for y in self.rows:
        #     print(y)
        print(self.sourceCode)
        print(self.result)


def main():
    work_book_path = "excels/Sample.xlsx"
    csv_path = r"csv/source_data/20200409/online_1600000055_20200409_stat.csv"

    my_work_book = MyWorkBook(work_book_path)
    my_csv = CsvParser(csv_path).get_csv_content()

    # 总览表
    total_sheet = my_work_book.get_sheet_by_index(0)
    # 征信分析表
    credit_query_sheet = my_work_book.get_sheet_by_index(1)
    # 授信分析表
    credit_sheet = my_work_book.get_sheet_by_index(2)
    # 提现分析表
    withdraw_sheet = my_work_book.get_sheet_by_index(3)

    # 遍历第二行至最后一行,如果只有一行,则退出
    if len(my_csv) == 1:
        logging.info(f"{csv_path}-->没有进件")
        sys.exit(0)
    #
    # # 获取分析结果 dict 形式
    parse_result = csv_handler(my_csv)
    print(parse_result)
    ...


if __name__ == '__main__':
    # main()
    path1 = "csv/results_output/20200409_qry_res/HB-20200409-qry-res.csv"
    ins = NewCsvHandler(path1)
    ins.gen_result()
    ins.x()
