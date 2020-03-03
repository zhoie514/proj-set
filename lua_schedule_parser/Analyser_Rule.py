"""
function:分析单个调度流程的一个脚本,生成指定格式的csv方便查看
by:zhouhao
email:zhoie@live.com
"""
import csv
import json
import logging
import os
import re
import time
from typing import Union


class MyError(Exception):
    def __init__(self, msg, status="01"):
        ...


logging.basicConfig(format='%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO)

BASE_DIR = os.path.dirname(__file__)


# 将GenRule.json处理成一个字典, "// " 代表注释
def read_json(filepath: str = "GenRule.json") -> Union[str, dict]:
    """
    加载json文件,可以使json中拥有以 // 开头的注释
    :param filepath: json file 的路径
    :return: 返回字典
    """
    if not os.path.isfile(filepath):
        # 文件不存在,返回
        logging.error(filepath + "文件不存在")
        raise FileNotFoundError(filepath + "文件不存在")
    with open(filepath, "r", encoding="utf-8") as f:
        content = ""
        try:
            tmp_line = True
            while tmp_line:
                tmp_line = f.readline()
                if tmp_line.strip().split(" ")[0] == "//" or tmp_line.strip()[
                    0] == "//" or tmp_line.strip() == "//" or tmp_line.strip() == "" or tmp_line.strip()[:2] == "//":
                    continue
                else:
                    content += tmp_line.strip()
        except IndexError as e:
            pass
        except Exception as e:
            logging.error("其他错误")
            raise MyError("其他错误")
        try:
            obj = json.loads(content)
        except json.decoder.JSONDecodeError as e:
            logging.error("解析json失败")
            return {}
    return obj


# 默认提取每一个流程中的 三个字段,返回 [[[],],[[],],...]这种形式,一个流程中,只有一个 ClientReqScriptFile 与 ClientResScriptFile
def parse_services(rule: dict, index_params: tuple = ("ServiceName", "ReqScriptFile", "ResScriptFile")) -> Union[
    list, bool]:
    """
    解析流程里面的东西
    :param rule: json转换成的字典
    :param index_params: 需要从流程中提出来的字段
    :return:[[[],[]],...]  此各形式
    """

    if not isinstance(rule, dict):
        # 非法参数
        logging.error("参数非法")
        return False
    out_list = list()
    out_list.append([[rule["ClientReqScriptFile"], rule["ClientResScriptFile"]]])
    for service_item in rule["Services"]:  # [[]] {}  有clone步骤的,取出的service_item来是 dict
        mid_list = []
        if isinstance(service_item, dict):
            logging.debug("这是一个clone步骤的字典")
            service_item = service_item["Services"][0]  # 将 clone 步骤里面的Services提出来
        for schedue in service_item:
            inside_list = []
            for index_field in index_params:
                try:
                    inside_list.append(schedue[index_field])
                except KeyError:
                    inside_list.append("")
            mid_list.append(inside_list)
        out_list.append(mid_list)
    return out_list


# 判断提取出来的文件相关的字段中的文件是否存在, 并按顺序返回可以打开的lua脚本列表
def exsit_file(file_list: list) -> tuple:
    service_name = []
    if not isinstance(file_list, list):
        return False, False
    for item in file_list:
        if not isinstance(item, list):
            return False, False
        for files in item:
            if not isinstance(files, list):
                return False, False
            if len(files) > 2:  # 针对流程里面的
                service_name.append(files[0])  # 把service_name单独提出来
                files.remove(files[0])  # 主要是删掉service_name这并不是个lua文件
                for file in files:
                    if file == "":
                        # 如果 是 "" 证明没有脚本存在 跳检测
                        files.remove(file)
                        continue
                    if not os.path.isfile(file):
                        logging.critical(f"{file} 不存在")
                        return False, False
            else:  # 针对 ['ClientReqScript.lua']这种
                for file in files:
                    if file == "":
                        files.remove(file)
                        # 如果 是 "" 证明没有脚本存在 跳检测
                        continue
                    if not os.path.isfile(file):
                        logging.critical(f"{file} 不存在")
                        return False, False
    return file_list, service_name


# 处理每个rule文件夹中的所有相关联的lua脚本
def handle(files_list: list, service_names: list):
    """:param files_list 文件路径 list [[[file],],...]
    :param service_name 服务名,空为 ""
    查找lua脚本中的要素
    SetFieldJson,GetFieldJson,SetResName,GetField,SetActionRequest,DelField,SetField
    """
    # 文件不存在不可能进行这个function [[]]
    # csv_list = [[],[]]
    # tmp_list = ["",""]
    csv_list = list()
    csv_list.append(
        ["主流程", "异步查询", "服务名", "url信息", "req脚本中的get", "req.lua中set", "res中的get", "res中的set及del,顺序排列", "lua脚本"])
    service_name_index = -1
    for file_list in files_list:  # get [[file],]
        # 取出每一个step
        for files in file_list:  # get [file]
            tmp_list = []
            tmp_list.append(files_list.index(file_list) - 1)
            tmp_list.append(file_list.index(files))
            if not service_name_index < 0:
                tmp_list.append(service_names[service_name_index])
            service_name_index += 1
            # 取出每个step 中的服务
            # files[0] 一般为req的文件,   files[1]如果存在,一定是res文件, 有可能不存在
            #  假如files[0]也不存在, 只针对 ClientReqScriptFile 与 ClientResScriptFile 均不存在时,
            #  如果一个流程这两个文件都没有,那就没意义了,可以删掉这个流程
            if files[0] == "":
                tmp_list.append("null")
                tmp_list.append("null")
                tmp_list.append("null")
            else:
                with open(files[0], 'r', encoding="utf-8") as f:
                    contents = f.read()
                    # 获取与url相关的东西
                    se_url = re.findall("/+[^json].+[\w,.]+\"", contents)
                    tmp_list.append(utils_join_str_ele(se_url))
                    # 获取req脚本的参数来源
                    se_param_orgin = re.findall("base_op\.[GetFieldJson,GetField]+\(.+\)", contents)
                    tmp_list.append(utils_join_str_ele(se_param_orgin))
                    # 获取req脚本的上下文变量设置
                    se_content_set = re.findall("base_op\.[SetField,SetFieldJson,SetResName]+\(.+\)", contents)
                    tmp_list.append(utils_join_str_ele(se_content_set))
            if len(files) < 2:
                # 证明没有res的脚本存在,加2个空,和下面的对齐
                tmp_list.append("null")
                tmp_list.append("null")
            else:
                # 证明有res脚本存在
                with open(files[1], 'r', encoding="utf-8") as f:
                    contents = f.read()
                    # 获取res脚本的 上下文获取相关的东西
                    se_param_orgin_res = re.findall("base_op\.[GetFieldJson,GetField]+\(.+\)", contents)
                    tmp_list.append(utils_join_str_ele(se_param_orgin_res))
                    # 获取res脚本的 set 和 del 保持源顺序
                    se_param_chg_res = re.findall("base_op\.[SetField,SetFieldJson,DelField]+\(.+\)", contents)
                    tmp_list.append(utils_join_str_ele(se_param_chg_res))
            tmp_list.append(utils_join_str_ele(files))
            csv_list.append(tmp_list)
    #  修复 第一行错位的问题,代码太乱实在找不到为啥会错位
    csv_list[1].insert(2, "")
    return csv_list


# 保存结果
def savefile(ls: list, encoding="gbk"):
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    with open(f'A-{timestamp}.csv', newline="", encoding=encoding, mode="a+") as f:
        writer = csv.writer(f)
        writer.writerows(ls)
        f.flush()
        return
    # ...


def utils_join_str_ele(lst: list, seq: str = "-line-") -> str:
    """
    :param lst: ["a","b"]
    :param seq: 方便在excel中替换为回车
    :return: str, "a回车b"
    """
    res = ""
    if len(lst) == 0:
        res = "null"
    if len(lst) == 1:
        res = str(lst[0]).replace("base_op.", "")
    if len(lst) >= 2:
        ls = [x.replace("base_op.", "") for x in lst]
        res = seq.join(ls)
    return res


def main(encoding="gbk"):
    json2dict = read_json()
    if not isinstance(json2dict, dict):
        logging.error("格式错误")
        return False
    field_list = parse_services(json2dict)
    file_list, service_names = exsit_file(field_list)  # 正常的lua文件
    if not file_list:
        # 如果有错误则返回False
        logging.error("没有lua文件")
        return False
    ls = handle(file_list, service_names)
    savefile(ls, encoding=encoding)
    return True


if __name__ == '__main__':
    """
    1. 用excel打开这个csv,替换-line- 为换行符
        方法:光标定位于替换框，按住Alt打数字小键盘上的0010（放手后看不到任何变化，但实际有换行符），全部替换。
    2. 调调格式什么的
    3, 这样就可以看到变量在哪设置的在哪引用的,在哪删除的
    """
    #  gbk / utf-8 看情况选吧
    main(encoding="gbk")
    logging.info("SUCC.........")
