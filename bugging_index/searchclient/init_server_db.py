import csv
import os

import jieba

from instance import config
from searchclient.db import get_db

with open(config.DEL_WORDS, 'r', encoding="utf8") as f:
    del_words = f.readlines()
    for item in del_words:
        jieba.del_word(item.strip())
with open(config.ADD_WORDS, 'r', encoding="utf8") as f:
    add_words = f.readlines()
    for item in add_words:
        jieba.add_word(item.strip())


def init_err(dir):
    db = get_db()
    with open(os.path.join(dir, 'errorlist.csv'), 'r', encoding="utf8") as f:
        contents = csv.reader(f)
        for content in contents:
            db.execute(
                'insert into errorlist (e_orign,e_describe, e_interface,e_mask,e_category,e_errorinfo,e_logsearch,'
                'e_procedure) values (?,?,?,?,?,?,?,?)',
                (content[1], content[2], content[3], content[4], content[5], content[6], content[7], content[8]))
        db.commit()
    return True


def init_ocrmap(dir):
    db = get_db()
    with open(os.path.join(dir, 'ocrmap.csv'), 'r', encoding="utf8") as f:
        contents = csv.reader(f)
        for content in contents:
            db.execute(
                'insert into ocrmap (o_type,o_code, o_msg) values (?,?,?)',
                (content[1], content[2], content[3]))
        db.commit()
    return True


def init_qa(dir):
    db = get_db()
    with open(os.path.join(dir, 'qanda.csv'), 'r', encoding="utf8") as f:
        contents = csv.reader(f)
        for content in contents:
            db.execute(
                'insert into qanda  (q_orign, q_ques,q_ans) values (?,?,?)',
                (content[1], content[2], content[3]))
        db.commit()
    return True


def init_index_err():
    # 利用结巴分词构建反向索引
    db = get_db()
    sql_1 = "select * from errorlist"
    contents = db.execute(sql_1).fetchall()
    if not contents:
        return False
    for content in contents:
        l = []
        new_l = []
        # content.pop(1)
        for item in content[1:]:
            # 如果item是空字段,jieba.cut会报错
            if item:
                l += jieba.cut_for_search(item)
        for item in l:
            if len(item) > 1:
                new_l.append(item)
        res = set(new_l)
        con_id = []
        for item in res:
            con_id.append((item, content[0]))
        con_id = tuple(con_id)
        db.executemany("insert into err_index (r_content,r_id) values (?, ?);", con_id)
        db.commit()
    return True


def init_index_qa():
    # 利用结巴分词构建反向索引
    db = get_db()
    sql_1 = "select * from qanda"
    contents = db.execute(sql_1).fetchall()
    if not contents:
        return False
    for content in contents:
        l = []
        new_l = []
        for item in content[1:]:
            #  同上
            if item:
                l += jieba.cut_for_search(item)
        for item in l:
            if len(item) > 1:
                new_l.append(item)
        res = set(new_l)
        con_id = []
        for item in res:
            con_id.append((item, content[0]))
        con_id = tuple(con_id)
        db.executemany("insert into qanda_index (r_content,r_id) values (?, ?);", con_id)
        db.commit()
    return True


# sys-ctrl utils

def cut(contents: list):
    con_id = []
    for content in contents:
        l = []
        new_l = []
        for item in content[1:]:
            if item:
                l += jieba.cut_for_search(item)
        for item in l:
            if len(item) > 1:
                new_l.append(item)
        res = set(new_l)
        for item in res:
            con_id.append((item, content[0]))
    con_id = tuple(con_id)
    return con_id


def cut_kw(kw: str):
    res = jieba.cut_for_search(kw)
    return res


# res = cut([["","我们以及url老师"]])
# print(res)
#
# res = jieba.cut_for_search("我们以及url老师")
# print(list(res))