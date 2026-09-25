from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort, session

from app.services.date_service import get_day_status
from app.repositories.mission_repo import get_missions_by_date, get_next_mission_no, insert_mission
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

    missions = [m for m in get_missions_by_date(user_id, mission_date) if not m["is_added"]]
    editable = status in ("today", "future")
    return render_template("plan.html", mission_date=mission_date, status=status, missions=missions, editable=editable)