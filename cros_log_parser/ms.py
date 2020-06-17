#!/usr/bin/python 
# -*- coding: utf-8 -*-
import logging
from datetime import datetime

import pandas as pd
import CONF
import os

import Utils

logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', level=logging.INFO, filename='log.txt')


# df = pd.read_excel(CONF.EXCEL_TAR_PATH, sheet_name=0)


def move_cros_log(source_dir: str, tar_dir: str, file_name: str):
    """
    将cros_log从系统默认的下载路径转移到希望保存的路径
    :param source_dir: 原保存位置
    :param tar_dir: 期望的保存位置
    :param file_name: 文件名
    :return:
    """
    if not os.path.isdir(source_dir):
        os.makedirs(source_dir)
    if not os.path.isfile(os.path.join(source_dir, file_name)):
        logging.critical(f"{file_name} 不存在.")
        return
    if os.path.isfile(os.path.join(tar_dir, file_name)):
        logging.info(f"{filename} 已存在")
        return
    with open(os.path.join(source_dir, file_name), "rb") as f:
        with open(os.path.join(tar_dir, file_name), "wb") as nf:
            nf.write(f.read())
            logging.info(f"{filename} 移动成功")
    # ctrx + x
    if CONF.CLEAR_SOURCE_EXCEL:
        if os.path.isfile(os.path.join(source_dir, file_name)):
            os.remove(os.path.join(source_dir, file_name))
    ...


if __name__ == "__main__":
    filename = Utils.cob_filename(datetime.now())
    move_cros_log(CONF.EXCEL_SOURCE_PATH, CONF.EXCEL_TAR_PATH, filename)
