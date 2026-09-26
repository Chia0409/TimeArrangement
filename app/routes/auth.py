import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from pymysql.err import IntegrityError

from app.services.auth_service import hash_password, verify_password, login_required
from app.repositories.user_repo import (
    get_user_by_email, get_user_by_name, get_user_by_id, create_user, update_password, update_user_profile,
)

auth_bp = Blueprint("auth", __name__)
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["user_name"]
        password = request.form["password"]
        user = get_user_by_name(name)

        if user and verify_password(password, user["password_hash"]):
            session["user_id"] = user["user_id"]
            return redirect(url_for("home.index"))

        flash("名稱或密碼錯誤")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["user_name"]
        email = request.form["user_email"]
        password = request.form["password"]

        avatar_path = None
        file = request.files.get("avatar")
        if file and file.filename and _allowed_file(file.filename):
            filename = secure_filename(f"{name}_{file.filename}")
            upload_dir = os.path.join(current_app.root_path, "static", "uploads", "avatars")
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            avatar_path = f"uploads/avatars/{filename}"

        user_id = create_user(name, email, hash_password(password), avatar_path)
        session["user_id"] = user_id
        return redirect(url_for("home.index"))

    return render_template("register.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        name = request.form["user_name"]
        email = request.form["user_email"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("兩次輸入的密碼不一致")
            return render_template("forgot_password.html")

        user = get_user_by_email(email)
        if user and user["user_name"] == name:
            update_password(user["user_id"], hash_password(new_password))
            flash("密碼已更新，請重新登入")
            return redirect(url_for("auth.login"))

        flash("查無此帳號")
        return render_template("forgot_password.html", suggest_register=True)

    return render_template("forgot_password.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    user = get_user_by_id(user_id)

    if request.method == "POST":
        new_name = request.form["user_name"]
        new_email = request.form["user_email"]
        avatar_path = user["avatar_path"]  # 沒上傳新圖片就沿用原本的路徑

        file = request.files.get("avatar")
        if file and file.filename and _allowed_file(file.filename):
            filename = secure_filename(f"{new_name}_{file.filename}")
            upload_dir = os.path.join(current_app.root_path, "static", "uploads", "avatars")
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))

            # 有換新圖片的話，把舊檔案刪掉，避免資料夾裡累積一堆用不到的舊圖
            if user["avatar_path"]:
                old_file = os.path.join(current_app.root_path, "static", user["avatar_path"])
                if os.path.exists(old_file):
                    os.remove(old_file)

            avatar_path = f"uploads/avatars/{filename}"

        try:
            update_user_profile(user_id, new_name, new_email, avatar_path)
            flash("個人資料已更新！")
            return redirect(url_for("auth.profile"))
        except IntegrityError:
            flash("這個名稱或Email已經被其他帳號使用了")
            return render_template("profile.html", user=user)

    return render_template("profile.html", user=user)