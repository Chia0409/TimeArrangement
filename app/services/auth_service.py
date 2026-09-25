from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(raw_password):
    """把明文密碼變成雜湊值，存進資料庫的是這個回傳值，不是raw_password本身。"""
    return generate_password_hash(raw_password)


def verify_password(raw_password, password_hash):
    """登入時用這個比對：把使用者剛打的明文密碼，雜湊後跟資料庫存的雜湊值比對是否相符。"""
    return check_password_hash(password_hash, raw_password)


def login_required(view_func):
    """裝飾器：把它加在任何路由函式上方，沒登入的人存取那個網址會被自動導去登入頁。"""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapped
