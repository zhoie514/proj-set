# step 2
# 分析解压后的csv日志
# 生成文件：N个产品的csv
"""分析 50002/4/6/15 的日志源文件的脚本,用来根据产品生成结构化的csv文件
by zhouhao
date 2020-03-26
update 2020-04-02"""
import codecs
import csv
import json
import os
import time
import logging

from collections import defaultdict
from datetime import timedelta, datetime
from threading import Thread

import CONF
import Utils

logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', level=logging.INFO, filename='log_results.txt')


def save_file_csv(timestamp: str, obj: dict) -> None:
    """生成每个产品,每个cmd_id对应的 CSV """
    # 先创建一个符合日期的目录
    if not os.path.isdir(f"{CONF.OUTPUT_DIR}/{timestamp}_qry_res"):
        os.makedirs(f"{CONF.OUTPUT_DIR}/{timestamp}_qry_res")

    cmd_id = None
    for product in obj:
        # product : "HB","TPJF",etc
        # {product:{(k1,k2,...):count,...},...}
        for k in obj[product]:
            if not cmd_id:
                try:
                    cmd_id = k[-1]
                except Exception as e:
                    print(e)
                    continue
        with open(f"{CONF.OUTPUT_DIR}/{timestamp}_qry_res/{product}-{cmd_id}-{timestamp}-res.csv", "w+",
                  encoding="utf-8",
                  newline="") as f:
            writter = csv.writer(f)
            if cmd_id == "50002":
                if product == "TPJF":
                    # 太平要多写一列name_list
                    writter.writerows([["log_type", "rsp_code", "result", "rsp_msg", "err", "name_list", "count"]])
                else:
                    writter.writerows([["log_type", "rsp_code", "result", "rsp_msg", "err", "count"]])
                for tup in obj[product]:
                    t = list(tup[:-1])
                    t.append(obj[product][tup])  # 添加统计计数
                    row = [t]  # [[1,1,1,1,]] 形式才行
                    writter.writerows(row)
                logging.info(f"{product}|50002|文件生成成功")
            elif cmd_id == "50004":
                writter.writerows([["log_type", "rsp_code", "result", "rsp_msg", "err", "count"]])
                for tup in obj[product]:
                    t = list(tup[:-1])
                    t.append(obj[product][tup])  # 添加统计计数
                    row = [t]  # [[1,1,1,1,]] 形式才行
                    writter.writerows(row)
                logging.info(f"{product}|50004|文件生成成功")
            elif cmd_id in ("50006"):
                writter.writerows([["log_type", "result", "rsp_msg", "err", "count"]])
                for tup in obj[product]:
                    t = list(tup[:-1])
                    t.append(obj[product][tup])  # 添加统计计数
                    row = [t]  # [[1,1,1,1,]] 形式才行
                    writter.writerows(row)
                logging.info(f"{product}|50006|文件生成成功")
            elif cmd_id == "50015":
                writter.writerows([["log_type", "result", "rsp_msg", "err", "count"]])
                for tup in obj[product]:
                    t = list(tup[:-1])
                    t.append(obj[product][tup])  # 添加统计计数
                    row = [t]  # [[1,1,1,1,]] 形式才行
                    writter.writerows(row)
                logging.info(f"{product}|50015|文件生成成功")
            elif cmd_id in ("50001", "50003", "50005", "50014"):
                writter.writerows([["log_type", "rsp_code", "result", "rsp_msg", "err", "count"]])
                for tup in obj[product]:
                    t = list(tup[:-1])
                    t.append(obj[product][tup])  # 添加统计计数
                    row = [t]  # [[1,1,1,1,]] 形式才行
                    writter.writerows(row)
                logging.info(f"{product}|{cmd_id}|文件生成成功")
            else:
                logging.error(f"cmd_id:{cmd_id}未知错误.")


def parse_row_obj(obj: dict) -> ():
    """解析每一行 数据, 返回元组 与 int(1)"""
    log_type = obj["_source"]["log_type"] or ""
    rsp_msg = obj["_source"]["rsp_msg"] or ""
    err = obj["_source"]["err"] or ""
    result = obj["_source"]["result"] or ""
    rule_num = obj["_source"]["rule_num"] or ""
    name_list = "-999"
    rsp_code = obj["_source"].get("rsp_code", -999)

    if obj["_source"]["rule_num"] == "50002":
        rsp_code = obj["_source"]["rsp_code"] or ""
        # 针对太平筛选name_list = 1 或 0 的
        if obj["_source"]["extra"]["source_code"].upper() == "TPJF":
            # 处理中的 50002 不会返回name_list,所以做此处理
            string = obj["_source"]["extra"]["pbc_data"].encode("utf8")
            # if string == b"":
            #     print(obj["_source"]["extra"])
            if string != b"":
                name_list = json.loads(string).get("name_list", -1)
            return (log_type, rsp_code, result, rsp_msg, err, name_list, rule_num), 1
        return (log_type, rsp_code, result, rsp_msg, err, rule_num), 1
    # 授信
    if obj["_source"]["rule_num"] == "50004":
        rsp_code = obj["_source"]["rsp_code"] or ""
        return (log_type, rsp_code, result, rsp_msg, err, rule_num), 1
    # 放款
    if obj["_source"]["rule_num"] in ("50006", "50015"):
        # 筛数据临时用的代码
        if CONF.DEBUG == True:
            if obj["_source"]["extra"]["source_code"] == "QH" and obj["_source"]["rsp_msg"] == "其它错误":
                print("流水号:", obj["_source"]["extra"]["serial_no"], " , ", "trx:", obj["_source"]["trx"])
        return (log_type, result, rsp_msg, err, rule_num), 1
    if obj["_source"]["rule_num"] in ("50001", "50003", "50005", "50014"):
        return (log_type, rsp_code, result, rsp_msg, err, rule_num), 1
    # 都不符合打印一个错误日志
    logging.error(f'{obj["_source"]["rule_num"]}|未知的cmd_id')
    return (), 1


# 解析 csv 文件, 并生成产品对应的csv文件
def read_csv(filepath: str, date) -> dict:
    """解析 CSV 按产品统计"""
    # 返回数据格式为{"tpjf":{(k,k2):int(count),...},"lx":{(k1,k2):1}...}
    result = defaultdict(dict)
    if not os.path.isfile(filepath):
        logging.error(f"{filepath}不存在")
        return {}
    with open(filepath, 'rb') as f:
        # 读取 csv 文件,每一行为一个 json str
        contents = f.readlines()
        i = 0  # 计数
        total = len(contents)  # 总记录条数
        uin_serial = []  # 记录唯一流水号
        for row in contents:
            if row.startswith(codecs.BOM_UTF8):
                row = row.decode("utf8").encode("utf8")
            i += 1
            row_obj = json.loads(row)
            # 针对同一流水号的请求,对方请求N次进行筛选
            # 由于日志是倒序的,相同流水的日志，第一条必然是当天所能统计的终态
            # req_params = json.loads(row_obj["_source"]["extra"]["req_params"])
            if row_obj["_source"]["log_type"] not in CONF.LOG_TYPE:
                # 有一个register 事件是202004-23新增的，其内部没有extra字段,导致脚本有个值没取到，bug
                # 不在规定Log_type内的事件 排除掉，不统计
                continue
            try:
                req_params = eval(row_obj["_source"]["extra"]["req_params"])
            except:
                try:
                    req_params = eval(row_obj["_source"]["extra"]["loanReqNo"])
                except:
                    req_params = {"pbocQueryNo": "null", "loanReqNo": "null"}
            serial = req_params.get('pbocQueryNo', "") or req_params.get('loanReqNo', "")

            if serial in uin_serial:
                if CONF.DEBUG is True and row_obj["_source"]["extra"]["source_code"] == "HB" and row_obj["_source"]["rule_num"] == "50001":
                    print(serial)
                continue
            uin_serial.append(serial)

            # 返回 要统计的字段的 元组形式 （）
            t_key, t_count = parse_row_obj(row_obj)
            sub_result = result.get(row_obj["_source"]["extra"]["source_code"].upper(), defaultdict())
            # 获得原来的t_key的 count
            count = sub_result.get(t_key, 0)
            # 每次加 1
            new_count = count + t_count
            # 更新这个sub result
            sub_result[t_key] = new_count
            # 更新 比如 TPJF 内部的 dict
            result[row_obj["_source"]["extra"]["source_code"]].update(sub_result)
        logging.info(f"{row_obj['_source']['rule_num']}|共有{str(total)}条数据,解析完成{str(i)}条")
    #     保存文件
    save_file_csv(date, result)
    return result


def make_lite_files(date: str, products: tuple):
    """将单个产品的 50002 50004文件合并，
    有多少个产品->生成多少个文件，减少冗余"""
    filedir = f"{CONF.OUTPUT_DIR}/{date}_qry_res"
    gbk = "gbk"

    # 首先删除以前的成品输出
    for pro in products:
        if os.path.isfile(f"{filedir}/{pro}-{date}-qry-res.csv"):
            os.remove(f"{filedir}/{pro}-{date}-qry-res.csv")
    #  获取当日output 下的所有文件
    filenames = os.listdir(filedir)

    # 取出每一个产品编号
    for pro in products:
        # 取出包含该产品号的N个文件,将N个文件合并为一个新文件
        for name in filenames:
            if pro in name:
                with open(f"{filedir}/{name}", "r", encoding="utf-8") as of:
                    contents = of.read()
                    with open(f"{filedir}/{pro}-{date}-qry-res.csv", "a+", encoding=gbk) as nf:
                        nf.write(contents)

    # 如果有这个标志,会在生成新文件后,将合并前的旧文件删除,反正也不大,看心情
    if CONF.LITE_DEL:
        for file in filenames:
            os.remove(f"{filedir}/{file}")


if __name__ == "__main__":
    # 转换一下日期,为昨天
    date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET)).strftime("%Y%m%d")

    filepaths = Utils.gen_filapaths(date, CONF.CMD_ID)


    def sin_thread_run():
        st = time.time()
        for filepath in filepaths[:]:
            read_csv(filepath, date)
        print("单线程用时：", time.time() - st)  # 4.几秒


    def mult_thread_run():
        st = time.time()
        jobs = []
        for filepath in filepaths:
            trd = Thread(target=read_csv, args=(filepath, date))
            jobs.append(trd)
            trd.start()
        for trd in jobs:
            trd.join()
        print("多线程用时：", time.time() - st)  # 3.几 秒  辣鸡
        logging.info(f"多线程用时: {time.time() - st} 秒")


    mult_thread_run()
    # sin_thread_run()
    make_lite_files(date, CONF.PRODUCTS)
