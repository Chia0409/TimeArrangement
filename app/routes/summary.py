from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, session

from app.services.date_service import get_day_status, calc_actual_hours
from app.repositories.mission_repo import (
    get_missions_by_date, get_next_mission_no, insert_mission,
    update_mission_summary, delete_mission,
)
from app.services.auth_service import login_required

summary_bp = Blueprint("summary", __name__)


def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


@summary_bp.route("/summary/<date_str>")
@login_required
def summary(date_str):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    status = get_day_status(mission_date)

    if status == "future":
        return render_template("summary.html", mission_date=mission_date, status=status,
                                block1=[], block2=[], can_edit_block1=False, can_edit_block2=False)

    all_missions = get_missions_by_date(user_id, mission_date)
    block1 = [m for m in all_missions if not m["is_added"]]
    block2 = [m for m in all_missions if m["is_added"]]

    return render_template("summary.html", mission_date=mission_date, status=status,
                            block1=block1, block2=block2,
                            can_edit_block1=(status == "today"),
                            can_edit_block2=(status in ("today", "past")))


@summary_bp.route("/summary/<date_str>/update/<int:mission_id>", methods=["POST"])
@login_required
def update_block1(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) != "today":
        abort(403)

    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    is_finished = 1 if request.form.get("is_finished") else 0
    actual_hours = calc_actual_hours(start_time, end_time)

    update_mission_summary(user_id, mission_id, start_time, end_time, actual_hours, is_finished)
    flash("已儲存！")
    return redirect(url_for("summary.summary", date_str=date_str))


@summary_bp.route("/summary/<date_str>/add", methods=["POST"])
@login_required
def add_block2(date_str):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) not in ("today", "past"):
        abort(403)

    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    insert_mission({
        "user_id": user_id,
        "mission_date": mission_date,
        "mission_no": get_next_mission_no(user_id, mission_date),
        "segment_no": 1,
        "mission_name": request.form["mission_name"],
        "estimated_hours": 0,
        "start_time": start_time, "end_time": end_time,
        "actual_hours": calc_actual_hours(start_time, end_time),
        "is_finished": 1, "is_long_term": 0, "is_added": 1,
        "project_id": None, "notfinished_mission_id": None,
    })
    flash("已新增追加任務！")
    return redirect(url_for("summary.summary", date_str=date_str))


@summary_bp.route("/summary/<date_str>/delete/<int:mission_id>", methods=["POST"])
@login_required
def delete_block2(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) not in ("today", "past"):
        abort(403)

    delete_mission(user_id, mission_id)
    flash("已刪除！")
    return redirect(url_for("summary.summary", date_str=date_str))