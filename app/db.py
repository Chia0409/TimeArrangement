import pymysql
from pymysql.cursors import DictCursor
from flask import g, current_app


def get_db():
    """取得這次request專屬的資料庫連線；同一個request裡重複呼叫會拿到同一條，不會一直開新連線。"""
    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config["DB_HOST"],
            port=current_app.config["DB_PORT"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"],
            cursorclass=DictCursor,   # 讓查詢結果變成 {"欄位名":值} 的字典，比預設的tuple好用
            autocommit=False,
        )
    return g.db


def close_db(e=None):
    """request處理完自動被呼叫，負責關掉連線，避免連線越開越多沒人關。"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """在 create_app() 裡呼叫一次，告訴Flask：每次request結束時記得執行 close_db。"""
    app.teardown_appcontext(close_db)