from datetime import date
from app.db import get_db


def sync_stage_mission_status(user_id, mission_id):
    """任務狀態有變動時呼叫：只要這個任務目前掛在某個project_stage底下，就同步橋接表；
    沒有project_stage_id(非長期任務)的話，這支函式什麼事都不做。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT project_stage_id, status FROM daily_mission WHERE mission_id=%s AND user_id=%s",
            (mission_id, user_id),
        )
        dm = cur.fetchone()
        if dm is None or dm["project_stage_id"] is None:
            return

        unfinished_id = None
        if dm["status"] == "default":
            new_status = "arrangement"
        elif dm["status"] == "unfinished":
            cur.execute(
                "SELECT unfinished_id FROM unfinished_mission WHERE mission_id=%s AND is_operatable=1",
                (mission_id,),
            )
            row = cur.fetchone()
            unfinished_id = row["unfinished_id"] if row else None
            new_status = "open"
        else:  # 'finished'
            cur.execute(
                "SELECT unfinished_id, status FROM unfinished_mission WHERE mission_id=%s "
                "ORDER BY unfinished_id DESC LIMIT 1",
                (mission_id,),
            )
            row = cur.fetchone()
            if row is None:
                new_status = "resolved"      # 當天就做完，從沒進過unfinished
            else:
                unfinished_id = row["unfinished_id"]
                new_status = row["status"]   # 跟著那筆終點紀錄是resolved還是closed

        cur.execute(
            """INSERT INTO project_stage_mission (project_stage_id, mission_id, unfinished_id, status, is_operatable, update_date)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE
                 unfinished_id=VALUES(unfinished_id), status=VALUES(status),
                 is_operatable=VALUES(is_operatable), update_date=VALUES(update_date)""",
            (dm["project_stage_id"], mission_id, unfinished_id, new_status,
             0 if new_status in ("resolved", "closed") else 1, date.today()),
        )
    db.commit()


def get_assignable_missions(user_id):
    """還沒歸類、且還沒回報過的任務，可以被使用者手動歸進某個專案階段。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT mission_id, mission_name, mission_start_date FROM daily_mission
               WHERE user_id=%s AND project_stage_id IS NULL AND status='default'
               ORDER BY mission_start_date DESC LIMIT 50""",
            (user_id,),
        )
        return cur.fetchall()


def assign_mission_to_stage(user_id, project_stage_id, mission_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE daily_mission SET project_stage_id=%s "
            "WHERE mission_id=%s AND user_id=%s AND project_stage_id IS NULL",
            (project_stage_id, mission_id, user_id),
        )
        if cur.rowcount == 0:
            return False
    db.commit()
    sync_stage_mission_status(user_id, mission_id)
    return True


def get_stage_missions(user_id, project_stage_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT dm.mission_id, dm.mission_name, dm.mission_start_date, dm.mission_finish_date, psm.status
               FROM project_stage_mission psm
               JOIN daily_mission dm ON dm.mission_id = psm.mission_id
               WHERE psm.project_stage_id = %s AND dm.user_id = %s
               ORDER BY dm.mission_start_date DESC""",
            (project_stage_id, user_id),
        )
        return cur.fetchall()