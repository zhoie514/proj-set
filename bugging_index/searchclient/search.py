from flask import (Blueprint, render_template, request, redirect, url_for)
from searchclient.db import get_db
import jieba

bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/test")
def tt():
    #  一个测试请求的函数
    db = get_db()
    res = [1, 2]
    return render_template("base.html")


@bp.route("/", methods=("get",))
def homepage():
    # 随机显示三个项目中的某一个,随机显示条数
    res = error_list_random()
    return render_template("search/homepage.html", res=res)


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
        if kw:
            key_words = kw_deal(kw)
            # 查出每一个关键字对应的主表中的id
            r_id = []
            for key in key_words:
                r_id.append(db.execute("select r_id from err_index where r_content = ?", (key,)).fetchall())
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
        if kw:
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
@bp.route("/err/<id>", methods=["get", "pOST", "del"])
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


@bp.route("/qa/<id>", methods=["get", "POST", "DEL"])
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


# utils
def error_list_random():
    # 随机取不大于20条记录进行显示
    db = get_db()
    cur = db.execute('select id from errorlist')
    all_id = set(cur.fetchall())
    id_lst = []
    try:
        for i in range(20):
            id_lst.append(all_id.pop()['id'], )
    except Exception as e:
        pass
    res = []
    for item in id_lst:
        cur = db.execute("select * from errorlist where id ={}".format(item))
        res += cur.fetchall()
    db.close()
    return res


def kw_deal(kw: str) -> list:
    # 将 kw 利用jieba分词进行处理 处理成 [a,b,c,]"的形式,
    from instance import config
    with open(config.DEL_WORDS, 'r', encoding="utf8") as f:
        del_words = f.read()
    jieba.del_word(del_words)
    lst = []
    for item in jieba.cut_for_search(kw):
        if len(item) > 1:
            lst.append(item)
    return lst
