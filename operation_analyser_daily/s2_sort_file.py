"""
由于收到的原始日志数据是无序的
故按时间戳从大到小进行排序
先解压,再排序
"""

import codecs
import json
import logging
import os
from datetime import timedelta, datetime

import CONF
import Utils

logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', level=logging.INFO, filename='log_sort.txt')


def sort_file(filepath: str):
    """将文件按时间戳进行排序 """
    res = list()
    if not os.path.isfile(filepath):
        # 文件不存在 返回
        logging.critical(f"{filepath}:不存在")
        return
    with open(filepath, 'rb') as f:
        # 读取 csv 文件,每一行为一个 json str
        contents = f.readlines()
        total = len(contents)  # 总记录条数 后面用来核对数量的
        for row in contents:
            if row.startswith(codecs.BOM_UTF8):
                row = row.decode("utf8").encode("utf8")
            row_obj = json.loads(row)
            res.append(row_obj)  # 将字典添加到列表中
    #     打印一下日志,看看记录数量
    logging.info(f"{row_obj['_source']['rule_num']}|共有{str(total)}条数据,解析完成{len(res)}条")
    #     保存文件
    # 对列表进行排序
    sorted_res = sorted(res, key=lambda v: v["_source"]['update_time'], reverse=True)
    # 将内部的字典转化为str
    sorted_res = [json.dumps(x) for x in sorted_res]
    # 再写入文件
    with open(filepath, 'w', encoding='utf-8', newline="") as f:
        f.writelines([x + "\n" for x in sorted_res])
        logging.info(f"{filepath}排序完成")
    return None


if __name__ == '__main__':

    date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET)).strftime("%Y%m%d")
    filepaths = Utils.gen_filapaths(date, CONF.CMD_ID)
    for file in filepaths:
        sort_file(file)
