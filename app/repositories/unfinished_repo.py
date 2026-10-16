from app.db import get_db
from app.repositories.mission_repo import finish_mission_from_unfinished, close_mission_from_unfinished
from app.repositories.stage_mission_repo import sync_stage_mission_status

def create_chains_for_newly_unfinished(user_id):
    """幫『剛被標成unfinished、但還沒有任何追蹤紀錄』的任務，各自建立第一筆。
    update_date用mission_start_date，代表『從它原本該執行的那天就開始追蹤』；
    NOT EXISTS確保每個任務一輩子只會經過這支函式一次，之後的版本都是靠匯入續接，不會重複跑到這裡。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO unfinished_mission (user_id, mission_id, status, is_operatable, sequence_exit, update_date)
               SELECT dm.user_id, dm.mission_id, 'open', 1, 0, dm.mission_start_date
               FROM daily_mission dm
               WHERE dm.user_id = %s AND dm.status = 'unfinished'
                 AND NOT EXISTS (SELECT 1 FROM unfinished_mission um WHERE um.mission_id = dm.mission_id)""",
            (user_id,),
        )
    db.commit()


def get_open_unfinished_missions(user_id):
    """撈『目前活著、可被操作』的未完成任務，給「預計執行任務」頁面的匯入清單用。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT um.unfinished_id, um.mission_id, um.update_date, dm.mission_name
               FROM unfinished_mission um
               JOIN daily_mission dm ON dm.mission_id = um.mission_id
               WHERE um.user_id = %s AND um.status = 'open' AND um.is_operatable = 1 AND dm.project_stage_id IS NULL
               ORDER BY um.update_date""",
            (user_id,),
        )
        return cur.fetchall()


def _get_current_open(cur, user_id, mission_id):
    cur.execute(
        """SELECT unfinished_id FROM unfinished_mission
           WHERE user_id=%s AND mission_id=%s AND status='open' AND is_operatable=1""",
        (user_id, mission_id),
    )
    return cur.fetchone()


def import_continue(user_id, mission_id, today, start_time, end_time, actual_hours):
    """匯入後『依然未完成』：目前活著的那一筆退場(is_operatable→0, sequence_exit→1)，
    新增下一個版本接續(follower_id指回剛剛退場的那一筆)。"""
    db = get_db()
    with db.cursor() as cur:
        current = _get_current_open(cur, user_id, mission_id)
        if current is None:
            return False
        cur.execute(
            "UPDATE unfinished_mission SET is_operatable=0, sequence_exit=1 WHERE unfinished_id=%s",
            (current["unfinished_id"],),
        )
        cur.execute(
            """INSERT INTO unfinished_mission
               (user_id, mission_id, status, is_operatable, sequence_exit, follower_id,
                update_date, start_time, end_time, actual_hours)
               VALUES (%s, %s, 'open', 1, 0, %s, %s, %s, %s, %s)""",
            (user_id, mission_id, current["unfinished_id"], today, start_time, end_time, actual_hours),
        )
    db.commit()
    sync_stage_mission_status(user_id, mission_id)
    return True


def import_resolve(user_id, mission_id, today, start_time, end_time, actual_hours, delay_reason):
    """匯入後『已完成』：退場目前這筆、新增一筆終點紀錄(resolved)，並連動daily_mission。
    delay_reason是你確認過的『必填』規則，這裡擋在最前面，不合規則連資料庫都不碰。"""
    if not delay_reason:
        return False, "請填寫延遲原因"

    db = get_db()
    with db.cursor() as cur:
        current = _get_current_open(cur, user_id, mission_id)
        if current is None:
            return False, "找不到這筆未完成任務的追蹤紀錄"
        cur.execute(
            "UPDATE unfinished_mission SET is_operatable=0, sequence_exit=1 WHERE unfinished_id=%s",
            (current["unfinished_id"],),
        )
        cur.execute(
            """INSERT INTO unfinished_mission
               (user_id, mission_id, status, is_operatable, sequence_exit, follower_id,
                update_date, start_time, end_time, actual_hours, delay_reason)
               VALUES (%s, %s, 'resolved', 0, 0, %s, %s, %s, %s, %s, %s)""",
            (user_id, mission_id, current["unfinished_id"], today, start_time, end_time, actual_hours, delay_reason),
        )
    db.commit()
    finish_mission_from_unfinished(user_id, mission_id, start_time, end_time, actual_hours)
    sync_stage_mission_status(user_id, mission_id)
    return True, None

def get_open_unfinished_list(user_id):
    """未完成任務管理頁用：比plan.html的匯入清單多算一個『懸掛天數』。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT um.unfinished_id, um.mission_id, um.update_date, dm.mission_name,
                      DATEDIFF(CURDATE(), um.update_date) AS pending_days
               FROM unfinished_mission um
               JOIN daily_mission dm ON dm.mission_id = um.mission_id
               WHERE um.user_id = %s AND um.status = 'open' AND um.is_operatable = 1 AND dm.project_stage_id IS NULL
               ORDER BY um.update_date""",
            (user_id,),
        )
        return cur.fetchall()


def close_unfinished(user_id, mission_id, today, closed_reason):
    """強制結束：退場目前活著的那一筆，新增一筆closed終點紀錄，連動daily_mission。
    closed_reason必填——這是你確認過的規則，在資料庫真的被改動之前就先擋下來。"""
    if not closed_reason:
        return False, "請填寫結束原因"

    db = get_db()
    with db.cursor() as cur:
        current = _get_current_open(cur, user_id, mission_id)
        if current is None:
            return False, "找不到這筆未完成任務的追蹤紀錄"
        cur.execute(
            "UPDATE unfinished_mission SET is_operatable=0, sequence_exit=1 WHERE unfinished_id=%s",
            (current["unfinished_id"],),
        )
        cur.execute(
            """INSERT INTO unfinished_mission
               (user_id, mission_id, status, is_operatable, sequence_exit, follower_id, update_date, closed_reason)
               VALUES (%s, %s, 'closed', 0, 0, %s, %s, %s)""",
            (user_id, mission_id, current["unfinished_id"], today, closed_reason),
        )
    db.commit()
    sync_stage_mission_status(user_id, mission_id)
    close_mission_from_unfinished(user_id, mission_id, today)
    return True, None
