import os
from flask import Flask, redirect, url_for


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='DEV',
        DATABASE=os.path.join(app.instance_path, 'data.sqlite'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return redirect(url_for("search.homepage"))

    from . import db
    db.init_app(app)

    # from . import init_server_db
    # app.register_blueprint(init_server_db.bp)

    from . import search
    app.register_blueprint(search.bp)

    from . import sys_ctrl
    app.register_blueprint(sys_ctrl.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    return app
