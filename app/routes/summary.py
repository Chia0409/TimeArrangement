from datetime import datetime, date
from flask import Blueprint, render_template, request, session, jsonify

from app.services.date_service import get_day_status, calc_actual_hours
from app.repositories.mission_repo import (
    get_missions_by_date, get_next_mission_no, insert_mission,
    update_mission_result, update_original_mission_result,
    delete_mission, close_overdue_missions,
)
from app.repositories.project_repo import (
    get_unfinished_projects, get_project, get_or_create_project,
)
from app.services.auth_service import login_required

summary_bp = Blueprint("summary", __name__)


def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _compute_hours(start_time, end_time):
    if start_time and end_time:
        return calc_actual_hours(start_time, end_time)
    return None


def _fmt_time(t):
    """PyMySQL把MySQL的TIME讀成timedelta，str()後早上9點會變'9:00:00'，
    <input type="time">不吃這種格式(要兩位數的'09:00')，所以統一轉成HH:MM。"""
    if t is None:
        return ""
    minutes = int(t.total_seconds() // 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _resolve_longterm(user_id, mission_date):
    """讀取表單裡的長期任務欄位，回傳 (is_long_term, project, created, error)：
       project = 選中(或新建)的長期任務dict，沒有就是None
       created = 這次是否「新建立」，前端要靠它更新下拉清單
       error   = 有問題時的提示文字，沒問題是None"""
    if request.form.get("is_long_term", "0") != "1":
        return 0, None, False, None

    choice = request.form.get("project_id", "")

    if choice == "__new__":
        new_name = request.form.get("new_project_name", "").strip()
        if not new_name:
            return 0, None, False, "請輸入新的長期任務名稱"
        project, created = get_or_create_project(user_id, new_name, mission_date)
        return 1, project, created, None

    if not choice.isdigit():
        return 0, None, False, "請選擇一個長期任務，或新增一個"

    project = get_project(user_id, int(choice))  # 確認這個專案真的是這個人的
    if project is None:
        return 0, None, False, "找不到這個長期任務"
    return 1, project, False, None


@summary_bp.route("/api/projects")
@login_required
def list_projects():
    return jsonify(projects=get_unfinished_projects(session["user_id"]))


@summary_bp.route("/summary/<date_str>")
@login_required
def summary(date_str):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    today = date.today()
    status = get_day_status(mission_date, today)

    if status == "future":
        return render_template("summary.html", mission_date=mission_date, status=status,
                               pending=[], answered=[], added=[],
                               can_edit_original=False, can_edit_added=False)

    # 惰性結算：進來就把「過去日期、還沒回報」的任務自動關閉
    close_overdue_missions(user_id, today)

    all_missions = get_missions_by_date(user_id, mission_date)
    for m in all_missions:
        m["start_hhmm"] = _fmt_time(m["start_time"])
        m["end_hhmm"] = _fmt_time(m["end_time"])

    original = [m for m in all_missions if not m["is_added"]]
    added = [m for m in all_missions if m["is_added"]]
    pending = [m for m in original if m["is_finished"] is None]
    answered = [m for m in original if m["is_finished"] is not None]

    return render_template(
        "summary.html", mission_date=mission_date, status=status,
        pending=pending, answered=answered, added=added,
        can_edit_original=(status == "today"),
        can_edit_added=(status in ("today", "past")),
    )


# ---------- 原計畫任務：回報 與 修改 共用同一支 ----------
# 兩者在後端做的事完全一樣（把這筆任務的結果寫進去），所以合併成一支路由，
# 又是DRY原則：同一件事只寫一次。

@summary_bp.route("/summary/<date_str>/mission/<int:mission_id>/save", methods=["POST"])
@login_required
def save_original_mission(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) != "today":
        return jsonify(success=False, message="只有今天的任務可以回報或修改"), 403

    is_finished = request.form.get("is_finished", "")
    if is_finished not in ("0", "1"):
        return jsonify(success=False, message="請選擇是否完成"), 400

    is_long_term, project, created, error = _resolve_longterm(user_id, mission_date)
    if error:
        return jsonify(success=False, message=error), 400

    start_time = request.form.get("start_time") or None
    end_time = request.form.get("end_time") or None
    actual_hours = _compute_hours(start_time, end_time)
    project_id = project["project_id"] if project else None

    update_original_mission_result(user_id, mission_id, int(is_finished),
                                   start_time, end_time, actual_hours, is_long_term, project_id)
    return jsonify(
        success=True, is_finished=int(is_finished),
        start_time=start_time, end_time=end_time, actual_hours=actual_hours,
        is_long_term=is_long_term, project_id=project_id,
        project_name=project["project_name"] if project else None,
        created_project=created,
    )


# ---------- 追加任務（與上一版相同） ----------

@summary_bp.route("/summary/<date_str>/added/add", methods=["POST"])
@login_required
def add_added_mission(date_str):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) not in ("today", "past"):
        return jsonify(success=False, message="這一天不能新增追加任務"), 403

    name = request.form.get("mission_name", "").strip()
    if not name:
        return jsonify(success=False, message="任務名稱不能空白"), 400

    start_time = request.form.get("start_time") or None
    end_time = request.form.get("end_time") or None
    is_finished = request.form.get("is_finished", "1")

    mission_no = get_next_mission_no(user_id, mission_date)
    mission_id = insert_mission({
        "user_id": user_id, "mission_date": mission_date,
        "mission_no": mission_no, "segment_no": 1,
        "mission_name": name, "estimated_hours": 0,
        "start_time": start_time, "end_time": end_time,
        "actual_hours": _compute_hours(start_time, end_time),
        "is_finished": int(is_finished) if is_finished in ("0", "1") else 1,
        "is_long_term": 0, "is_added": 1,
        "project_id": None, "notfinished_mission_id": None,
    })
    return jsonify(success=True, mission_id=mission_id, mission_no=mission_no)


@summary_bp.route("/summary/<date_str>/added/<int:mission_id>/update", methods=["POST"])
@login_required
def update_added_mission(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) not in ("today", "past"):
        return jsonify(success=False, message="這一天不能修改追加任務"), 403

    is_finished = request.form.get("is_finished", "1")
    start_time = request.form.get("start_time") or None
    end_time = request.form.get("end_time") or None

    update_mission_result(
        user_id, mission_id,
        int(is_finished) if is_finished in ("0", "1") else 1,
        start_time, end_time, _compute_hours(start_time, end_time),
    )
    return jsonify(success=True)


@summary_bp.route("/summary/<date_str>/added/<int:mission_id>/delete", methods=["POST"])
@login_required
def delete_added_mission(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) not in ("today", "past"):
        return jsonify(success=False, message="這一天不能刪除追加任務"), 403

    delete_mission(user_id, mission_id)
    return jsonify(success=True)