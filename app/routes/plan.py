from datetime import datetime, date
from flask import Blueprint, render_template, request, session, jsonify

from app.services.date_service import get_day_status, calc_actual_hours
from app.repositories.mission_repo import get_created_missions, get_next_mission_no, insert_mission, update_mission_plan, delete_mission
from app.repositories.unfinished_repo import get_open_unfinished_missions, import_mission
from app.services.auth_service import login_required

plan_bp = Blueprint("plan", __name__)


def _hours(start_time, end_time):
    return calc_actual_hours(start_time, end_time) if start_time and end_time else None


@plan_bp.route("/plan/<date_str>")
@login_required
def plan(date_str):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    status = get_day_status(mission_date)

    missions = get_created_missions(user_id, mission_date)
    editable = status in ("today", "future")
    open_unfinished = get_open_unfinished_missions(user_id) if status == "today" else []

    return render_template("plan.html", mission_date=mission_date, status=status,
                            missions=missions, editable=editable, open_unfinished=open_unfinished)


@plan_bp.route("/plan/<date_str>/mission/add", methods=["POST"])
@login_required
def add_mission_ajax(date_str):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) == "past":
        return jsonify(success=False, message="過去的日期不能新增"), 403

    name = request.form.get("mission_name", "").strip()
    start_time = request.form.get("start_time") or None
    end_time = request.form.get("end_time") or None
    if not name or not start_time or not end_time:
        return jsonify(success=False, message="任務名稱、預計開始與結束時間不能空白"), 400

    hours = _hours(start_time, end_time)
    if hours is None:
        return jsonify(success=False, message="結束時間必須晚於開始時間"), 400

    category = request.form.get("category", "").strip() or None
    stage_id = request.form.get("project_stage_id", "")
    project_stage_id = int(stage_id) if stage_id.isdigit() else None

    mission_no = get_next_mission_no(user_id, mission_date)
    mission_id = insert_mission({
        "user_id": user_id, "mission_start_date": mission_date, "mission_no": mission_no,
        "mission_name": name, "category": category, "estimated_hours": hours,
        "start_time": start_time, "end_time": end_time, "is_added": 0, "project_stage_id": project_stage_id,
    })
    return jsonify(success=True, mission_id=mission_id, mission_no=mission_no)


@plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/update", methods=["POST"])
@login_required
def update_mission_ajax(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) == "past":
        return jsonify(success=False, message="過去的日期不能修改"), 403

    name = request.form.get("mission_name", "").strip()
    start_time = request.form.get("start_time") or None
    end_time = request.form.get("end_time") or None
    if not name or not start_time or not end_time:
        return jsonify(success=False, message="任務名稱、預計開始與結束時間不能空白"), 400

    hours = _hours(start_time, end_time)
    if hours is None:
        return jsonify(success=False, message="結束時間必須晚於開始時間"), 400

    category = request.form.get("category", "").strip() or None
    stage_id = request.form.get("project_stage_id", "")
    project_stage_id = int(stage_id) if stage_id.isdigit() else None

    if not update_mission_plan(user_id, mission_id, name, hours, start_time, end_time, category, project_stage_id):
        return jsonify(success=False, message="這筆任務目前不能編輯"), 400
    return jsonify(success=True)


# @plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/delete", methods=["POST"])
# @login_required
# def delete_mission_ajax(date_str, mission_id):
#     user_id = session["user_id"]
#     mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     if get_day_status(mission_date) == "past":
#         return jsonify(success=False, message="過去的日期不能刪除"), 403
#     if not delete_mission(user_id, mission_id):
#         return jsonify(success=False, message="這筆任務目前不能刪除"), 400
#     return jsonify(success=True)

@plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/delete", methods=["POST"])
@login_required
def delete_mission_ajax(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) == "past":
        return jsonify(success=False, message="過去的日期不能刪除"), 403

    success, reverted = delete_mission(user_id, mission_id)
    if not success:
        return jsonify(success=False, message="這筆任務目前不能刪除"), 400
    return jsonify(success=True, reverted=reverted)

@plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/import", methods=["POST"])
@login_required
def import_mission_ajax(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) != "today":
        return jsonify(success=False, message="只有今天能匯入未完成任務"), 403

    category = request.form.get("category", "").strip() or None
    stage_id = request.form.get("project_stage_id", "")
    project_stage_id = int(stage_id) if stage_id.isdigit() else None

    ok, error = import_mission(user_id, mission_id, date.today(), category, project_stage_id)
    if not ok:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True)

# from datetime import datetime, date
# from flask import Blueprint, render_template, request, session, jsonify

# from app.services.date_service import get_day_status
# from app.repositories.mission_repo import (
#     get_created_missions, get_next_mission_no, insert_mission,
#     update_mission_plan, delete_mission,
# )
# from app.services.auth_service import login_required

# from app.repositories.unfinished_repo import get_open_unfinished_missions, import_continue, import_resolve
# from app.services.date_service import get_day_status, calc_actual_hours

# plan_bp = Blueprint("plan", __name__)


# @plan_bp.route("/plan/<date_str>")
# @login_required
# def plan(date_str):
#     user_id = session["user_id"]
#     mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     status = get_day_status(mission_date)

#     missions = get_created_missions(user_id, mission_date)
#     editable = status in ("today", "future")
#     # 匯入只在「今天」才有意義，過去/未來的計畫頁不顯示這塊
#     open_unfinished = get_open_unfinished_missions(user_id) if status == "today" else []

#     return render_template("plan.html", mission_date=mission_date, status=status,
#                             missions=missions, editable=editable, open_unfinished=open_unfinished)

# @plan_bp.route("/plan/<date_str>/mission/add", methods=["POST"])
# @login_required
# def add_mission_ajax(date_str):
#     user_id = session["user_id"]
#     mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     if get_day_status(mission_date) == "past":
#         return jsonify(success=False, message="過去的日期不能新增"), 403

#     name = request.form.get("mission_name", "").strip()
#     hours = request.form.get("estimated_hours", "").strip()
#     if not name or not hours:
#         return jsonify(success=False, message="任務名稱與預計耗時不能空白"), 400

#     mission_no = get_next_mission_no(user_id, mission_date)
#     mission_id = insert_mission({
#         "user_id": user_id,
#         "mission_start_date": mission_date,
#         "mission_no": mission_no,
#         "mission_name": name,
#         "category": None,
#         "estimated_hours": hours,
#         "is_added": 0,
#         "project_stage_id": None,
#     })
#     return jsonify(success=True, mission_id=mission_id, mission_no=mission_no)


# @plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/update", methods=["POST"])
# @login_required
# def update_mission_ajax(date_str, mission_id):
#     user_id = session["user_id"]
#     mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     if get_day_status(mission_date) == "past":
#         return jsonify(success=False, message="過去的日期不能修改"), 403

#     name = request.form.get("mission_name", "").strip()
#     hours = request.form.get("estimated_hours", "").strip()
#     if not name or not hours:
#         return jsonify(success=False, message="任務名稱與預計耗時不能空白"), 400

#     if not update_mission_plan(user_id, mission_id, name, hours):
#         return jsonify(success=False, message="這筆任務目前不能編輯"), 400
#     return jsonify(success=True)


# @plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/delete", methods=["POST"])
# @login_required
# def delete_mission_ajax(date_str, mission_id):
#     user_id = session["user_id"]
#     mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     if get_day_status(mission_date) == "past":
#         return jsonify(success=False, message="過去的日期不能刪除"), 403

#     if not delete_mission(user_id, mission_id):
#         return jsonify(success=False, message="這筆任務目前不能刪除"), 400
#     return jsonify(success=True)

# @plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/import", methods=["POST"])
# @login_required
# def import_mission_ajax(date_str, mission_id):
#     user_id = session["user_id"]
#     mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     if get_day_status(mission_date) != "today":
#         return jsonify(success=False, message="只有今天能匯入未完成任務"), 403

#     outcome = request.form.get("outcome")
#     start_time = request.form.get("start_time") or None
#     end_time = request.form.get("end_time") or None
#     actual_hours = calc_actual_hours(start_time, end_time) if start_time and end_time else None
#     today = date.today()

#     if outcome == "continue":
#         if not import_continue(user_id, mission_id, today, start_time, end_time, actual_hours):
#             return jsonify(success=False, message="找不到這筆未完成任務"), 400
#         return jsonify(success=True)

#     if outcome == "resolved":
#         delay_reason = request.form.get("delay_reason", "").strip()
#         ok, error = import_resolve(user_id, mission_id, today, start_time, end_time, actual_hours, delay_reason)
#         if not ok:
#             return jsonify(success=False, message=error), 400
#         return jsonify(success=True)

#     return jsonify(success=False, message="狀態錯誤"), 400