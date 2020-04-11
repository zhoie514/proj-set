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
    main()
    ...
