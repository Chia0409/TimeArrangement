from datetime import datetime
from flask import Blueprint, render_template, request, session, jsonify

from app.services.date_service import get_day_status, calc_actual_hours
from app.repositories.mission_repo import (
    get_missions_by_date, get_next_mission_no, insert_mission,
    update_mission_result, delete_mission,
)
from app.services.auth_service import login_required

summary_bp = Blueprint("summary", __name__)


def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _compute_hours(start_time, end_time):
    """時間沒填齊就不算，回傳None讓資料庫存NULL，不強迫使用者一定要填時間才能標記完成狀態。"""
    if start_time and end_time:
        return calc_actual_hours(start_time, end_time)
    return None


@summary_bp.route("/summary/<date_str>")
@login_required
def summary(date_str):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    status = get_day_status(mission_date)

    if status == "future":
        return render_template("summary.html", mission_date=mission_date, status=status,
                                pending=[], answered=[], added=[],
                                can_edit_original=False, can_edit_added=False)

    all_missions = get_missions_by_date(user_id, mission_date)
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


# ---------- 原計畫任務：回報完成狀態 / 修改已回報的資料 ----------

@summary_bp.route("/summary/<date_str>/mission/<int:mission_id>/answer", methods=["POST"])
@login_required
def answer_mission(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) != "today":
        return jsonify(success=False, message="只有今天的任務可以回報"), 403

    is_finished = request.form.get("is_finished", "")
    if is_finished not in ("0", "1"):
        return jsonify(success=False, message="請選擇是否完成"), 400

    start_time = request.form.get("start_time") or None
    end_time = request.form.get("end_time") or None
    actual_hours = _compute_hours(start_time, end_time)

    update_mission_result(user_id, mission_id, int(is_finished), start_time, end_time, actual_hours)
    return jsonify(success=True, is_finished=int(is_finished), start_time=start_time,
                   end_time=end_time, actual_hours=actual_hours)


@summary_bp.route("/summary/<date_str>/mission/<int:mission_id>/update", methods=["POST"])
@login_required
def update_answered_mission(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) != "today":
        return jsonify(success=False, message="只有今天的任務可以修改"), 403

    is_finished = request.form.get("is_finished", "")
    if is_finished not in ("0", "1"):
        return jsonify(success=False, message="請選擇是否完成"), 400

    start_time = request.form.get("start_time") or None
    end_time = request.form.get("end_time") or None
    actual_hours = _compute_hours(start_time, end_time)

    update_mission_result(user_id, mission_id, int(is_finished), start_time, end_time, actual_hours)
    return jsonify(success=True)


# ---------- 追加任務：跟plan.html同一套每列獨立儲存/刪除 ----------

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