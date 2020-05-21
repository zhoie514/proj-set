# coding:utf-8
import logging
import time
from datetime import timedelta, datetime
from threading import Thread

import CONF
import Utils
import s1_unzip_file
from s2_sort_file import sort_file
from s3_parse_result import read_csv, make_lite_files
from s4_make_res_zip_email import makezip
from s5_ana_query_csv import main

logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', level=logging.INFO, filename='log_merge.txt')

date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET)).strftime("%Y%m%d")

#  s1 unzip
ZIP_DIR = f"{CONF.ZIP_DIR}/{date}_zd_query_result.zip"
ZIP_DIR_NORMAL = f"{CONF.ZIP_DIR}/{date}.zip"
TARGET_DIR = f"{CONF.SOURCE_DIR}/{date}_zd_query_result/"
TARGET_DIR_NORMAL = f"{CONF.SOURCE_DIR}/{date}/"
s1_unzip_file.un_zip(ZIP_DIR, TARGET_DIR)
s1_unzip_file.un_zip(ZIP_DIR_NORMAL, TARGET_DIR_NORMAL)
print("-----解压缩完成-----")

#  s2 sort File
filepaths = Utils.gen_filapaths(date, CONF.CMD_ID)
for file in filepaths:
    sort_file(file)

filepaths = Utils.gen_filapaths(date, CONF.CMD_ID)
print("-----排序完成-----")


#   s3  parse result
def mult_thread_run():
    st = time.time()
    jobs = []
    for filepath in filepaths:
        trd = Thread(target=read_csv, args=(filepath, date))
        jobs.append(trd)
        trd.start()
    for trd in jobs:
        trd.join()
    print("生成结果用时：", time.time() - st)  # 3.几 秒  辣鸡


mult_thread_run()
make_lite_files(date, CONF.PRODUCTS)
print("-----删除多余的文件-----")

#  s4 simplify files and zip
zip_file_name = makezip(f"{CONF.OUTPUT_DIR}/{date}_qry_res", CONF.ZIP_GEN_DIR, force=True)
print("-----csv文件压缩完成-----")


#  s5 生成excel
def xm(date: str = None):
    source_codes = ("HB", "TPJF", "LX",)
    if not date:
        date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET)).strftime("%Y%m%d")
    files = Utils.gen_res_file_path(date, source_codes)
    # excel文件名用的日期
    simple_date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET)).strftime("%Y-%m")

    for f in files:
        if "TPJF" in f:
            main(f, f"excels/TPJF-{simple_date}.xlsx")
        if "HB" in f:
            main(f, f"excels/HB-{simple_date}.xlsx")
        if "LX" in f:
            main(f, f"excels/LX-{simple_date}.xlsx")
        if "QH" in f:
            main(f, f"excels/QH-{simple_date}.xlsx", source_code="")


xm()
