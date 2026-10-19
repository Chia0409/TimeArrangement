from datetime import date, timedelta
from app.db import get_db
from app.repositories.stage_mission_repo import sync_stage_mission_status


def _recalc_project_estimate(cur, project_id):
    cur.execute(
        "SELECT COUNT(*) AS n, COALESCE(SUM(estimate_days),0) AS total FROM project_stage "
        "WHERE project_id=%s AND status='ongoing'",
        (project_id,),
    )
    row = cur.fetchone()
    cur.execute("SELECT start_date FROM project WHERE project_id=%s", (project_id,))
    start_date = cur.fetchone()["start_date"]
    total_days = int(row["total"])
    finish_date = start_date + timedelta(days=total_days - 1) if total_days else None
    cur.execute(
        "UPDATE project SET stage_amount=%s, estimate_days=%s, estimated_finish_date=%s WHERE project_id=%s",
        (row["n"], total_days or None, finish_date, project_id),
    )


def create_project_with_stages(user_id, project_name, category, start_date, stages):
    """stages是 [{"stage_name":..., "estimate_days":...}, ...]，依序排，
    每一期接續上一期結束日的隔天開始。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO project (user_id, project_name, category, start_date, status) VALUES (%s,%s,%s,%s,'ongoing')",
            (user_id, project_name, category, start_date),
        )
        project_id = cur.lastrowid

        cursor_date = start_date
        for i, s in enumerate(stages, start=1):
            days = int(s["estimate_days"])
            cur.execute(
                """INSERT INTO project_stage
                   (project_id, user_id, stage_no, stage_name, estimate_days, start_date, estimated_finish_date, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,'ongoing')""",
                (project_id, user_id, i, s["stage_name"], days, cursor_date,
                 cursor_date + timedelta(days=days - 1)),
            )
            cursor_date = cursor_date + timedelta(days=days)

        _recalc_project_estimate(cur, project_id)
    db.commit()
    return project_id


def get_projects_overview(user_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT p.*,
                      COUNT(dm.mission_id) AS mission_count,
                      COALESCE(SUM(dm.actual_hours),0) AS total_hours,
                      COALESCE(SUM(dm.status='finished'),0) AS finished_count,
                      COALESCE(SUM(dm.status='unfinished'),0) AS unfinished_count,
                      COALESCE(SUM(dm.is_auto_closed=1),0) AS forgot_count
               FROM project p
               LEFT JOIN project_stage ps ON ps.project_id = p.project_id
               LEFT JOIN daily_mission dm ON dm.project_stage_id = ps.project_stage_id
               WHERE p.user_id = %s
               GROUP BY p.project_id
               ORDER BY p.status, p.start_date DESC""",
            (user_id,),
        )
        return cur.fetchall()


def get_project(user_id, project_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM project WHERE project_id=%s AND user_id=%s", (project_id, user_id))
        return cur.fetchone()


def get_project_stages(user_id, project_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT ps.*,
                      COUNT(dm.mission_id) AS mission_count,
                      COALESCE(SUM(dm.status='finished'),0) AS finished_count,
                      COALESCE(SUM(dm.status='unfinished'),0) AS unfinished_count
               FROM project_stage ps
               LEFT JOIN daily_mission dm ON dm.project_stage_id = ps.project_stage_id
               WHERE ps.project_id=%s AND ps.user_id=%s
               GROUP BY ps.project_stage_id
               ORDER BY ps.stage_no""",
            (project_id, user_id),
        )
        return cur.fetchall()


def add_stage(user_id, project_id, stage_name, estimate_days):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(MAX(stage_no),0)+1 AS next_no, "
            "COALESCE(MAX(estimated_finish_date), (SELECT start_date FROM project WHERE project_id=%s) - INTERVAL 1 DAY) AS last_end "
            "FROM project_stage WHERE project_id=%s",
            (project_id, project_id),
        )
        row = cur.fetchone()
        start_date = row["last_end"] + timedelta(days=1)
        days = int(estimate_days)
        cur.execute(
            """INSERT INTO project_stage
               (project_id, user_id, stage_no, stage_name, estimate_days, start_date, estimated_finish_date, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,'ongoing')""",
            (project_id, user_id, row["next_no"], stage_name, days,
             start_date, start_date + timedelta(days=days - 1)),
        )
        _recalc_project_estimate(cur, project_id)
    db.commit()


def _cascade_close_missions(cur, project_stage_id, user_id, reason):
    """stage/project被關閉時，批次把底下還沒結案的任務收尾——
    直接寫SQL而不是逐筆呼叫unfinished_repo的單筆函式，因為這是批次操作，
    理由固定、不需要逐筆走『必填驗證』那一套。"""
    cur.execute(
        "SELECT mission_id FROM daily_mission WHERE project_stage_id=%s AND user_id=%s AND status IN ('default','unfinished')",
        (project_stage_id, user_id),
    )
    mission_ids = [r["mission_id"] for r in cur.fetchall()]
    if not mission_ids:
        return mission_ids

    cur.execute(
        "UPDATE daily_mission SET status='finished', mission_finish_date=CURDATE(), is_ONTime_finished=0 "
        "WHERE project_stage_id=%s AND user_id=%s AND status IN ('default','unfinished')",
        (project_stage_id, user_id),
    )
    cur.execute(
        "UPDATE unfinished_mission SET status='closed', is_operatable=0, closed_reason=%s "
        "WHERE mission_id IN %s AND is_operatable=1",
        (reason, tuple(mission_ids)),
    )
    return mission_ids


def resolve_stage(user_id, project_id, project_stage_id, delay_reason):
    if not delay_reason:
        return False, "請填寫延遲原因"
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS n FROM daily_mission WHERE project_stage_id=%s AND user_id=%s AND status<>'finished'",
            (project_stage_id, user_id),
        )
        if cur.fetchone()["n"] > 0:
            return False, "這個階段底下還有任務尚未完成，無法標記完成"

        cur.execute("SELECT estimated_finish_date FROM project_stage WHERE project_stage_id=%s", (project_stage_id,))
        est = cur.fetchone()["estimated_finish_date"]
        on_time = 1 if (est is None or date.today() <= est) else 0

        cur.execute(
            "UPDATE project_stage SET status='resolved', actual_finish_date=CURDATE(), "
            "is_ONTime_finished=%s, delay_reason=%s WHERE project_stage_id=%s",
            (on_time, delay_reason, project_stage_id),
        )
        _recalc_project_estimate(cur, project_id)
    db.commit()
    return True, None


def close_stage(user_id, project_id, project_stage_id, closed_reason):
    if not closed_reason:
        return False, "請填寫結束原因"
    db = get_db()
    with db.cursor() as cur:
        affected = _cascade_close_missions(cur, project_stage_id, user_id, "專案階段任務關閉")
        cur.execute(
            "UPDATE project_stage SET status='stopped', actual_finish_date=CURDATE(), closed_reason=%s WHERE project_stage_id=%s",
            (closed_reason, project_stage_id),
        )
        _recalc_project_estimate(cur, project_id)
    db.commit()
    for mid in affected:
        sync_stage_mission_status(user_id, mid)
    return True, None


def resolve_project(user_id, project_id, delay_reason):
    if not delay_reason:
        return False, "請填寫延遲原因"
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM project_stage WHERE project_id=%s AND status='ongoing'", (project_id,))
        if cur.fetchone()["n"] > 0:
            return False, "還有專案階段任務仍在進行中，無法標記完成"

        cur.execute("SELECT estimated_finish_date FROM project WHERE project_id=%s", (project_id,))
        est = cur.fetchone()["estimated_finish_date"]
        on_time = 1 if (est is None or date.today() <= est) else 0

        cur.execute(
            "UPDATE project SET status='resolved', actual_finish_date=CURDATE(), is_ONTime_finished=%s, delay_reason=%s WHERE project_id=%s",
            (on_time, delay_reason, project_id),
        )
    db.commit()
    return True, None


def close_project(user_id, project_id, closed_reason):
    if not closed_reason:
        return False, "請填寫結束原因"
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT project_stage_id FROM project_stage WHERE project_id=%s AND status='ongoing'", (project_id,))
        stage_ids = [r["project_stage_id"] for r in cur.fetchall()]

        all_affected = []
        for sid in stage_ids:
            all_affected += _cascade_close_missions(cur, sid, user_id, "專案關閉")
        if stage_ids:
            cur.execute(
                "UPDATE project_stage SET status='stopped', actual_finish_date=CURDATE(), closed_reason='專案關閉' "
                "WHERE project_stage_id IN %s", (tuple(stage_ids),),
            )
        cur.execute(
            "UPDATE project SET status='stopped', actual_finish_date=CURDATE(), closed_reason=%s WHERE project_id=%s",
            (closed_reason, project_id),
        )
    db.commit()
    for mid in all_affected:
        sync_stage_mission_status(user_id, mid)
    return True, None

def get_ongoing_projects(user_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT project_id, project_name FROM project WHERE user_id=%s AND status='ongoing' ORDER BY project_name",
            (user_id,),
        )
        return cur.fetchall()


def get_ongoing_stages(user_id, project_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT project_stage_id, stage_name FROM project_stage WHERE project_id=%s AND user_id=%s AND status='ongoing' ORDER BY stage_no",
            (project_id, user_id),
        )
        return cur.fetchall()