from app.db import get_db
from app.repositories.stage_mission_repo import sync_stage_mission_status


def get_active_dates_in_range(user_id, start_date, end_date):
    """首頁/月曆判斷『哪天有活動痕跡』：建立日、目前活躍日、結案日、未完成追蹤被動作的日期，四個來源都算。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT mission_start_date AS d FROM daily_mission WHERE user_id=%s AND mission_start_date BETWEEN %s AND %s
               UNION
               SELECT mission_active_date AS d FROM daily_mission WHERE user_id=%s AND mission_active_date BETWEEN %s AND %s
               UNION
               SELECT mission_finish_date AS d FROM daily_mission WHERE user_id=%s AND mission_finish_date BETWEEN %s AND %s
               UNION
               SELECT update_date AS d FROM unfinished_mission WHERE user_id=%s AND update_date BETWEEN %s AND %s""",
            (user_id, start_date, end_date, user_id, start_date, end_date,
             user_id, start_date, end_date, user_id, start_date, end_date),
        )
        return {row["d"] for row in cur.fetchall()}


def get_created_missions(user_id, active_date):
    """『任務安排』清單：用mission_active_date篩『今天』，不再碰mission_start_date。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT dm.*, ps.stage_name, ps.project_id, p.project_name,
                      EXISTS(SELECT 1 FROM unfinished_mission um WHERE um.mission_id=dm.mission_id) AS name_locked
               FROM daily_mission dm
               LEFT JOIN project_stage ps ON dm.project_stage_id = ps.project_stage_id
               LEFT JOIN project p ON ps.project_id = p.project_id
               WHERE dm.user_id = %s AND dm.mission_active_date = %s AND dm.is_added = 0
                 AND dm.status != 'unfinished'
               ORDER BY dm.mission_no""",
            (user_id, active_date),
        )
        return cur.fetchall()


def get_missions_by_date(user_id, active_date):
    """任務總結頁用，同樣改用mission_active_date。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT dm.*, ps.stage_name, ps.project_id, p.project_name
               FROM daily_mission dm
               LEFT JOIN project_stage ps ON dm.project_stage_id = ps.project_stage_id
               LEFT JOIN project p ON ps.project_id = p.project_id
               WHERE dm.user_id = %s AND dm.mission_active_date = %s
               ORDER BY dm.mission_no""",
            (user_id, active_date),
        )
        return cur.fetchall()


def get_next_mission_no(user_id, active_date):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(MAX(mission_no),0)+1 AS next_no FROM daily_mission WHERE user_id=%s AND mission_active_date=%s",
            (user_id, active_date),
        )
        return cur.fetchone()["next_no"]


def insert_mission(data: dict):
    """全新任務：mission_start_date(建立日)跟mission_active_date(目前活躍日)一開始必然相同，
    之後mission_start_date永遠不會再被改動，只有mission_active_date會跟著匯入動作變動。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO daily_mission
               (user_id, mission_start_date, mission_active_date, mission_no, mission_name, category,
                estimated_hours, start_time, end_time, is_added, project_stage_id, status)
               VALUES (%(user_id)s, %(mission_start_date)s, %(mission_start_date)s, %(mission_no)s, %(mission_name)s, %(category)s,
                       %(estimated_hours)s, %(start_time)s, %(end_time)s, %(is_added)s, %(project_stage_id)s, 'default')""",
            data,
        )
    db.commit()
    mission_id = cur.lastrowid
    if data.get("project_stage_id"):
        sync_stage_mission_status(data["user_id"], mission_id)
    return mission_id


def update_mission_plan(user_id, mission_id, mission_name, estimated_hours, start_time, end_time, category, project_stage_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT mission_name, estimated_hours, start_time, end_time, category, project_stage_id "
            "FROM daily_mission WHERE mission_id=%s AND user_id=%s AND status='default'",
            (mission_id, user_id),
        )
        current = cur.fetchone()
        if current is None:
            return None

        cur.execute("SELECT 1 FROM unfinished_mission WHERE mission_id=%s LIMIT 1", (mission_id,))
        locked = cur.fetchone() is not None
        final_name = current["mission_name"] if locked else mission_name

        def fmt(t):
            if t is None:
                return None
            total_minutes = int(t.total_seconds() // 60)
            return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

        changed = (
            final_name != current["mission_name"]
            or float(estimated_hours) != float(current["estimated_hours"])
            or start_time != fmt(current["start_time"])
            or end_time != fmt(current["end_time"])
            or category != current["category"]
            or project_stage_id != current["project_stage_id"]
        )
        if not changed:
            return "unchanged"

        cur.execute(
            """UPDATE daily_mission SET mission_name=%s, estimated_hours=%s, start_time=%s, end_time=%s, category=%s, project_stage_id=%s
               WHERE mission_id=%s AND user_id=%s AND status='default'""",
            (final_name, estimated_hours, start_time, end_time, category, project_stage_id, mission_id, user_id),
        )
    db.commit()
    sync_stage_mission_status(user_id, mission_id)
    return "updated"


# def delete_mission(user_id, mission_id):
#     """『刪除』的實際行為：沒有匯入歷史的任務→真的刪除；有歷史的任務→退回成『目前活躍日=最近一次追蹤紀錄的update_date』的unfinished狀態。
#     這裡只動mission_active_date，mission_start_date完全不碰，建立日永遠保持原樣。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             "SELECT unfinished_id, update_date FROM unfinished_mission WHERE mission_id=%s ORDER BY unfinished_id DESC LIMIT 1",
#             (mission_id,),
#         )
#         last = cur.fetchone()

#         if last is None:
#             cur.execute(
#                 "DELETE FROM daily_mission WHERE mission_id=%s AND user_id=%s AND status='default'",
#                 (mission_id, user_id),
#             )
#             db.commit()
#             return (cur.rowcount > 0), False

#         restored_date = last["update_date"]
#         cur.execute(
#             "SELECT COALESCE(MAX(mission_no),0)+1 AS next_no FROM daily_mission WHERE user_id=%s AND mission_active_date=%s",
#             (user_id, restored_date),
#         )
#         next_no = cur.fetchone()["next_no"]

#         cur.execute(
#             """UPDATE daily_mission
#                SET status='unfinished', mission_active_date=%s, mission_no=%s,
#                    start_time=NULL, end_time=NULL, actual_hours=NULL
#                WHERE mission_id=%s AND user_id=%s AND status='default'""",
#             (restored_date, next_no, mission_id, user_id),
#         )
#         updated = cur.rowcount
#         if updated:
#             cur.execute(
#                 "UPDATE unfinished_mission SET is_operatable=1, sequence_exit=0 WHERE unfinished_id=%s",
#                 (last["unfinished_id"],),
#             )
#     db.commit()
#     if updated:
#         sync_stage_mission_status(user_id, mission_id)
#     return (updated > 0), True
def delete_mission(user_id, mission_id):
    """『刪除』＝真正復原到匯入前的狀態，不是重新起算一個新的懸掛起點：
    - 沒有匯入過的任務：直接物理刪除。
    - 匯入過的任務：找出『匯入動作當下新增的那一筆』(U_new)直接刪掉(它整個是匯入的副產物)，
      把它的前一筆(U_old)復原成is_operatable=1, sequence_exit=0，
      daily_mission的mission_active_date/mission_no退回U_old.update_date當時的狀態，
      懸掛天數因此自然接續原本的軌跡，不會被重置。"""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT unfinished_id, follower_id FROM unfinished_mission WHERE mission_id=%s ORDER BY unfinished_id DESC LIMIT 1",
            (mission_id,),
        )
        latest = cur.fetchone()

        if latest is None:
            cur.execute(
                "DELETE FROM daily_mission WHERE mission_id=%s AND user_id=%s AND status='default'",
                (mission_id, user_id),
            )
            db.commit()
            return (cur.rowcount > 0), False

        if latest["follower_id"] is None:
            # 理論上不該發生：有歷史紀錄卻是第一筆，代表資料不一致，安全起見直接回報失敗，不盲目猜測
            return False, False

        cur.execute(
            "SELECT unfinished_id, update_date FROM unfinished_mission WHERE unfinished_id=%s",
            (latest["follower_id"],),
        )
        old = cur.fetchone()

        restored_date = old["update_date"]
        cur.execute(
            "SELECT COALESCE(MAX(mission_no),0)+1 AS next_no FROM daily_mission "
            "WHERE user_id=%s AND mission_active_date=%s AND mission_id<>%s",
            (user_id, restored_date, mission_id),
        )
        next_no = cur.fetchone()["next_no"]

        cur.execute(
            """UPDATE daily_mission
               SET status='unfinished', mission_active_date=%s, mission_no=%s,
                   start_time=NULL, end_time=NULL, actual_hours=NULL
               WHERE mission_id=%s AND user_id=%s AND status='default'""",
            (restored_date, next_no, mission_id, user_id),
        )
        updated = cur.rowcount
        if updated:
            # 把匯入時新增的那一筆整個刪掉，再把舊的那一筆復原
            cur.execute("DELETE FROM unfinished_mission WHERE unfinished_id=%s", (latest["unfinished_id"],))
            cur.execute(
                "UPDATE unfinished_mission SET is_operatable=1, sequence_exit=0 WHERE unfinished_id=%s",
                (old["unfinished_id"],),
            )
    db.commit()
    if updated:
        sync_stage_mission_status(user_id, mission_id)
    return (updated > 0), True


def report_mission_result(user_id, mission_id, is_finished, start_time, end_time, actual_hours, category, project_stage_id):
    """這裡修掉一個真實存在的bug：選『已完成』時，原本只敢UPDATE一筆is_operatable=1的追蹤紀錄，
    但如果這個任務是今天才匯入的，匯入當下並不會留下活著的追蹤紀錄，導致這個UPDATE悄悄地找不到任何資料、
    那筆追蹤紀錄永遠卡在open狀態、從未被標記resolved。
    這次的修法是把『匯入』也改成會留下一筆活著的追蹤紀錄(見下方import_mission)，
    這樣這裡的UPDATE語句本身就能一如預期地找到並正確結案。"""
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
                    """UPDATE unfinished_mission SET status='resolved', is_operatable=0,
                           start_time=%s, end_time=%s, actual_hours=%s
                       WHERE mission_id=%s AND is_operatable=1""",
                    (start_time, end_time, actual_hours, mission_id),
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
                cur.execute("SELECT unfinished_id FROM unfinished_mission WHERE mission_id=%s AND is_operatable=1", (mission_id,))
                existing = cur.fetchone()
                if existing:
                    cur.execute(
                        "UPDATE unfinished_mission SET start_time=%s, end_time=%s, actual_hours=%s WHERE unfinished_id=%s",
                        (start_time, end_time, actual_hours, existing["unfinished_id"]),
                    )
                else:
                    cur.execute("SELECT mission_active_date FROM daily_mission WHERE mission_id=%s", (mission_id,))
                    active_date = cur.fetchone()["mission_active_date"]
                    cur.execute(
                        "SELECT unfinished_id FROM unfinished_mission WHERE mission_id=%s ORDER BY unfinished_id DESC LIMIT 1",
                        (mission_id,),
                    )
                    prev = cur.fetchone()
                    cur.execute(
                        """INSERT INTO unfinished_mission
                           (user_id, mission_id, status, is_operatable, sequence_exit, follower_id, update_date, start_time, end_time, actual_hours)
                           VALUES (%s, %s, 'open', 1, 0, %s, %s, %s, %s, %s)""",
                        (user_id, mission_id, prev["unfinished_id"] if prev else None, active_date, start_time, end_time, actual_hours),
                    )
    db.commit()
    if updated:
        sync_stage_mission_status(user_id, mission_id)
    return updated


def mark_overdue_as_unfinished(user_id, today):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE daily_mission SET status='unfinished', is_auto_closed=1
               WHERE user_id=%s AND mission_active_date < %s AND is_added=0 AND status='default'""",
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



# # def delete_mission(user_id, mission_id):
# #     db = get_db()
# #     with db.cursor() as cur:
# #         cur.execute("DELETE FROM daily_mission WHERE mission_id=%s AND user_id=%s AND status='default'", (mission_id, user_id))
# #     db.commit()
# #     return cur.rowcount

