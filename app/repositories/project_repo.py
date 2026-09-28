from app.db import get_db


def get_unfinished_projects(user_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT project_id, project_name FROM project
               WHERE user_id = %s AND is_finished = 0
               ORDER BY project_name""",
            (user_id,),
        )
        return cur.fetchall()


def get_project(user_id, project_id):
    """確認這個project_id真的屬於這位使用者，防止有人偷塞別人的專案id。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT project_id, project_name FROM project WHERE project_id = %s AND user_id = %s",
            (project_id, user_id),
        )
        return cur.fetchone()


def get_or_create_project(user_id, project_name, start_date):
    """同名的未完成長期任務已存在就直接沿用，避免重複輸入造成兩筆一樣的專案。
    回傳 (專案dict, 是否為新建立)。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT project_id, project_name FROM project "
            "WHERE user_id = %s AND project_name = %s AND is_finished = 0",
            (user_id, project_name),
        )
        existing = cur.fetchone()
        if existing:
            return existing, False

        cur.execute(
            "INSERT INTO project (user_id, project_name, start_date, is_finished) VALUES (%s, %s, %s, 0)",
            (user_id, project_name, start_date),
        )
        new_id = cur.lastrowid
    db.commit()
    return {"project_id": new_id, "project_name": project_name}, True