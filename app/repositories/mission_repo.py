from app.db import get_db


def get_active_dates_in_range(user_id, start_date, end_date):
    """撈這段期間裡所有「有活動痕跡」的日期，用在首頁週表格／月曆頁判斷哪幾天要顯示連結。
    三個來源分別代表：任務建立日、任務真正結案日、未完成任務被操作的日期
    （第三個來源現在還不會真的查到東西，等下一批匯入功能做出來才會生效，這裡先把邏輯寫對）。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT mission_start_date AS d FROM daily_mission
               WHERE user_id = %s AND mission_start_date BETWEEN %s AND %s
               UNION
               SELECT mission_finish_date AS d FROM daily_mission
               WHERE user_id = %s AND mission_finish_date BETWEEN %s AND %s
               UNION
               SELECT update_date AS d FROM unfinished_mission
               WHERE user_id = %s AND update_date BETWEEN %s AND %s""",
            (user_id, start_date, end_date,
             user_id, start_date, end_date,
             user_id, start_date, end_date),
        )
        return {row["d"] for row in cur.fetchall()}


def get_created_missions(user_id, mission_start_date):
    """「預計執行任務」頁面的『新增任務』清單：當天新建立、原計畫(非追加)、都還是status='default'。
    status='default'是因為這批只處理「新建立」這條線——
    萬一這天有任務後來變成unfinished/finished，就不該再出現在這份「待編輯清單」裡。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT * FROM daily_mission
               WHERE user_id = %s AND mission_start_date = %s AND is_added = 0
               ORDER BY mission_no""",
            (user_id, mission_start_date),
        )
        return cur.fetchall()


def get_next_mission_no(user_id, mission_start_date):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT COALESCE(MAX(mission_no), 0) + 1 AS next_no
               FROM daily_mission WHERE user_id = %s AND mission_start_date = %s""",
            (user_id, mission_start_date),
        )
        return cur.fetchone()["next_no"]


def insert_mission(data: dict):
    """新增一筆任務，status固定從'default'(尚未回報)開始。
    category跟project_stage_id這批先用不到(傳None)，等Batch3專案功能接上後才會真的賦值。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO daily_mission
               (user_id, mission_start_date, mission_no, mission_name, category,
                estimated_hours, is_added, project_stage_id, status)
               VALUES (%(user_id)s, %(mission_start_date)s, %(mission_no)s, %(mission_name)s, %(category)s,
                       %(estimated_hours)s, %(is_added)s, %(project_stage_id)s, 'default')""",
            data,
        )
    db.commit()
    return cur.lastrowid


def update_mission_plan(user_id, mission_id, mission_name, estimated_hours):
    """只有status還是'default'的任務才准許修改——回傳rowcount，0代表「這筆其實已經不能改了」，
    呼叫端可以依此判斷要不要跟使用者說明原因，而不是悄悄地什麼都沒發生。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE daily_mission SET mission_name=%s, estimated_hours=%s
               WHERE mission_id=%s AND user_id=%s AND status='default'""",
            (mission_name, estimated_hours, mission_id, user_id),
        )
    db.commit()
    return cur.rowcount


def delete_mission(user_id, mission_id):
    """同樣限定status='default'，同樣回傳rowcount。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "DELETE FROM daily_mission WHERE mission_id=%s AND user_id=%s AND status='default'",
            (mission_id, user_id),
        )
    db.commit()
    return cur.rowcount

def get_missions_by_date(user_id, mission_date):
    """任務總結頁用：撈『今天這份清單』上的任務——
    嚴格來說新schema下『今天』不等於mission_start_date=今天，
    但這批先只處理『今天新建立、原計畫』這條線，跟plan.html的清單定義一致，
    匯入進來的舊任務要等下一批接上。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT dm.*, ps.stage_name
               FROM daily_mission dm
               LEFT JOIN project_stage ps ON dm.project_stage_id = ps.project_stage_id
               WHERE dm.user_id = %s AND dm.mission_start_date = %s
               ORDER BY dm.mission_no""",
            (user_id, mission_date),
        )
        return cur.fetchall()


def report_mission_result(user_id, mission_id, is_finished, start_time, end_time, actual_hours):
    """回報任務結果，status直接寫死'finished'——新schema下不管『真的完成』還是『強制結束』都是這個值，
    is_finished這個參數維持是為了相容現在的呼叫端判斷『是否完成』，但這批先不寫進unfinished_mission，
    那段串連邏輯留到下一批一起做，這裡先求任務總結頁面本身能存檔。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE daily_mission
               SET status='finished', start_time=%s, end_time=%s, actual_hours=%s,
                   mission_finish_date=CURDATE(), is_ONTime_finished=%s
               WHERE mission_id=%s AND user_id=%s AND status='default'""",
            (start_time, end_time, actual_hours, 1 if is_finished else 0, mission_id, user_id),
        )
    db.commit()
    return cur.rowcount


# def close_overdue_missions(user_id, today):
#     """過期還沒回報(status還是'default')的任務 → 標成unfinished+系統代標。
#     這批先只做daily_mission這邊的狀態轉換，『同時幫它在unfinished_mission建一筆追蹤紀錄』
#     這段(對應舊版的notfinished_mission寫入)留到下一批，因為那是unfinished_repo的責任範圍。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission SET status='unfinished', is_auto_closed=1
#                WHERE user_id=%s AND mission_start_date < %s AND is_added=0 AND status='default'""",
#             (user_id, today),
#         )
#     db.commit()

def mark_overdue_as_unfinished(user_id, today):
    """過期還沒回報的任務 → daily_mission自己的狀態轉換。
    只處理這張表自己的事，『要不要連動建立unfinished_mission』交給unfinished_repo，
    每張表的repo只碰自己對應的那張表，分工維持單純。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE daily_mission SET status='unfinished', is_auto_closed=1
               WHERE user_id=%s AND mission_start_date < %s AND is_added=0 AND status='default'""",
            (user_id, today),
        )
    db.commit()


def finish_mission_from_unfinished(user_id, mission_id, start_time, end_time, actual_hours):
    """未完成任務透過匯入變『完成』時，回頭更新daily_mission——
    is_ONTime_finished固定寫0，因為會呼叫到這支，前提就是它曾經是unfinished過，不可能準時。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE daily_mission
               SET status='finished', mission_finish_date=CURDATE(),
                   is_ONTime_finished=0, start_time=%s, end_time=%s, actual_hours=%s
               WHERE mission_id=%s AND user_id=%s""",
            (start_time, end_time, actual_hours, mission_id, user_id),
        )
    db.commit()

# add for not having ImportError
# def get_missions_by_date(user_id, mission_date):
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """SELECT dm.*, p.project_name
#                FROM daily_mission dm
#                LEFT JOIN project p ON dm.project_id = p.project_id
#                WHERE dm.user_id = %s AND dm.mission_date = %s
#                ORDER BY dm.mission_no, dm.segment_no""",
#             (user_id, mission_date),
#         )
#         return cur.fetchall()
    
# def update_mission_result(user_id, mission_id, is_finished, start_time, end_time, actual_hours):
#     """更新「完成狀態＋開始/結束時間＋實際工時」，原計畫任務跟追加任務共用這支。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission
#                SET is_finished=%s, start_time=%s, end_time=%s, actual_hours=%s
#                WHERE mission_id=%s AND user_id=%s""",
#             (is_finished, start_time, end_time, actual_hours, mission_id, user_id),
#         )
#     db.commit()

# def update_original_mission_result(user_id, mission_id, is_finished, start_time, end_time,
#                                    actual_hours, is_long_term, project_id):
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission
#                SET is_finished=%s, start_time=%s, end_time=%s, actual_hours=%s,
#                    is_long_term=%s, project_id=%s
#                WHERE mission_id=%s AND user_id=%s""",
#             (is_finished, start_time, end_time, actual_hours,
#              is_long_term, project_id, mission_id, user_id),
#         )
#     db.commit()

# def close_overdue_missions(user_id, today):
#     """過期未回報 → 標成未完成+系統代標，並各自建立、串上notfinished_mission追蹤紀錄。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission SET is_finished = 0, is_auto_closed = 1
#                WHERE user_id = %s AND mission_date < %s
#                  AND is_added = 0 AND is_finished IS NULL""",
#             (user_id, today),
#         )
#         cur.execute(
#             """INSERT INTO notfinished_mission (user_id, mission_id, status, start_date)
#                SELECT user_id, mission_id, 'open', mission_date
#                FROM daily_mission
#                WHERE user_id = %s AND is_auto_closed = 1 AND notfinished_mission_id IS NULL""",
#             (user_id,),
#         )
#         cur.execute(
#             """UPDATE daily_mission dm
#                JOIN notfinished_mission nm ON nm.mission_id = dm.mission_id
#                SET dm.notfinished_mission_id = nm.notfinished_mission_id
#                WHERE dm.user_id = %s AND dm.notfinished_mission_id IS NULL AND dm.is_finished = 0""",
#             (user_id,),
#         )
#     db.commit()