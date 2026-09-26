from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort, session, flash

from app.services.date_service import get_day_status
from app.repositories.mission_repo import (
    get_missions_by_date, get_next_mission_no, insert_mission, update_mission_plan, delete_mission,
)
from app.services.auth_service import login_required

plan_bp = Blueprint("plan", __name__)


@plan_bp.route("/plan/<date_str>", methods=["GET", "POST"])
@login_required
def plan(date_str):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    status = get_day_status(mission_date)

    if request.method == "POST":
        if status == "past":
            abort(403)
        insert_mission({
            "user_id": user_id,
            "mission_date": mission_date,
            "mission_no": get_next_mission_no(user_id, mission_date),
            "segment_no": 1,
            "mission_name": request.form["mission_name"],
            "estimated_hours": request.form["estimated_hours"],
            "start_time": None, "end_time": None, "actual_hours": None,
            "is_finished": 0, "is_long_term": 0, "is_added": 0,
            "project_id": None, "notfinished_mission_id": None,
        })
        return redirect(url_for("plan.plan", date_str=date_str))

    # missions = [m for m in get_missions_by_date(user_id, mission_date) if not m["is_added"]]
    # editable = status in ("today", "future")
    # return render_template("plan.html", mission_date=mission_date, status=status, missions=missions, editable=editable)

    missions = [m for m in get_missions_by_date(user_id, mission_date) if not m["is_added"]]
    mission_ids_str = ",".join(str(m["mission_id"]) for m in missions)  # 新增這行
    editable = status in ("today", "future")
    return render_template(
        "plan.html", mission_date=mission_date, status=status,
        missions=missions, editable=editable, mission_ids_str=mission_ids_str,  # 多傳這個
    )

@plan_bp.route("/plan/<date_str>/update", methods=["POST"])
@login_required
def update_missions(date_str):
    user_id = session["user_id"]
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if get_day_status(mission_date) == "past":
        abort(403)

    mission_ids = request.form.get("mission_ids", "")
    for mid_str in mission_ids.split(","):
        if not mid_str:
            continue
        mission_id = int(mid_str)

        if request.form.get(f"delete_{mission_id}"):
            delete_mission(user_id, mission_id)
        else:
            update_mission_plan(
                user_id, mission_id,
                request.form.get(f"mission_name_{mission_id}"),
                request.form.get(f"estimated_hours_{mission_id}"),
            )

    flash("任務安排已更新！")
    return redirect(url_for("plan.plan", date_str=date_str))