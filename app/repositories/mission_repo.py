from app.db import get_db


def get_missions_by_date(mission_date):
    """撈某一天所有任務(含拆分時段、含追加任務)，依編號與時段排序。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT * FROM daily_mission
               WHERE mission_date = %s
               ORDER BY mission_no, segment_no""",
            (mission_date,),
        )
        return cur.fetchall()


def get_missions_in_range(start_date, end_date):
    """撈一段日期範圍的任務，首頁「當週7天」表格會用到這個。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT * FROM daily_mission
               WHERE mission_date BETWEEN %s AND %s
               ORDER BY mission_date, mission_no, segment_no""",
            (start_date, end_date),
        )
        return cur.fetchall()


def insert_mission(data: dict):
    """新增一筆任務，data的key要對應資料表欄位名稱。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO daily_mission
               (mission_date, mission_no, segment_no, mission_name, estimated_hours,
                start_time, end_time, actual_hours, is_finished, is_long_term, is_added,
                project_id, notfinished_mission_id)
               VALUES (%(mission_date)s, %(mission_no)s, %(segment_no)s, %(mission_name)s,
                       %(estimated_hours)s, %(start_time)s, %(end_time)s, %(actual_hours)s,
                       %(is_finished)s, %(is_long_term)s, %(is_added)s,
                       %(project_id)s, %(notfinished_mission_id)s)""",
            data,
        )
    db.commit()
    return cur.lastrowid

def get_next_mission_no(mission_date):
    """算出這一天下一個可用的任務編號（從1開始往上加）。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(MAX(mission_no), 0) + 1 AS next_no FROM daily_mission WHERE mission_date = %s",
            (mission_date,),
        )
        return cur.fetchone()["next_no"]
    
def update_mission_summary(mission_id, start_time, end_time, actual_hours, is_finished):
    """更新區塊一任務的總結欄位（開始/結束時間、實際時數、是否完成）。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE daily_mission
               SET start_time=%s, end_time=%s, actual_hours=%s, is_finished=%s
               WHERE mission_id=%s""",
            (start_time, end_time, actual_hours, is_finished, mission_id),
        )
    db.commit()


def delete_mission(mission_id):
    """刪除一筆任務，主要給區塊二(追加任務)的刪除按鈕用。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM daily_mission WHERE mission_id=%s", (mission_id,))
    db.commit()