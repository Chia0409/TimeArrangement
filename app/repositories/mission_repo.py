from app.db import get_db


def get_missions_by_date(user_id, mission_date):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT * FROM daily_mission
               WHERE user_id = %s AND mission_date = %s
               ORDER BY mission_no, segment_no""",
            (user_id, mission_date),
        )
        return cur.fetchall()


def get_missions_in_range(user_id, start_date, end_date):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT * FROM daily_mission
               WHERE user_id = %s AND mission_date BETWEEN %s AND %s
               ORDER BY mission_date, mission_no, segment_no""",
            (user_id, start_date, end_date),
        )
        return cur.fetchall()


def get_next_mission_no(user_id, mission_date):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT COALESCE(MAX(mission_no), 0) + 1 AS next_no
               FROM daily_mission WHERE user_id = %s AND mission_date = %s""",
            (user_id, mission_date),
        )
        return cur.fetchone()["next_no"]


def insert_mission(data: dict):
    """data字典裡要包含user_id這個key，呼叫端(routes)要記得放進去。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO daily_mission
               (user_id, mission_date, mission_no, segment_no, mission_name, estimated_hours,
                start_time, end_time, actual_hours, is_finished, is_long_term, is_added,
                project_id, notfinished_mission_id)
               VALUES (%(user_id)s, %(mission_date)s, %(mission_no)s, %(segment_no)s, %(mission_name)s,
                       %(estimated_hours)s, %(start_time)s, %(end_time)s, %(actual_hours)s,
                       %(is_finished)s, %(is_long_term)s, %(is_added)s,
                       %(project_id)s, %(notfinished_mission_id)s)""",
            data,
        )
    db.commit()
    return cur.lastrowid


def update_mission_summary(user_id, mission_id, start_time, end_time, actual_hours, is_finished):
    """WHERE多加user_id=%s：就算有人硬改網址URL裡的mission_id想改別人的資料，也會因為user_id對不上而改到0筆。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE daily_mission
               SET start_time=%s, end_time=%s, actual_hours=%s, is_finished=%s
               WHERE mission_id=%s AND user_id=%s""",
            (start_time, end_time, actual_hours, is_finished, mission_id, user_id),
        )
    db.commit()


def delete_mission(user_id, mission_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM daily_mission WHERE mission_id=%s AND user_id=%s", (mission_id, user_id))
    db.commit()