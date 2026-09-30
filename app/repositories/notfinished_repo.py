from app.db import get_db
from app.repositories.project_repo import name_taken, create_project


def get_notfinished_list(user_id):
    """依user_id撈所有追蹤紀錄，pending_days查詢當下現算，不存在資料庫裡。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT nm.*, dm.mission_name,
                      DATEDIFF(COALESCE(nm.finish_date, CURDATE()), nm.start_date) AS pending_days
               FROM notfinished_mission nm
               JOIN daily_mission dm ON dm.mission_id = nm.mission_id
               WHERE nm.user_id = %s
               ORDER BY nm.status, nm.start_date""",
            (user_id,),
        )
        return cur.fetchall()


def track_mission_status(user_id, mission_id, mission_date, is_finished):
    """依這次回報的完成狀態，同步notfinished_mission的追蹤紀錄：
       is_finished=0 且這筆任務還沒建立過追蹤紀錄 → 新增一筆，並把id串回daily_mission
       is_finished=1 且這筆任務曾經被追蹤過        → 把那筆追蹤紀錄標記為resolved
       兩種情況都用SQL的條件式一次處理，不用先查再判斷，減少來回資料庫的次數。"""
    db = get_db()
    with db.cursor() as cur:
        if is_finished == 0:
            cur.execute(
                """INSERT INTO notfinished_mission (user_id, mission_id, status, start_date)
                   SELECT %s, %s, 'open', %s
                   WHERE NOT EXISTS (
                       SELECT 1 FROM daily_mission
                       WHERE mission_id = %s AND notfinished_mission_id IS NOT NULL
                   )""",
                (user_id, mission_id, mission_date, mission_id),
            )
            cur.execute(
                """UPDATE daily_mission dm
                   JOIN notfinished_mission nm ON nm.mission_id = dm.mission_id
                   SET dm.notfinished_mission_id = nm.notfinished_mission_id
                   WHERE dm.mission_id = %s AND dm.notfinished_mission_id IS NULL""",
                (mission_id,),
            )
        elif is_finished == 1:
            cur.execute(
                """UPDATE notfinished_mission nm
                   JOIN daily_mission dm ON dm.notfinished_mission_id = nm.notfinished_mission_id
                   SET nm.status = 'resolved', nm.finish_date = CURDATE()
                   WHERE dm.mission_id = %s AND dm.user_id = %s""",
                (mission_id, user_id),
            )
    db.commit()

def get_open_notfinished_list(user_id):
    """只列status='open'的，懸掛天數用DATEDIFF現算(這些都還沒finish_date，直接跟CURDATE()比)。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT nm.notfinished_mission_id, nm.mission_id, nm.start_date, dm.mission_name,
                      DATEDIFF(CURDATE(), nm.start_date) AS pending_days
               FROM notfinished_mission nm
               JOIN daily_mission dm ON dm.mission_id = nm.mission_id
               WHERE nm.user_id = %s AND nm.status = 'open'
               ORDER BY nm.start_date""",
            (user_id,),
        )
        return cur.fetchall()


def resolve_notfinished(user_id, notfinished_mission_id, delayed_reason):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE notfinished_mission
               SET status = 'resolved', finish_date = CURDATE(), delayed_reason = %s
               WHERE notfinished_mission_id = %s AND user_id = %s AND status = 'open'""",
            (delayed_reason, notfinished_mission_id, user_id),
        )
        if cur.rowcount:  # 真的有改到才需要連動，避免重複點擊時多做一次沒意義的UPDATE
            cur.execute(
                """UPDATE daily_mission dm
                   JOIN notfinished_mission nm ON nm.mission_id = dm.mission_id
                   SET dm.is_finished = 1
                   WHERE nm.notfinished_mission_id = %s AND dm.user_id = %s""",
                (notfinished_mission_id, user_id),
            )
    db.commit()


def close_notfinished(user_id, notfinished_mission_id, closed_reason):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE notfinished_mission
               SET status = 'closed', finish_date = CURDATE(), closed_reason = %s
               WHERE notfinished_mission_id = %s AND user_id = %s AND status = 'open'""",
            (closed_reason, notfinished_mission_id, user_id),
        )
    db.commit()


def convert_to_long_term(user_id, notfinished_mission_id, project_name, today):
    """回傳 (project_id, error)：成功時error是None，失敗時project_id是None。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT mission_id FROM notfinished_mission
               WHERE notfinished_mission_id = %s AND user_id = %s AND status = 'open'""",
            (notfinished_mission_id, user_id),
        )
        row = cur.fetchone()

    if row is None:
        return None, "找不到這筆未完成任務，或已經被處理過了"
    if name_taken(user_id, project_name):
        return None, "已經有同名的進行中長期任務了"

    project_id = create_project(user_id, project_name, today)

    with db.cursor() as cur:
        cur.execute(
            "UPDATE daily_mission SET is_long_term = 1, project_id = %s WHERE mission_id = %s AND user_id = %s",
            (project_id, row["mission_id"], user_id),
        )
        cur.execute(
            "UPDATE notfinished_mission SET status = 'converted', finish_date = %s WHERE notfinished_mission_id = %s AND user_id = %s",
            (today, notfinished_mission_id, user_id),
        )
    db.commit()
    return project_id, None