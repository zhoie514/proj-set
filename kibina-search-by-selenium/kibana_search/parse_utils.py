"""解析工具, 文本处理相关"""
import json
import re
from typing import List, Union


def json2dict(filepath: str) -> Union[dict, str]:
    """
    加载json文件,可以使json中拥有以 # 开头的注释
    :param filepath: json file 的路径
    :return: 一个字典 文件解析错误返回{"error":"error_info"}
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = ""
        try:
            tmp_line = True
            while tmp_line:
                tmp_line = f.readline()
                if tmp_line.split(" ")[0] == "//" or tmp_line.strip()[0] == "//" or tmp_line.strip() == "//":
                    continue
                else:
                    content += tmp_line.strip()
        except IndexError as e:
            pass
        except Exception as e:
            return f"解析错误{e}"
        try:
            obj = json.loads(content)
        except json.decoder.JSONDecodeError as e:
            return f"解析错误{e}"
    return obj


def parse_actions_field(string: str) -> List[dict]:
    """
    解析从网页中获取的字符串  主要针对 doc.actions 这个字段的
    :param string:input {"":"","":"",...},{"":"","":"",...}...
    :return:[{"":"","":"",...},{"":"","":"",...},...]
    """
    string = '['+string+']'
    return json.loads(string)



def parse_index(web_content: List, config_content: List) -> List[int]:
    """
    对比网页中看到的表数据的列数 与 default/custom中的列数 去掉不要的
    :param web_content: 网页中拿到的表头的列表
    :param config_content: config文件中的scratch_field字段中的字段
    :return: 返回 web_content 中需要元素的索引值 [int]
    :error: 如果 config 中的某个元素不在 web_co..中,会报错
    """
    res = []
    # 忽略大小写
    web_content = [item.lower() for item in web_content]
    for e in config_content:
        try:
            x = web_content.index(e.lower())
            res.append(x)
        except ValueError:
            raise ValueError(f'{e} 字段不在网页中,请把网页调整一下,重新复制url')
    if len(res) == 0:
        raise ValueError('所有字段均不在网页中,请把网页调整一下,重新复制url')
    # 一个比较秀的写法 但想有详细的 Error 丢出来,且后者要求全匹配, 故pass
    # res = [web_content.index(item) for item in web_content for item2 in config_content if item.lower() == item2.lower()]
    return list(set(res))


def input2list(filepath: str) -> list:
    res = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        for line in f.readlines():
            obj = re.search(r'(\w+)', line)
            res.append(obj.group(1))
    return res


# class DefError(Exception):
#     pass


if __name__ == '__main__':
    #  可以 检测 json 文件 是否能正确解析
    #  出错的话,得去找找原因
    cust = json2dict("custom_config.json")
    print(cust)
    defa = json2dict('default_config.json')
    print(defa)
