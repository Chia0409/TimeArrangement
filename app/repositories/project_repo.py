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

def get_projects_with_stats(user_id):
    """一次撈出所有長期任務，加上每個專案的累計統計。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT p.project_id, p.project_name, p.start_date, p.finish_date, p.is_finished,
                      COUNT(dm.mission_id)                                        AS record_count,
                      COALESCE(SUM(dm.actual_hours), 0)                           AS total_hours,
                      COALESCE(SUM(dm.is_finished = 1), 0)                        AS done_count,
                      COALESCE(SUM(dm.is_finished = 0 AND dm.is_auto_closed = 0), 0) AS undone_count,
                      COALESCE(SUM(dm.is_auto_closed = 1), 0)                     AS forgot_count
               FROM project p
               LEFT JOIN daily_mission dm
                      ON dm.project_id = p.project_id AND dm.user_id = p.user_id
               WHERE p.user_id = %s
               GROUP BY p.project_id, p.project_name, p.start_date, p.finish_date, p.is_finished
               ORDER BY p.is_finished, p.start_date DESC, p.project_id DESC""",
            (user_id,),
        )
        return cur.fetchall()


def name_taken(user_id, project_name, exclude_id=None):
    """這個人「進行中」的長期任務裡，有沒有同名的。
    exclude_id用來排除自己：專案id從1開始，傳0(None時)就等於誰都不排除。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT 1 FROM project
               WHERE user_id = %s AND project_name = %s AND is_finished = 0
                 AND project_id <> %s
               LIMIT 1""",
            (user_id, project_name, exclude_id or 0),
        )
        return cur.fetchone() is not None


def create_project(user_id, project_name, start_date):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO project (user_id, project_name, start_date, is_finished) VALUES (%s, %s, %s, 0)",
            (user_id, project_name, start_date),
        )
        new_id = cur.lastrowid
    db.commit()
    return new_id


def rename_project(user_id, project_id, project_name):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE project SET project_name = %s WHERE project_id = %s AND user_id = %s",
            (project_name, project_id, user_id),
        )
    db.commit()


def set_project_finished(user_id, project_id, finished, today):
    """完成時記下完成日；重新開啟時把完成日清空。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE project SET is_finished = %s, finish_date = %s WHERE project_id = %s AND user_id = %s",
            (1 if finished else 0, today if finished else None, project_id, user_id),
        )
    db.commit()


def count_project_missions(user_id, project_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS n FROM daily_mission WHERE project_id = %s AND user_id = %s",
            (project_id, user_id),
        )
        return cur.fetchone()["n"]


def delete_project(user_id, project_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM project WHERE project_id = %s AND user_id = %s", (project_id, user_id))
    db.commit()