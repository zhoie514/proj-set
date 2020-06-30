#!/usr/bin/python 
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import CONF


def cob_filename(dt: datetime):
    """
    生成 cros_log清洗统计结果_2020-06-17.xlsx 这样的文件名
    :param dt: 当前日期
    :return: str
    """
    dt_format = (dt + timedelta(days=CONF.OFFSET_DAY + 1)).strftime("%Y-%m-%d")
    return f"cros_log清洗统计结果_{dt_format}.xlsx"


def fix_filename(dt: datetime):
    """生成 核心放款结果 统计_2020-06-28.xlsx 这样的文件名"""
    dt_format = (dt + timedelta(days=CONF.OFFSET_DAY + 1)).strftime("%Y-%m-%d")
    return f"核心放款_{dt_format}.xlsx "


if __name__ == '__main__':
    x = cob_filename(datetime.now())
    print(x)
