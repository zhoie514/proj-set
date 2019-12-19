import os
import csv
import jieba
from flask import (Blueprint, render_template, redirect, url_for, current_app)
from searchclient.db import get_db
from instance.config import (REBUILD, DEL_WORDS, BACKUP, BACKUP_DIR, INIT)
from . import init_server_db as initdb

bp = Blueprint("sys", __name__, url_prefix="/sys")


@bp.route("/")
def tt():
    return render_template("sys_ctrl/sysctrl_page.html")


@bp.route("/reverse-index/<name>")
def rebuild_index(name):
    # 重建索引, 将索引数据库删掉,重建
    if name == "err":
        name = "errorlist"
    elif name == "qa":
        name = "qanda"
    else:
        return {"code": 200, "msg": "Error Name"}

    if REBUILD:
        with open(DEL_WORDS, 'r', encoding="utf8") as f:
            del_words = f.read()
        jieba.del_word(del_words)
        db = get_db()
        select_sql = "select * from {}".format(name)
        contents = db.execute(select_sql).fetchall()
        if not contents:
            return {"code": 200, "msg": "blank Database"}
        con_id = []
        for content in contents:
            l = []
            new_l = []
            for item in content[1:]:
                l += jieba.cut_for_search(item)
            for item in l:
                if len(item) > 1:
                    new_l.append(item)
            res = set(new_l)
            for item in res:
                con_id.append((item, content[0]))
        con_id = tuple(con_id)

        if name == "errorlist":
            db.execute("delete from err_index")
            db.executemany("insert into err_index (r_content,r_id) values (?, ?);", con_id)
            db.commit()
        elif name == "qanda":
            db.execute("delete from qanda_index")
            db.executemany("insert into qanda_index (r_content,r_id) values (?, ?);", con_id)
            db.commit()
    if not REBUILD:
        return {"code": 200, "msg": "not allowed"}

    return {"code": 200, "msg": u"done"}


@bp.route("/backup")
def backup():
    for name in ["err", "qa", "ocrmap"]:
        if name == "err":
            name = "errorlist"
        elif name == "qa":
            name = "qanda"
        elif name == "ocrmap":
            name = "ocrmap"
        else:
            return {"code": 200, "msg": "Error Name"}

        if not BACKUP:
            return {"code": 200, "msg": "not allowed"}

        db = get_db()
        select_sql = "select * from {}".format(name)
        contents = db.execute(select_sql).fetchall()
        with open(os.path.join(BACKUP_DIR, "{}.csv".format(name)), "w", newline="") as f:
            writer = csv.writer(f)
            # for item in contents:
            writer.writerows(contents)
    return {"code": 200, "msg": "done"}


@bp.route("/init/<name>")
def init(name):
    if not INIT:
        return {"code": 200, "msg": "not allowed"}
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
        return redirect(url_for("search.homepage"))
    return {"code": 200, "msg": "done"}
