import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


# g  是一个特殊对象，独立于每一个请求。在处理请求过程中，它可以用于储存 可能多个函数都会用到的数据
# current_app 是另一个特殊对象，该对象指向处理请求的 Flask 应用。
# sqlite3.Row 告诉连接返回类似于字典的行，这样可以通过列名称来操作 数据。
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("buildDatabase.sql") as f:
        db.executescript(f.read().decode("utf8"))


# 注册一个 init-db的命令, 并将其与 app 关联 以实现  flaskapp init-db
@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("初始化sqlite数据库...\r\n Done....")


def init_app(application):
    application.teardown_appcontext(close_db)
    application.cli.add_command(init_db_command)
