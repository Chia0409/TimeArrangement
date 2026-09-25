from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort

from app.services.date_service import get_day_status
from app.repositories.mission_repo import get_missions_by_date, get_next_mission_no, insert_mission

plan_bp = Blueprint("plan", __name__)


@plan_bp.route("/plan/<date_str>", methods=["GET", "POST"])
def plan(date_str):
    mission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    status = get_day_status(mission_date)

    if request.method == "POST":
        if status == "past":
            abort(403)  # 對照流程圖：過去的日期「開放進入但不可編輯」，這裡擋掉寫入

        insert_mission({
            "mission_date": mission_date,
            "mission_no": get_next_mission_no(mission_date),
            "segment_no": 1,
            "mission_name": request.form["mission_name"],
            "estimated_hours": request.form["estimated_hours"],
            "start_time": None,
            "end_time": None,
            "actual_hours": None,
            "is_finished": 0,
            "is_long_term": 0,
            "is_added": 0,
            "project_id": None,
            "notfinished_mission_id": None,
        })
        return redirect(url_for("plan.plan", date_str=date_str))

    missions = [m for m in get_missions_by_date(mission_date) if not m["is_added"]]
    editable = status in ("today", "future")

    return render_template(
        "plan.html",
        mission_date=mission_date,
        status=status,
        missions=missions,
        editable=editable,
    )