from datetime import datetime, date
from flask import Blueprint, render_template, request, session, jsonify

from app.services.date_service import get_day_status, calc_actual_hours
from app.repositories.mission_repo import get_missions_by_date, report_mission_result, mark_overdue_as_unfinished
from app.repositories.unfinished_repo import create_chains_for_newly_unfinished
from app.services.auth_service import login_required

summary_bp = Blueprint("summary", __name__)


def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _compute_hours(start_time, end_time):
    return calc_actual_hours(start_time, end_time) if start_time and end_time else None


@summary_bp.route("/summary/<date_str>")
@login_required
def summary(date_str):
    user_id = session["user_id"]
    mission_date = _parse_date(date_str)
    today = date.today()
    status = get_day_status(mission_date, today)

    if status == "future":
        return render_template("summary.html", mission_date=mission_date, status=status, pending=[], finished=[], unfinished=[], can_edit=False)
    
    mark_overdue_as_unfinished(user_id, today)
    create_chains_for_newly_unfinished(user_id)

    all_missions = get_missions_by_date(user_id, mission_date)
    pending = [m for m in all_missions if m["status"] == "default"]
    finished = [m for m in all_missions if m["status"] == "finished"]
    unfinished = [m for m in all_missions if m["status"] == "unfinished"]

    return render_template("summary.html", mission_date=mission_date, status=status,
                            pending=pending, finished=finished, unfinished=unfinished, can_edit=(status == "today"))


@summary_bp.route("/summary/<date_str>/mission/<int:mission_id>/report", methods=["POST"])
@login_required
def report_mission(date_str, mission_id):
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
    category = request.form.get("category", "").strip() or None
    stage_id = request.form.get("project_stage_id", "")
    project_stage_id = int(stage_id) if stage_id.isdigit() else None

    if not report_mission_result(user_id, mission_id, int(is_finished), start_time, end_time, actual_hours, category, project_stage_id):
        return jsonify(success=False, message="這筆任務目前不能回報"), 400
    return jsonify(success=True)

# from datetime import datetime, date
# from flask import Blueprint, render_template, request, session, jsonify

# from app.services.date_service import get_day_status, calc_actual_hours

# from app.repositories.mission_repo import (
#     get_missions_by_date, get_next_mission_no, insert_mission,
#     report_mission_result, mark_overdue_as_unfinished,
# )
# from app.repositories.unfinished_repo import create_chains_for_newly_unfinished

# from app.services.auth_service import login_required

# summary_bp = Blueprint("summary", __name__)


# def _parse_date(date_str):
#     return datetime.strptime(date_str, "%Y-%m-%d").date()


# def _compute_hours(start_time, end_time):
#     if start_time and end_time:
#         return calc_actual_hours(start_time, end_time)
#     return None


# @summary_bp.route("/summary/<date_str>")
# @login_required
# def summary(date_str):
#     user_id = session["user_id"]
#     mission_date = _parse_date(date_str)
#     today = date.today()
#     status = get_day_status(mission_date, today)

#     if status == "future":
#         return render_template("summary.html", mission_date=mission_date, status=status,
#                                pending=[], finished=[], can_edit=False)

#     # close_overdue_missions(user_id, today)
#     mark_overdue_as_unfinished(user_id, today)
#     create_chains_for_newly_unfinished(user_id)

#     all_missions = get_missions_by_date(user_id, mission_date)
#     pending = [m for m in all_missions if m["status"] == "default"]
#     finished = [m for m in all_missions if m["status"] == "finished"]
#     # status='unfinished' 的任務這批先不在這頁顯示——它們要等下一批「未完成任務管理」頁做出來才有地方去

#     return render_template(
#         "summary.html", mission_date=mission_date, status=status,
#         pending=pending, finished=finished,
#         can_edit=(status == "today"),
#     )


# @summary_bp.route("/summary/<date_str>/mission/<int:mission_id>/report", methods=["POST"])
# @login_required
# def report_mission(date_str, mission_id):
#     user_id = session["user_id"]
#     mission_date = _parse_date(date_str)
#     if get_day_status(mission_date) != "today":
#         return jsonify(success=False, message="只有今天的任務可以回報"), 403

#     is_finished = request.form.get("is_finished", "")
#     if is_finished not in ("0", "1"):
#         return jsonify(success=False, message="請選擇是否完成"), 400

#     start_time = request.form.get("start_time") or None
#     end_time = request.form.get("end_time") or None
#     actual_hours = _compute_hours(start_time, end_time)

#     if not report_mission_result(user_id, mission_id, int(is_finished), start_time, end_time, actual_hours):
#         return jsonify(success=False, message="這筆任務目前不能回報"), 400

#     return jsonify(success=True, start_time=start_time, end_time=end_time, actual_hours=actual_hours)
