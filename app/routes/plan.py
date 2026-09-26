from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort, session, flash, jsonify

from app.services.date_service import get_day_status
from app.repositories.mission_repo import (
    get_missions_by_date, get_next_mission_no, insert_mission,
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

    missions = [m for m in get_missions_by_date(user_id, mission_date) if not m["is_added"]]
    editable = status in ("today", "future")

    return render_template("plan.html", mission_date=mission_date, status=status,
                            missions=missions, editable=editable)


# @plan_bp.route("/plan/<date_str>/update", methods=["POST"])
# @login_required
# def update_missions(date_str):
#     """處理表格裡『既有任務的更新』跟『新增列的寫入』，刪除已經在下面那個路由即時處理過了。"""
#     user_id = session["user_id"]
#     mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     if get_day_status(mission_date) == "past":
#         abort(403)

#     row_ids = request.form.get("row_ids", "")
#     for row_id in row_ids.split(","):
#         if not row_id:
#             continue

#         name = request.form.get(f"mission_name_{row_id}", "").strip()
#         hours = request.form.get(f"estimated_hours_{row_id}", "").strip()
#         if not name or not hours:
#             continue  # JS已經擋過一次了，這裡是後端第二層保險，不能只信任前端

#         if row_id.startswith("new_"):
#             insert_mission({
#                 "user_id": user_id,
#                 "mission_date": mission_date,
#                 "mission_no": get_next_mission_no(user_id, mission_date),
#                 "segment_no": 1,
#                 "mission_name": name,
#                 "estimated_hours": hours,
#                 "start_time": None, "end_time": None, "actual_hours": None,
#                 "is_finished": 0, "is_long_term": 0, "is_added": 0,
#                 "project_id": None, "notfinished_mission_id": None,
#             })
#         else:
#             update_mission_plan(user_id, int(row_id), name, hours)

#     flash("任務安排已更新！")
#     return redirect(url_for("plan.plan", date_str=date_str))

@plan_bp.route("/plan/<date_str>/mission/add", methods=["POST"])
@login_required
def add_mission_ajax(date_str):
    """新增一筆任務(AJAX版)，回傳新產生的mission_id跟mission_no給前端更新畫面用。"""
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
        "mission_date": mission_date,
        "mission_no": mission_no,
        "segment_no": 1,
        "mission_name": name,
        "estimated_hours": hours,
        "start_time": None, "end_time": None, "actual_hours": None,
        "is_finished": 0, "is_long_term": 0, "is_added": 0,
        "project_id": None, "notfinished_mission_id": None,
    })
    return jsonify(success=True, mission_id=mission_id, mission_no=mission_no)


@plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/update", methods=["POST"])
@login_required
def update_mission_ajax(date_str, mission_id):
    """更新單一筆既有任務(AJAX版)。"""
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) == "past":
        return jsonify(success=False, message="過去的日期不能修改"), 403

    name = request.form.get("mission_name", "").strip()
    hours = request.form.get("estimated_hours", "").strip()
    if not name or not hours:
        return jsonify(success=False, message="任務名稱與預計耗時不能空白"), 400

    update_mission_plan(user_id, mission_id, name, hours)
    return jsonify(success=True)


@plan_bp.route("/plan/<date_str>/mission/<int:mission_id>/delete", methods=["POST"])
@login_required
def delete_mission_ajax(date_str, mission_id):
    """專門給JS用fetch呼叫，回傳JSON而不是redirect——這樣按下去才能立刻生效，不用整頁重整。"""
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) == "past":
        return jsonify(success=False, message="過去的日期不能刪除"), 403

    delete_mission(user_id, mission_id)
    return jsonify(success=True)