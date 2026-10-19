from app.db import get_db
from app.repositories.stage_mission_repo import sync_stage_mission_status


def get_active_dates_in_range(user_id, start_date, end_date):
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
            (user_id, start_date, end_date, user_id, start_date, end_date, user_id, start_date, end_date),
        )
        return {row["d"] for row in cur.fetchall()}


def get_created_missions(user_id, mission_start_date):
    """『任務安排』清單：多join project_stage跟project，順便算出name_locked
    ——只要這個任務在unfinished_mission裡曾經出現過，就代表它是被接續的任務，名稱不給改。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT dm.*, ps.stage_name, ps.project_id, p.project_name,
                      EXISTS(SELECT 1 FROM unfinished_mission um WHERE um.mission_id=dm.mission_id) AS name_locked
               FROM daily_mission dm
               LEFT JOIN project_stage ps ON dm.project_stage_id = ps.project_stage_id
               LEFT JOIN project p ON ps.project_id = p.project_id
               WHERE dm.user_id = %s AND dm.mission_start_date = %s AND dm.is_added = 0
                 AND dm.status != 'unfinished'
               ORDER BY dm.mission_no""",
            (user_id, mission_start_date),
        )
        return cur.fetchall()


def get_missions_by_date(user_id, mission_date):
    """任務總結頁用，跟get_created_missions差別在這支不排除is_added、不算name_locked
    （總結頁不涉及改名，不需要這個資訊）。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT dm.*, ps.stage_name, ps.project_id, p.project_name
               FROM daily_mission dm
               LEFT JOIN project_stage ps ON dm.project_stage_id = ps.project_stage_id
               LEFT JOIN project p ON ps.project_id = p.project_id
               WHERE dm.user_id = %s AND dm.mission_start_date = %s
               ORDER BY dm.mission_no""",
            (user_id, mission_date),
        )
        return cur.fetchall()


def get_next_mission_no(user_id, mission_start_date):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(MAX(mission_no),0)+1 AS next_no FROM daily_mission WHERE user_id=%s AND mission_start_date=%s",
            (user_id, mission_start_date),
        )
        return cur.fetchone()["next_no"]


def insert_mission(data: dict):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO daily_mission
               (user_id, mission_start_date, mission_no, mission_name, category,
                estimated_hours, start_time, end_time, is_added, project_stage_id, status)
               VALUES (%(user_id)s, %(mission_start_date)s, %(mission_no)s, %(mission_name)s, %(category)s,
                       %(estimated_hours)s, %(start_time)s, %(end_time)s, %(is_added)s, %(project_stage_id)s, 'default')""",
            data,
        )
    db.commit()
    mission_id = cur.lastrowid
    if data.get("project_stage_id"):
        sync_stage_mission_status(data["user_id"], mission_id)
    return mission_id


def update_mission_plan(user_id, mission_id, mission_name, estimated_hours, start_time, end_time, category, project_stage_id):
    """name_locked由後端自己判斷，不信任前端傳來的任何旗標——
    就算有人把disabled的input用瀏覽器開發工具解鎖硬改，後端這裡還是會忽略改名。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT 1 FROM unfinished_mission WHERE mission_id=%s LIMIT 1", (mission_id,))
        locked = cur.fetchone() is not None

        if locked:
            cur.execute(
                """UPDATE daily_mission SET estimated_hours=%s, start_time=%s, end_time=%s, category=%s, project_stage_id=%s
                   WHERE mission_id=%s AND user_id=%s AND status='default'""",
                (estimated_hours, start_time, end_time, category, project_stage_id, mission_id, user_id),
            )
        else:
            cur.execute(
                """UPDATE daily_mission SET mission_name=%s, estimated_hours=%s, start_time=%s, end_time=%s, category=%s, project_stage_id=%s
                   WHERE mission_id=%s AND user_id=%s AND status='default'""",
                (mission_name, estimated_hours, start_time, end_time, category, project_stage_id, mission_id, user_id),
            )
    db.commit()
    if cur.rowcount:
        sync_stage_mission_status(user_id, mission_id)
    return cur.rowcount


# def delete_mission(user_id, mission_id):
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute("DELETE FROM daily_mission WHERE mission_id=%s AND user_id=%s AND status='default'", (mission_id, user_id))
#     db.commit()
#     return cur.rowcount

def delete_mission(user_id, mission_id):
    """刪除『任務安排』裡的一筆任務。
    物理刪除只給『從沒匯入過』的任務用——匯入過的任務因為unfinished_mission的外鍵
    擋著，刪不掉，而且使用者要的也不是刪除，是『復原成匯入前的狀態』。
    回傳 (success, reverted)：reverted=True代表這次是復原，不是真的刪除。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT unfinished_id, update_date FROM unfinished_mission WHERE mission_id=%s ORDER BY unfinished_id DESC LIMIT 1",
            (mission_id,),
        )
        last = cur.fetchone()

        if last is None:
            cur.execute(
                "DELETE FROM daily_mission WHERE mission_id=%s AND user_id=%s AND status='default'",
                (mission_id, user_id),
            )
            db.commit()
            return (cur.rowcount > 0), False

        restored_date = last["update_date"]
        cur.execute(
            "SELECT COALESCE(MAX(mission_no),0)+1 AS next_no FROM daily_mission WHERE user_id=%s AND mission_start_date=%s",
            (user_id, restored_date),
        )
        next_no = cur.fetchone()["next_no"]

        cur.execute(
            """UPDATE daily_mission
               SET status='unfinished', mission_start_date=%s, mission_no=%s,
                   start_time=NULL, end_time=NULL, actual_hours=NULL
               WHERE mission_id=%s AND user_id=%s AND status='default'""",
            (restored_date, next_no, mission_id, user_id),
        )
        updated = cur.rowcount
        if updated:
            cur.execute(
                "UPDATE unfinished_mission SET is_operatable=1, sequence_exit=0 WHERE unfinished_id=%s",
                (last["unfinished_id"],),
            )
    db.commit()
    if updated:
        sync_stage_mission_status(user_id, mission_id)
    return (updated > 0), True


def report_mission_result(user_id, mission_id, is_finished, start_time, end_time, actual_hours, category, project_stage_id):
    """is_finished=1：真的完成，順便把還開著的追蹤紀錄收尾成resolved。
       is_finished=0：使用者今天就主動承認沒做完，等同『提早一天』進入unfinished追蹤（不用等明天自動過期才判定）。"""
    db = get_db()
    with db.cursor() as cur:
        if is_finished:
            cur.execute("SELECT 1 FROM unfinished_mission WHERE mission_id=%s LIMIT 1", (mission_id,))
            has_history = cur.fetchone() is not None
            cur.execute(
                """UPDATE daily_mission
                   SET status='finished', start_time=%s, end_time=%s, actual_hours=%s,
                       mission_finish_date=CURDATE(), is_ONTime_finished=%s, category=%s, project_stage_id=%s
                   WHERE mission_id=%s AND user_id=%s AND status='default'""",
                (start_time, end_time, actual_hours, 0 if has_history else 1, category, project_stage_id, mission_id, user_id),
            )
            updated = cur.rowcount
            if updated:
                cur.execute(
                    "UPDATE unfinished_mission SET status='resolved', is_operatable=0 WHERE mission_id=%s AND is_operatable=1",
                    (mission_id,),
                )
        else:
            cur.execute(
                """UPDATE daily_mission
                   SET status='unfinished', is_auto_closed=0, start_time=%s, end_time=%s, actual_hours=%s,
                       category=%s, project_stage_id=%s
                   WHERE mission_id=%s AND user_id=%s AND status='default'""",
                (start_time, end_time, actual_hours, category, project_stage_id, mission_id, user_id),
            )
            updated = cur.rowcount
            if updated:
                cur.execute("SELECT 1 FROM unfinished_mission WHERE mission_id=%s AND is_operatable=1", (mission_id,))
                if cur.fetchone() is None:
                    cur.execute("SELECT mission_start_date FROM daily_mission WHERE mission_id=%s", (mission_id,))
                    start_date = cur.fetchone()["mission_start_date"]
                    cur.execute(
                        "SELECT unfinished_id FROM unfinished_mission WHERE mission_id=%s ORDER BY unfinished_id DESC LIMIT 1",
                        (mission_id,),
                    )
                    prev = cur.fetchone()
                    cur.execute(
                        """INSERT INTO unfinished_mission (user_id, mission_id, status, is_operatable, sequence_exit, follower_id, update_date)
                        VALUES (%s, %s, 'open', 1, 0, %s, %s)""",
                        (user_id, mission_id, prev["unfinished_id"] if prev else None, start_date),
                    )
                    # cur.execute(
                    #     """INSERT INTO unfinished_mission (user_id, mission_id, status, is_operatable, sequence_exit, update_date)
                    #        VALUES (%s, %s, 'open', 1, 0, %s)""",
                    #     (user_id, mission_id, start_date),
                    # )
    db.commit()
    if updated:
        sync_stage_mission_status(user_id, mission_id)
    return updated


def mark_overdue_as_unfinished(user_id, today):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE daily_mission SET status='unfinished', is_auto_closed=1
               WHERE user_id=%s AND mission_start_date < %s AND is_added=0 AND status='default'""",
            (user_id, today),
        )
    db.commit()


def close_mission_from_unfinished(user_id, mission_id, today):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE daily_mission SET status='finished', mission_finish_date=%s, is_ONTime_finished=0 WHERE mission_id=%s AND user_id=%s",
            (today, mission_id, user_id),
        )
    db.commit()
    
# from app.db import get_db
# from app.repositories.stage_mission_repo import sync_stage_mission_status

# def get_active_dates_in_range(user_id, start_date, end_date):
#     """撈這段期間裡所有「有活動痕跡」的日期，用在首頁週表格／月曆頁判斷哪幾天要顯示連結。
#     三個來源分別代表：任務建立日、任務真正結案日、未完成任務被操作的日期
#     （第三個來源現在還不會真的查到東西，等下一批匯入功能做出來才會生效，這裡先把邏輯寫對）。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """SELECT mission_start_date AS d FROM daily_mission
#                WHERE user_id = %s AND mission_start_date BETWEEN %s AND %s
#                UNION
#                SELECT mission_finish_date AS d FROM daily_mission
#                WHERE user_id = %s AND mission_finish_date BETWEEN %s AND %s
#                UNION
#                SELECT update_date AS d FROM unfinished_mission
#                WHERE user_id = %s AND update_date BETWEEN %s AND %s""",
#             (user_id, start_date, end_date,
#              user_id, start_date, end_date,
#              user_id, start_date, end_date),
#         )
#         return {row["d"] for row in cur.fetchall()}


# def get_created_missions(user_id, mission_start_date):
#     """「預計執行任務」頁面的『新增任務』清單：當天新建立、原計畫(非追加)、都還是status='default'。
#     status='default'是因為這批只處理「新建立」這條線——
#     萬一這天有任務後來變成unfinished/finished，就不該再出現在這份「待編輯清單」裡。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """SELECT * FROM daily_mission
#                WHERE user_id = %s AND mission_start_date = %s AND is_added = 0
#                ORDER BY mission_no""",
#             (user_id, mission_start_date),
#         )
#         return cur.fetchall()


# def get_next_mission_no(user_id, mission_start_date):
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """SELECT COALESCE(MAX(mission_no), 0) + 1 AS next_no
#                FROM daily_mission WHERE user_id = %s AND mission_start_date = %s""",
#             (user_id, mission_start_date),
#         )
#         return cur.fetchone()["next_no"]


# def insert_mission(data: dict):
#     """新增一筆任務，status固定從'default'(尚未回報)開始。
#     category跟project_stage_id這批先用不到(傳None)，等Batch3專案功能接上後才會真的賦值。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """INSERT INTO daily_mission
#                (user_id, mission_start_date, mission_no, mission_name, category,
#                 estimated_hours, is_added, project_stage_id, status)
#                VALUES (%(user_id)s, %(mission_start_date)s, %(mission_no)s, %(mission_name)s, %(category)s,
#                        %(estimated_hours)s, %(is_added)s, %(project_stage_id)s, 'default')""",
#             data,
#         )
#     db.commit()
#     return cur.lastrowid


# def update_mission_plan(user_id, mission_id, mission_name, estimated_hours):
#     """只有status還是'default'的任務才准許修改——回傳rowcount，0代表「這筆其實已經不能改了」，
#     呼叫端可以依此判斷要不要跟使用者說明原因，而不是悄悄地什麼都沒發生。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission SET mission_name=%s, estimated_hours=%s
#                WHERE mission_id=%s AND user_id=%s AND status='default'""",
#             (mission_name, estimated_hours, mission_id, user_id),
#         )
#     db.commit()
#     return cur.rowcount


# def delete_mission(user_id, mission_id):
#     """同樣限定status='default'，同樣回傳rowcount。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             "DELETE FROM daily_mission WHERE mission_id=%s AND user_id=%s AND status='default'",
#             (mission_id, user_id),
#         )
#     db.commit()
#     return cur.rowcount

# def get_missions_by_date(user_id, mission_date):
#     """任務總結頁用：撈『今天這份清單』上的任務——
#     嚴格來說新schema下『今天』不等於mission_start_date=今天，
#     但這批先只處理『今天新建立、原計畫』這條線，跟plan.html的清單定義一致，
#     匯入進來的舊任務要等下一批接上。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """SELECT dm.*, ps.stage_name
#                FROM daily_mission dm
#                LEFT JOIN project_stage ps ON dm.project_stage_id = ps.project_stage_id
#                WHERE dm.user_id = %s AND dm.mission_start_date = %s
#                ORDER BY dm.mission_no""",
#             (user_id, mission_date),
#         )
#         return cur.fetchall()


# def report_mission_result(user_id, mission_id, is_finished, start_time, end_time, actual_hours):
#     """回報任務結果，status直接寫死'finished'——新schema下不管『真的完成』還是『強制結束』都是這個值，
#     is_finished這個參數維持是為了相容現在的呼叫端判斷『是否完成』，但這批先不寫進unfinished_mission，
#     那段串連邏輯留到下一批一起做，這裡先求任務總結頁面本身能存檔。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission
#                SET status='finished', start_time=%s, end_time=%s, actual_hours=%s,
#                    mission_finish_date=CURDATE(), is_ONTime_finished=%s
#                WHERE mission_id=%s AND user_id=%s AND status='default'""",
#             (start_time, end_time, actual_hours, 1 if is_finished else 0, mission_id, user_id),
#         )
#     db.commit()
#     if cur.rowcount:
#         sync_stage_mission_status(user_id, mission_id)
#     return cur.rowcount
    

# def mark_overdue_as_unfinished(user_id, today):
#     """過期還沒回報的任務 → daily_mission自己的狀態轉換。
#     只處理這張表自己的事，『要不要連動建立unfinished_mission』交給unfinished_repo，
#     每張表的repo只碰自己對應的那張表，分工維持單純。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission SET status='unfinished', is_auto_closed=1
#                WHERE user_id=%s AND mission_start_date < %s AND is_added=0 AND status='default'""",
#             (user_id, today),
#         )
#     db.commit()


# def finish_mission_from_unfinished(user_id, mission_id, start_time, end_time, actual_hours):
#     """未完成任務透過匯入變『完成』時，回頭更新daily_mission——
#     is_ONTime_finished固定寫0，因為會呼叫到這支，前提就是它曾經是unfinished過，不可能準時。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission
#                SET status='finished', mission_finish_date=CURDATE(),
#                    is_ONTime_finished=0, start_time=%s, end_time=%s, actual_hours=%s
#                WHERE mission_id=%s AND user_id=%s""",
#             (start_time, end_time, actual_hours, mission_id, user_id),
#         )
#     db.commit()

# def close_mission_from_unfinished(user_id, mission_id, today):
#     """強制結束：daily_mission.status變finished，但不像『報完成』那樣記錄start/end/actual_hours
#     ——強制結束不代表真的投入了多少時間，這幾欄保持空白。is_ONTime_finished固定寫0。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """UPDATE daily_mission
#                SET status='finished', mission_finish_date=%s, is_ONTime_finished=0
#                WHERE mission_id=%s AND user_id=%s""",
#             (today, mission_id, user_id),
#         )
#     db.commit()

