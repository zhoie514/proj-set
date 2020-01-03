from flask import (Blueprint, render_template, redirect, url_for, current_app,
                   g, request, make_response)

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/", methods=("get", ))
def homepg():
    if request.method == "GET":
        admin = request.cookies.get('admin', "")
        if admin == "True":
            user = "admin"
        else:
            user = None
        return render_template("admin/admin.html", res=locals())
    return "404"


@bp.route("/login", methods=("post", "get"))
def login():
    if request.method == "GET":
        admin = request.cookies.get('admin', "")
        if admin == "True":
            user = "admin"
        else:
            user = None
        return render_template("admin/admin.html", res=locals())

    if request.method == "POST":
        try:
            uname = request.form['uname']
            upwd = request.form['upwd']
        except Exception as e:
            return {"code": 209, "msg": "字段错误"}

        if uname == "admin" and upwd == "admin":
            g.user = "admin"
        else:
            error="用户名或密码错误"
            return render_template("admin/admin.html",res=locals())
        if "user" in g:
            user = "admin"
        resp = make_response(render_template("admin/admin.html", res=locals()))
        resp.set_cookie('admin', "True", 36000)
        return resp
    return {"code": 210, "msg": "wrong request method"}


@bp.route("/logout")
def logout():
    if request.method == "GET":
        resp = make_response(redirect(url_for("admin.login")))
        if "user" in g:
            g.pop("user")
        resp.set_cookie('admin', 'False')
        return resp
    return "404"


@bp.route("/config", methods=('post', ))
def app_config():
    if request.method == "POST":
        # 尝试获取所有参数
        try:
            rebuild = request.form['rebuild'.upper()]
            backup = request.form['backup'.upper()]
            import_csv = request.form['import_csv'.upper()]
            init = request.form['init'.upper()]
            del_record = request.form['del_record'.upper()]
        except Exception as e:
            # 有任意一个失败则返回错误
            return {"code": 212, "msg": "invalid request parameter."}
        # 参数正常的话进行以下步骤
        config_path = current_app.instance_path + "/config.py"
        contents = []
        with open(config_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if len(line.split("=")) == 2:
                    if line.split("=")[0].strip() == 'rebuild'.upper():
                        new_line = "=".join(
                            [line.split("=")[0], rebuild + "\n"])
                    elif line.split("=")[0].strip() == 'backup'.upper():
                        new_line = "=".join(
                            [line.split("=")[0], backup + "\n"])
                    elif line.split("=")[0].strip() == 'import_csv'.upper():
                        new_line = "=".join(
                            [line.split("=")[0], import_csv + "\n"])
                    elif line.split("=")[0].strip() == 'init'.upper():
                        new_line = "=".join([line.split("=")[0], init + "\n"])
                    elif line.split("=")[0].strip() == 'del_record'.upper():
                        new_line = "=".join(
                            [line.split("=")[0], del_record + "\n"])
                    else:
                        new_line = line
                    contents.append(new_line)
                else:
                    contents.append(line)
        with open(config_path, 'w', encoding="utf-8") as f:
            f.writelines(contents)
            f.flush()
        return redirect(url_for("admin.login"))
    return {"code": 211, "msg": "wrong request method."}
