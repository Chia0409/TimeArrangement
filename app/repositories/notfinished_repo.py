from app.db import get_db
from app.repositories.project_repo import name_taken, create_project, get_project


def get_open_notfinished_list(user_id):
    """懸掛天數=0代表start_date就是今天，先天上不算「懸掛」，不顯示。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT nm.notfinished_mission_id, nm.mission_id, nm.start_date, dm.mission_name,
                      DATEDIFF(CURDATE(), nm.start_date) AS pending_days
               FROM notfinished_mission nm
               JOIN daily_mission dm ON dm.mission_id = nm.mission_id
               WHERE nm.user_id = %s AND nm.status = 'open' AND nm.start_date < CURDATE()
               ORDER BY nm.start_date""",
            (user_id,),
        )
        return cur.fetchall()


def get_processed_notfinished_list(user_id, year_month=None, pending_op=None, pending_days=None, status=None):
    sql = """
        SELECT * FROM (
            SELECT nm.notfinished_mission_id, nm.mission_id, nm.status, nm.start_date, nm.finish_date,
                   nm.delayed_reason, nm.closed_reason, dm.mission_name,
                   DATEDIFF(nm.finish_date, nm.start_date) AS pending_days
            FROM notfinished_mission nm
            JOIN daily_mission dm ON dm.mission_id = nm.mission_id
            WHERE nm.user_id = %s AND nm.status <> 'open'
        ) t
        WHERE 1=1
    """
    params = [user_id]

    if year_month:
        sql += " AND DATE_FORMAT(start_date, '%%Y-%%m') = %s"
        params.append(year_month)
    if pending_op in (">", "=", "<") and pending_days is not None:
        sql += f" AND pending_days {pending_op} %s"
        params.append(pending_days)
    if status in ("resolved", "closed", "converted"):
        sql += " AND status = %s"
        params.append(status)

    sql += " ORDER BY finish_date DESC"

    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params)
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


def set_status_resolved(user_id, notfinished_mission_id, delayed_reason):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE notfinished_mission SET status='resolved', finish_date=CURDATE(), delayed_reason=%s
               WHERE notfinished_mission_id=%s AND user_id=%s AND status IN ('open','closed')""",
            (delayed_reason, notfinished_mission_id, user_id),
        )
        if cur.rowcount:
            cur.execute(
                """UPDATE daily_mission dm JOIN notfinished_mission nm ON nm.mission_id = dm.mission_id
                   SET dm.is_finished = 1 WHERE nm.notfinished_mission_id=%s AND dm.user_id=%s""",
                (notfinished_mission_id, user_id),
            )
    db.commit()


def set_status_closed(user_id, notfinished_mission_id, closed_reason):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE notfinished_mission SET status='closed', finish_date=CURDATE(), closed_reason=%s
               WHERE notfinished_mission_id=%s AND user_id=%s AND status IN ('open','resolved')""",
            (closed_reason, notfinished_mission_id, user_id),
        )
        if cur.rowcount:
            cur.execute(
                """UPDATE daily_mission dm JOIN notfinished_mission nm ON nm.mission_id = dm.mission_id
                   SET dm.is_finished = 0 WHERE nm.notfinished_mission_id=%s AND dm.user_id=%s""",
                (notfinished_mission_id, user_id),
            )
    db.commit()


def reopen_notfinished(user_id, notfinished_mission_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE notfinished_mission
               SET status='open', finish_date=NULL, delayed_reason=NULL, closed_reason=NULL
               WHERE notfinished_mission_id=%s AND user_id=%s AND status IN ('resolved','closed')""",
            (notfinished_mission_id, user_id),
        )
        if cur.rowcount:
            cur.execute(
                """UPDATE daily_mission dm JOIN notfinished_mission nm ON nm.mission_id = dm.mission_id
                   SET dm.is_finished = 0 WHERE nm.notfinished_mission_id=%s AND dm.user_id=%s""",
                (notfinished_mission_id, user_id),
            )
    db.commit()


def _apply_conversion(db, user_id, mission_id, notfinished_mission_id, project_id, today):
    with db.cursor() as cur:
        cur.execute(
            "UPDATE daily_mission SET is_long_term=1, project_id=%s WHERE mission_id=%s AND user_id=%s",
            (project_id, mission_id, user_id),
        )
        cur.execute(
            "UPDATE notfinished_mission SET status='converted', finish_date=%s WHERE notfinished_mission_id=%s AND user_id=%s",
            (today, notfinished_mission_id, user_id),
        )
    db.commit()


def convert_to_new_project(user_id, notfinished_mission_id, project_name, today):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT mission_id FROM notfinished_mission
               WHERE notfinished_mission_id=%s AND user_id=%s AND status IN ('open','resolved','closed')""",
            (notfinished_mission_id, user_id),
        )
        row = cur.fetchone()
    if row is None:
        return None, "找不到這筆任務，或已經轉為長期任務"
    if name_taken(user_id, project_name):
        return None, "已經有同名的進行中長期任務了"

    project_id = create_project(user_id, project_name, today)
    _apply_conversion(db, user_id, row["mission_id"], notfinished_mission_id, project_id, today)
    return project_id, None


def convert_to_existing_project(user_id, notfinished_mission_id, project_id, today):
    db = get_db()
    project = get_project(user_id, project_id)
    if project is None:
        return None, "找不到這個長期任務"

    with db.cursor() as cur:
        cur.execute(
            """SELECT mission_id FROM notfinished_mission
               WHERE notfinished_mission_id=%s AND user_id=%s AND status IN ('open','resolved','closed')""",
            (notfinished_mission_id, user_id),
        )
        row = cur.fetchone()
    if row is None:
        return None, "找不到這筆任務，或已經轉為長期任務"

    _apply_conversion(db, user_id, row["mission_id"], notfinished_mission_id, project_id, today)
    return project_id, None
    db.commit()