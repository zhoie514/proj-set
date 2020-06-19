#!/usr/bin/python 
# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import zipfile
import smtplib
import pandas as pd
import CONF
import os
from os import PathLike

import Utils

logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', level=logging.INFO, filename='log.txt')


# df = pd.read_excel(CONF.EXCEL_TAR_PATH, sheet_name=0)


def move_cros_log(source_dir: str, tar_dir: str, file_name: str):
    """
    将cros_log从系统默认的下载路径转移到希望保存的路径
    :param source_dir: 原保存位置
    :param tar_dir: 期望的保存位置
    :param file_name: 文件名
    :return: None or 1
    """
    if not os.path.isdir(tar_dir):
        os.makedirs(tar_dir)
    if os.path.isfile(os.path.join(tar_dir, file_name)):
        logging.info(f" {file_name} 已存在")
        return 1
    if not os.path.isfile(os.path.join(source_dir, file_name)):
        logging.critical(f" {file_name} 不存在.")
        return
    with open(os.path.join(source_dir, file_name), "rb") as f:
        with open(os.path.join(tar_dir, file_name), "wb+") as nf:
            nf.write(f.read())
            logging.info(f" {file_name} 移动成功")
    # ctrx + x
    if CONF.CLEAR_SOURCE_EXCEL:
        if os.path.isfile(os.path.join(source_dir, file_name)):
            os.remove(os.path.join(source_dir, file_name))
    return 1


class Tool:
    def __init__(self):
        self.inits()
        self.res = {}

    def inits(self):

        self.zx_sum = 0  # 请求总量
        self.zx_request_failed = 0  # 请求失败
        self.zx_already_regist = 0  # 已注册用户
        self.zx_unregist = 0  # 未注册
        self.zx_ocr_failed = 0  # ocr失败
        self.zx_code_06 = 0
        self.zx_code_04 = 0
        self.zx_succ = 0
        self.zx_succ_rate = 0

        self.sx_sum = 0  # 授信总量
        self.sx_request_failed = 0  # 请求失败
        self.sx_succ = 0  # 授信成功
        self.sx_ilog_reject = 0  # 信用拒绝
        self.sx_antifraud_reject = 0  # 反欺诈拒绝
        self.sx_net_failed = 0  # 网络错误
        self.sx_succ_rate = 0  # 授信成功率

        self.tx_sum = 0  # 提现总笔数
        self.tx_request_failed = 0  # 请求失败
        self.tx_succ = 0  # 提现成功笔数
        self.tx_antifraud_reject = 0  # 反欺诈拒绝
        self.tx_ilog_reject = 0  # 风控拒绝
        self.tx_pay_failed = 0  # 支付拒绝
        self.tx_amtques = 0  # 额度问题
        self.tx_succ_rate = 0

        self.ch_flag = False

    def gen_result(self, dt: pd.DataFrame):
        """
        {"HB":[1,2,3,...],}
        :param dt: 表格数据
        :return:
        """
        for col, row in dt.iterrows():
            try:
                if row['production_code'] != dt.at[col + 1, 'production_code']:
                    self.ch_flag = True
            except KeyError as e:
                try:
                    print("换行:", f"{row['production_code']} -> f{dt.at[col + 1, 'production_code']}")
                except KeyError as e:
                    print()
            if row['log_type'] == "realnameauth":
                self.zx_sum += int(row['count'])
                if str(row['rsp_code']) == "1":
                    self.zx_request_failed += int(row['count'])
                if str(row['rsp_code']) == '3':
                    self.zx_already_regist += int(row['count'])
                self.zx_unregist = self.zx_sum - self.zx_request_failed - self.zx_already_regist
            if row['log_type'] == 'realnameauth_query':
                if str(row['rsp_code']) == "8":
                    self.zx_ocr_failed += int(row['count'])
                if str(row['rsp_code']) == "4":
                    self.zx_code_04 = int(row['count'])
                if str(row['rsp_code']) == "6":
                    self.zx_code_06 = int(row['count'])
                if str(row['rsp_code']) == "0":
                    self.zx_succ = int(row['count'])
                if self.zx_sum:
                    self.zx_succ_rate = self.zx_succ / self.zx_sum
            if row['log_type'] == "credit":
                self.sx_sum += int(row['count'])
                if row['result'] == "success" and str(row['rsp_code']) == "0":
                    self.sx_succ += int(row['count'])
                if row['err'] == "antifraud reject" and str(row['rsp_code']) == "1":
                    self.sx_antifraud_reject += int(row['count'])
                if row['result'] == "reject" and str(row['rsp_code']) == "0":
                    self.sx_ilog_reject += int(row['count'])
                if row['err'] != "antifraud reject" and str(row['rsp_code']) == "1":
                    self.sx_request_failed += int(row['count'])
                if len(str(row['rsp_code'])) > 2:
                    self.sx_request_failed += int(row['count'])
                if self.sx_sum:
                    self.sx_succ_rate = self.sx_succ / self.sx_sum
            if row['log_type'] == 'withdraw':
                if row['result'] != "review":
                    self.tx_sum += int(row['count'])
                if row['result'] == "reject" and str(row['rsp_code']) == '0':
                    self.tx_ilog_reject += int(row['count'])
                if row['err'] == "antifraud reject" and str(row['rsp_code']) == '1':
                    self.tx_antifraud_reject += int(row['count'])
                if row['err'] in CONF.REQUEST_FAILED:
                    self.tx_request_failed += int(row['count'])
                if str(row['production_code']) == "SQC" and row['result'] == "success":
                    self.tx_succ += int(row['count'])
            if row['log_type'] == 'withdraw_query':
                if row['result'] == "BCMS4027":
                    self.tx_amtques += int(row['count'])
                # 核心支付成功与失败通过 核心的成功失败表去纠正,这里统计的成功不做数
                elif str(row['rsp_code']) == "0":
                    if str(row['production_code']) != "SQC":
                        self.tx_succ += int(row['count'])
            if self.tx_sum:
                self.tx_succ_rate = self.tx_succ / self.tx_sum

            # 上面把数据拿完了
            # 下面组织 一条记录
            self.res[row['production_code']] = [
                (datetime.now() + timedelta(days=CONF.OFFSET_DAY)).strftime("%Y-%m-%d"),
                self.zx_sum,
                self.zx_request_failed,
                self.zx_already_regist,
                self.zx_unregist,
                self.zx_ocr_failed,
                self.zx_code_06,
                self.zx_code_04,
                self.zx_succ,
                self.zx_succ_rate,
                self.sx_sum,
                self.sx_request_failed,
                self.sx_succ,
                self.sx_ilog_reject,
                self.sx_net_failed,
                self.sx_antifraud_reject,
                self.sx_succ_rate,
                self.tx_sum,
                self.tx_request_failed,
                self.tx_succ,
                self.tx_antifraud_reject,
                self.tx_ilog_reject,
                self.tx_amtques,
                self.tx_pay_failed,
                self.tx_succ_rate or '-'
            ]
            # 判断是否要换一个产品了
            if self.ch_flag:
                self.inits()
                self.ch_flag = False

    def get_result(self):
        return self.res


class MyExcel:
    def __init__(self, data: dict):
        self.data_struc = []
        for k in data:
            if os.path.isfile(os.path.join(CONF.EXCEL_OUT, f'{k}.xlsx')):
                self.data_struc.append(
                    {"wb": load_workbook(os.path.join(CONF.EXCEL_OUT, f'{k}.xlsx')),
                     "datas": data[k],
                     "wb_name": f'{k}.xlsx'})

    def append_row(self):
        for dic in self.data_struc:
            single_sheet = dic.get('wb').get_sheet_by_name('Sheet1')
            data_row = dic.get('datas')
            for grid in range(1, 1000):
                blank_row = single_sheet.cell(row=grid, column=1)
                if not blank_row.value:
                    for col in range(0, len(data_row)):
                        single_sheet.cell(row=blank_row.row, column=col + 1).value = data_row[col]
                    break
            dic.get('wb').save(os.path.join(CONF.EXCEL_OUT, dic.get("wb_name")))
            logging.info(f" {dic.get('wb_name')} 已生成")
        return


def zipfiles():
    if not os.path.isdir(CONF.ZIP_OUT):
        os.makedirs(CONF.ZIP_OUT)
    # 内部邮件附件
    f_selfy = zipfile.ZipFile(
        os.path.join(CONF.ZIP_OUT,
                     f'{(datetime.now() + timedelta(days=CONF.OFFSET_DAY)).strftime("%Y-%m-%d")}_助贷流量excel内部统计结果.zip')
        , 'w', zipfile.ZIP_DEFLATED)
    # 内部全量文件
    selfy_files = []
    for f in CONF.SELFY_FILES:
        prod_file = os.path.join(CONF.EXCEL_OUT, f"{f}.xlsx")
        if os.path.isfile(prod_file):
            selfy_files.append(prod_file)
    # 压缩
    for i in selfy_files:
        file = i.split('/')[-1].split('\\')[-1]
        f_selfy.write(i, file)
    f_selfy.close()

    # 外部邮件附件
    f_out = zipfile.ZipFile(
        os.path.join(CONF.ZIP_OUT,
                     f'{(datetime.now() + timedelta(days=CONF.OFFSET_DAY)).strftime("%Y-%m-%d")}_助贷流量excel统计结果.zip')
        , 'w', zipfile.ZIP_DEFLATED)

    # 对外发送的文件
    out_files = []
    for f in CONF.OUT_FILES:
        prod_file = os.path.join(CONF.EXCEL_OUT, f"{f}.xlsx")
        if os.path.isfile(prod_file):
            out_files.append(prod_file)

    for i in out_files:
        file = i.split('/')[-1]
        f_out.write(i, file)
    f_out.close()
    logging.info(" 压缩包生成-成功 ")
    return f_selfy.filename.split('\\')[-1], f_out.filename.split('\\')[-1]


if __name__ == "__main__":
    # filename = Utils.cob_filename(datetime.now())
    # move_cros_log(CONF.EXCEL_SOURCE_PATH, CONF.EXCEL_TAR_PATH, filename)
    # xl_data = pd.read_excel(os.path.join(CONF.EXCEL_TAR_PATH, filename), header=1)
    # xl_data.replace(CONF.PROD_CODE, CONF.PROD_NAME, inplace=True)
    # # print(xl_data)
    # tool = Tool()
    # tool.gen_result(xl_data)
    # res = tool.get_result()
    # for k in res:
    #     print(k, ":", res[k])
    # myexcel = MyExcel(res)
    # myexcel.append_row()

    a, b = zipfiles()
    print(a, b)
