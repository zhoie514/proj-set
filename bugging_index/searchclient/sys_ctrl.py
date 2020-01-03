import csv
import os
from imp import reload

from flask import (Blueprint, render_template, redirect, url_for, current_app,
                   request)
from werkzeug.utils import secure_filename
from instance.config import (BACKUP_DIR)
import instance.config
from searchclient.db import get_db
from flask_cors import cross_origin

from . import init_server_db as initdb

bp = Blueprint("sys", __name__, url_prefix="/sys")


@bp.route("/")
def tt():
    return render_template("sys_ctrl/sysctrl_page.html")


@bp.route("/reverse-index/<name>")
@cross_origin()
def rebuild_index(name):
    # 重建索引, 将索引数据库删掉,重建,此接口可以做成ajax请求,数据多的情况下返回较慢
    if name == "err":
        name = "errorlist"
    elif name == "qa":
        name = "qanda"
    else:
        return {"code": 405, "msg": "Error Name"}
    reload(instance.config)
    REBUILD = instance.config.REBUILD
    if REBUILD:
        db = get_db()
        select_sql = "select * from {}".format(name)
        contents = db.execute(select_sql).fetchall()
        if not contents:
            return {"code": 200, "msg": "blank Database"}
        # 生成倒排索引的 v-id值列表con_id为 ((value,id),())形式
        con_id = initdb.cut(contents)
        if name == "errorlist":
            db.execute("delete from err_index")
            db.executemany(
                "insert into err_index (r_content,r_id) values (?, ?);",
                con_id)
            db.commit()
        elif name == "qanda":
            db.execute("delete from qanda_index")
            db.executemany(
                "insert into qanda_index (r_content,r_id) values (?, ?);",
                con_id)
            db.commit()
    if not REBUILD:
        return {"code": 403, "msg": "not allowed"}

    return {"code": 200, "msg": "重建'{}'索引完成...".format(name)}


@bp.route("/backup")
@cross_origin()
def backup():
    # 将数据库的数据全部导出为 csv文件,通过ip:port/static/csv/errorlist[qanda/ocrmap]可以下载
    # 也可以做成ajax来访问,备份虽然很快
    # 本来想做成分类选择备份的,后来一想,没必要,就改成统一备份了,另外索引数据库未进行备份,重新生成即可
    for name in ["err", "qa", "ocrmap"]:
        if name == "err":
            name = "errorlist"
        elif name == "qa":
            name = "qanda"
        elif name == "ocrmap":
            name = "ocrmap"
        else:
            return {"code": 405, "msg": "Error Name"}

        reload(instance.config)
        if not instance.config.BACKUP:
            return {"code": 403, "msg": "暂时关闭功能,请联系管理员"}

        db = get_db()
        select_sql = "select * from {}".format(name)
        contents = db.execute(select_sql).fetchall()
        with open(os.path.join(BACKUP_DIR, "{}.csv".format(name)),
                  "w+",
                  newline="") as f:
            writer = csv.writer(f)
            writer.writerows(contents)
            f.flush()
    return {"code": 200, "msg": u"备份数据库完成..."}


@bp.route("/init/<name>")
@cross_origin()
def init(name):
    # 将之前备份为csv的文件进行还原
    # 由于必定有一个原始的csv ,故不做是否存在的检验
    # 前端可以做成ajax请求,耗时较久
    reload(instance.config)
    if not instance.config.INIT:
        return {"code": 405, "msg": "not allowed"}
    if name == "db":
        db = get_db()
        with current_app.open_resource("buildDatabase.sql") as f:
            # pass
            db.executescript(f.read().decode("utf8"))
        initdb.init_err(BACKUP_DIR)
        initdb.init_qa(BACKUP_DIR)
        initdb.init_ocrmap(BACKUP_DIR)
        initdb.init_index_err()
        initdb.init_index_qa()
        return {"code": 200, "msg": u"数据库还原成功..."}
    return {"code": 404, "msg": "not found"}


@bp.route("/add-err", methods=("post", ))
@cross_origin()
def add_err():
    reload(instance.config)
    if not instance.config.IMPORT_CSV:
        return {"code": 204, "msg": "暂时关闭此功能,请联系管理员"}
    try:
        f = request.files['errorlist']
    except Exception as e:
        return {"code": 201, "msg": "文件错误"}
    # 验证文件类型是否是 csv
    if f.filename[-3:] != "csv":
        #  如果不正确就不保存这个文件了
        return {"code": 205, "msg": "文件类型不正确"}

    save_path = current_app.instance_path[:-8] + "searchclient/static/upload_csv/errorlist.csv"
    f.save(save_path)
    with open(save_path, 'r', encoding="utf-8") as f:
        # 验证csv文件的每条记录的数量是否正确
        contents = csv.reader(f)
        for content in contents:
            column = 0
            for item in content:
                column += 1
            if column != 9:
                return {"code": 206, "msg": "每条记录的元素不正确."}
    # 通过验证后,将数据写入数据库
    add_path = save_path[:-14]
    # 写入数据库
    initdb.init_err(add_path)
    # 创建索引
    initdb.init_index_err()
    return {"code": 200, "msg": "添加记录完成..."}


@bp.route("/add-qa", methods=("post", ))
@cross_origin()
def add_qa():
    reload(instance.config)
    if not instance.config.IMPORT_CSV:
        return {"code": 204, "msg": "暂时关闭此功能,请联系管理员"}
    try:
        f = request.files['qanda']
    except Exception as e:
        return {"code": 201, "msg": "文件错误"}
    # 验证文件类型是否是 csv
    if f.filename[-3:] != "csv":
        #  如果不正确就不保存这个文件了
        return {"code": 205, "msg": "文件类型不正确"}

    save_path = current_app.instance_path[:-8] + "searchclient/static/upload_csv/qanda.csv"
    f.save(save_path)
    with open(save_path, 'r', encoding="utf-8") as f:
        # 验证csv文件的每条记录的数量是否正确
        contents = csv.reader(f)
        for content in contents:
            column = 0
            for item in content:
                column += 1
            if column != 4:
                return {"code": 206, "msg": "每条记录的元素不正确."}
    # 通过验证后,将数据写入数据库
    add_path = save_path[:-9]
    # 写入数据库
    initdb.init_qa(add_path)
    # 创建索引
    initdb.init_index_qa()
    return {"code": 200, "msg": "添加记录完成..."}