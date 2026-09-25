from app.db import get_db


def get_user_by_email(email):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM user_info WHERE user_email = %s", (email,))
        return cur.fetchone()


def get_user_by_name(name):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM user_info WHERE user_name = %s", (name,))
        return cur.fetchone()


def get_user_by_id(user_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM user_info WHERE user_id = %s", (user_id,))
        return cur.fetchone()


def create_user(user_name, user_email, password_hash, avatar_path=None):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO user_info (user_name, user_email, password_hash, avatar_path)
               VALUES (%s, %s, %s, %s)""",
            (user_name, user_email, password_hash, avatar_path),
        )
    db.commit()
    return cur.lastrowid


def update_password(user_id, password_hash):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("UPDATE user_info SET password_hash=%s WHERE user_id=%s", (password_hash, user_id))
    db.commit()