from datetime import datetime
from flask import Blueprint, render_template, request, session, jsonify

from app.services.date_service import get_day_status
from app.repositories.mission_repo import (
    get_created_missions, get_next_mission_no, insert_mission,
    update_mission_plan, delete_mission,
)
from app.services.auth_service import login_required

plan_bp = Blueprint("plan", __name__)


@plan_bp.route("/plan/<date_str>")
@login_required
def plan(date_str):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    status = get_day_status(mission_date)

    missions = get_created_missions(user_id, mission_date)
    editable = status in ("today", "future")

    return render_template("plan.html", mission_date=mission_date, status=status,
                            missions=missions, editable=editable)


@plan_bp.route("/plan/<date_str>/mission/add", methods=["POST"])
@login_required
def add_mission_ajax(date_str):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) == "past":
        return jsonify(success=False, message="過去的日期不能新增"), 403

    name = request.form.get("mission_name", "").strip()
    hours = request.form.get("estimated_hours", "").strip()
    if not name or not hours:
        return jsonify(success=False, message="任務名稱與預計耗時不能空白"), 400

    mission_no = get_next_mission_no(user_id, mission_date)
    mission_id = insert_mission({
        "user_id": user_id,
        "mission_start_date": mission_date,
        "mission_no": mission_no,
        "mission_name": name,
        "category": None,
        "estimated_hours": hours,
        "is_added": 0,
        "project_stage_id": None,
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
    hours = request.form.get("estimated_hours", "").strip()
    if not name or not hours:
        return jsonify(success=False, message="任務名稱與預計耗時不能空白"), 400

    if not update_mission_plan(user_id, mission_id, name, hours):
        return jsonify(success=False, message="這筆任務目前不能編輯"), 400
    return jsonify(success=True)


@plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/delete", methods=["POST"])
@login_required
def delete_mission_ajax(date_str, mission_id):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) == "past":
        return jsonify(success=False, message="過去的日期不能刪除"), 403

    if not delete_mission(user_id, mission_id):
        return jsonify(success=False, message="這筆任務目前不能刪除"), 400
    return jsonify(success=True)