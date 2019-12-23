import random

from flask import (Blueprint, render_template, request, redirect, url_for)
from flask_cors import cross_origin

from searchclient.db import get_db
from . import init_server_db as initdb

bp = Blueprint("search", __name__, url_prefix="/search")

@bp.route("/", methods=("get",))
def homepage():
    # 随机显示三个项目中的某一个
    kind = random.choice(("errorlist", "ocrmap", "qanda"))
    res = get_eles(kind)
    # res = get_eles(random.choice(("errorlist",)))
    return render_template("search/homepage.html", res=res, kind=kind)


@bp.route("/err", methods=("get", "post"))
def se_err():
    if request.method == "GET":
        kw = request.args.get("kw")
        pg = int(request.args.get("pg", 1))
        db = get_db()
        if not kw:
            kw = ""
            # 没有参数的话,就取所有的 并以20条进行分业
            cur = db.execute('select id from errorlist')
            all_id = cur.fetchall()
            # 取出总条数
            all_num = len(all_id)
            # 算页数
            all_pg = int((all_num + 20 - 1) / 20)
            # 取出指定条数
            cur = db.execute("select *  from errorlist limit {}, 20 ".format((pg - 1) * 20))
            res = cur.fetchall()
        else:
            key_words = kw_deal(kw)
            # 查出每一个关键字对应的主表中的id
            r_id = []
            for key in key_words:
                r_id.append(db.execute("select r_id from err_index where r_content = ?", (key,)).fetchall())
            # 将这些id去重,且保持原id顺序 有可能 r_id中有 None
            tmp = []
            for item in r_id:
                if isinstance(item, (list, tuple)):
                    for i in item:
                        if i not in tmp:
                            tmp.append(i)
            all_pg = int((len(tmp) + 20 - 1) / 20)
            # 取出去重后的tmp 中的有序id 查出对应的所有记录
            res_all = []
            for i in tmp:
                one_record = db.execute("select * from errorlist where id = ?", (i['r_id'],)).fetchone()
                if one_record:
                    res_all.append(one_record)
            # 手动分页 20 条一页
            res = res_all[(pg - 1) * 20:20 * pg]
        return render_template("search/err_page.html", res=res, kw=kw, pg=pg, all_page=all_pg)
    if request.method == "POST":
        e_orign = request.form['orign']
        e_describe = request.form['describe']
        e_interface = request.form['interface']
        e_mask = request.form['mask']
        e_category = request.form['category']
        e_errorinfo = request.form['errorinfo']
        e_logsearch = request.form['logsearch']
        e_procedure = request.form['procedure']

        if (not e_describe) or (not e_category) or (not e_procedure):
            return "必填项为空"
        db = get_db()
        db.execute(
            "insert into errorlist (e_orign,e_describe,e_interface,e_mask,e_category,e_errorinfo,e_logsearch,e_procedure) "
            "values (?,?,?,?,?,?,?,?);",
            (e_orign, e_describe, e_interface, e_mask, e_category, e_errorinfo, e_logsearch, e_procedure))
        db.commit()
        return redirect(url_for("search.se_err"))
    return "Invalid Request Method"


@bp.route("/qa", methods=("get", "post"))
def se_qa():
    if request.method == "GET":
        kw = request.args.get("kw")
        pg = int(request.args.get("pg", 1))
        db = get_db()
        if not kw:
            kw = ""
            # 没有参数的话,就取所有的 并以20条进行分业
            cur = db.execute('select id from qanda')
            all_id = cur.fetchall()
            # 取出总条数
            all_num = len(all_id)
            # 算页数
            all_pg = int((all_num + 20 - 1) / 20)
            # 取出指定条数
            cur = db.execute("select *  from qanda limit {}, 20 ".format((pg - 1) * 20))
            res = cur.fetchall()
        else:
            key_words = kw_deal(kw)
            # 查出每一个关键字对应的主表中的id
            r_id = []
            for key in key_words:
                r_id.append(db.execute("select r_id from qanda_index where r_content = ?", (key,)).fetchall())
            # 将这些id去重 有可能 r_id中有 None
            tmp = set()
            for item in r_id:
                if isinstance(item, (list, tuple)):
                    for i in item:
                        tmp.add(i)

            all_pg = int((len(tmp) + 20 - 1) / 20)
            tmp = list(tmp)
            print("all_pg", all_pg)

            # 取出去重后的tmp 中的id 对应的所有记录
            res_all = []
            for i in tmp:
                one_record = db.execute("select * from qanda where id = ?", (i['r_id'],)).fetchone()
                if one_record:
                    res_all.append(one_record)
            # 手动分页 20 条一页
            res = res_all[(pg - 1) * 20:20 * pg]
        return render_template("search/qa_page.html", res=res, kw=kw, pg=pg, all_page=all_pg)
    if request.method == "POST":
        q_ques = request.form['ques']
        q_ans = request.form['ans']
        if (not q_ques) or (not q_ans):
            return "必填项为空"
        db = get_db()
        db.execute("insert into qanda (q_ques,q_ans) values (?,?)", (q_ques, q_ans))
        db.commit()
        return redirect(url_for("search.se_qa"))
    return "Invalid Request Method"


@bp.route("/ocr-map", methods=("get", "post"))
def se_ocr():
    if request.method == "GET":
        pg = int(request.args.get("pg", 1))
        db = get_db()
        # 取所有的 并以20条进行分业
        cur = db.execute('select id from ocrmap')
        all_id = cur.fetchall()
        # 取出总条数
        all_num = len(all_id)
        # 算页数
        all_pg = int((all_num + 20 - 1) / 20)
        # 取出指定条数
        cur = db.execute("select *  from ocrmap limit {}, 20 ".format((pg - 1) * 20))
        res = cur.fetchall()
        return render_template("search/ocr_page.html", res=res, pg=pg, all_page=all_pg)
    if request.method == "POST":
        o_type = request.form['type']
        o_code = request.form['code']
        o_msg = request.form['msg']
        if (not o_code) or (not o_msg):
            return "必填项为空"
        db = get_db()
        db.execute("insert into ocrmap (o_type,o_code,o_msg) values (?,?,?)", (o_type, o_code, o_msg))
        db.commit()
        return redirect(url_for("search.se_ocr"))
    return "Invalid Request Method"


# 修改及删除
@bp.route("/err/<id>", methods=["get", "POST", "delete"])
@cross_origin()
def ch_err(id):
    try:
        id = int(id)
    except Exception as e:
        return "404"
    if request.method == "GET":
        # 进入修改页面
        db = get_db()
        record = db.execute("select * from errorlist where id = ?", (id,)).fetchall()
        if record:
            res = record
        else:
            return "404 not found"
        return render_template("search/ch_err_page.html", res=res, id=id)
    if request.method == "POST":
        # 提交修改
        id = request.form['id']
        e_describe = request.form['describle']
        e_category = request.form['category']
        e_errorinfo = request.form['errorinfo']
        e_logsearch = request.form['logsearch']
        e_procedure = request.form['procedure']
        sql = "update errorlist set e_describe=?,e_category=?,e_errorinfo=?,e_logsearch=?,e_procedure=? where id=?"
        db = get_db()
        db.execute(sql, (e_describe, e_category, e_errorinfo, e_logsearch, e_procedure, id))
        db.commit()
        return {"status": 200, "msg": "OK"}
    if request.method == "DELETE":
        db = get_db()
        try:
            db.execute("delete from errorlist where id=?", (id,)).fetchone()
            db.commit()
        except Exception as e:
            return {"code": 501, "error": "删除失败,请刷新后重试"}
        return {"code": 200, "msg": "succ"}


@bp.route("/qa/<id>", methods=["get", "POST", "DELete"])
@cross_origin()
def ch_qa(id):
    try:
        id = int(id)
    except Exception as e:
        return "404"
    if request.method == "GET":
        # 进入修改页面
        db = get_db()
        record = db.execute("select * from qanda where id = ?", (id,)).fetchall()
        if record:
            res = record
        else:
            return "404 not found"
        return render_template("search/ch_qa_page.html", res=res, id=id)
    if request.method == "POST":
        # 提交修改
        id = request.form['id']
        q_ques = request.form['ques']
        q_ans = request.form['ans']
        sql = "update qanda set q_ques=?,q_ans=? where id=?"
        db = get_db()
        db.execute(sql, (q_ques, q_ans, id))
        db.commit()
        return redirect(url_for("search.ch_qa", id=id))
    if request.method == "DELETE":
        db = get_db()
        try:
            db.execute("delete from qanda where id=?", (id,)).fetchone()
            db.commit()
        except Exception as e:
            return {"code": 501, "error": "删除失败,请刷新后重试"}
        return {"code": 200, "msg": "succ"}


@bp.route("/ocr-map/<id>", methods=["DELete"])
@cross_origin()
def ch_ocr(id):
    try:
        id = int(id)
    except Exception as e:
        return "404"
    if request.method == "DELETE":
        db = get_db()
        try:
            db.execute("delete from ocrmap where id=?", (id,)).fetchone()
            db.commit()
        except Exception as e:
            return {"code": 501, "error": "删除失败,请刷新后重试"}
        return {"code": 200, "msg": "succ"}


# 删除


# utils
def get_eles(tb_name: str):
    # 随机取不大于20条记录进行显示
    db = get_db()
    cur = db.execute('select id from {}'.format(tb_name))
    all_id = set(cur.fetchall())
    id_lst = []
    try:
        for i in range(20):
            id_lst.append(all_id.pop()['id'], )
    except Exception as e:
        pass
    res = []
    for item in id_lst:
        cur = db.execute("select * from {} where id ={}".format(tb_name, item))
        res += cur.fetchall()
    db.close()
    return res


def kw_deal(kw: str) -> list:
    lst = []
    # 首先按空格分,并排一次序,长度长的在前面
    for item in kw.split():
        lst.append(item)
    # 将 kw 利用jieba分词进行处理 处理成 [a,b,c,]"的形式,
    lst2 = []
    for item in initdb.cut_kw(kw):
        if len(item) > 1:
            lst2.append(item)
    for item in lst2:
        lst.append(item)
    lst = set(lst)
    lst = list(lst)
    lst.sort(key=lambda i: len(i), reverse=True)

    print(lst)
    return lst
