from datetime import date
from flask import Blueprint, render_template, request, session, jsonify

from app.repositories.notfinished_repo import (
    get_open_notfinished_list, get_processed_notfinished_list,
    set_status_resolved, set_status_closed, reopen_notfinished,
    convert_to_new_project, convert_to_existing_project,
)
from app.services.auth_service import login_required

notfinished_bp = Blueprint("notfinished", __name__)


def _fmt(d):
    return d.strftime("%Y/%m/%d") if d else None


@notfinished_bp.route("/notfinished")
@login_required
def notfinished_page():
    return render_template("notfinished.html", items=get_open_notfinished_list(session["user_id"]))


@notfinished_bp.route("/notfinished/processed")
@login_required
def processed_list_api():
    user_id = session["user_id"]
    year_month = request.args.get("year_month") or None
    pending_op = request.args.get("pending_op") or None
    raw_days = request.args.get("pending_days", "")
    pending_days = int(raw_days) if raw_days.isdigit() else None
    status = request.args.get("status") or None

    rows = get_processed_notfinished_list(user_id, year_month, pending_op, pending_days, status)
    items = [
        {
            "notfinished_mission_id": r["notfinished_mission_id"],
            "mission_name": r["mission_name"],
            "start_date": _fmt(r["start_date"]),
            "finish_date": _fmt(r["finish_date"]),
            "pending_days": r["pending_days"],
            "status": r["status"],
            "delayed_reason": r["delayed_reason"] or "",
            "closed_reason": r["closed_reason"] or "",
        }
        for r in rows
    ]
    return jsonify(items=items)


@notfinished_bp.route("/notfinished/<int:notfinished_mission_id>/resolve", methods=["POST"])
@login_required
def resolve_mission(notfinished_mission_id):
    reason = request.form.get("delayed_reason", "").strip() or None
    set_status_resolved(session["user_id"], notfinished_mission_id, reason)
    return jsonify(success=True)


@notfinished_bp.route("/notfinished/<int:notfinished_mission_id>/close", methods=["POST"])
@login_required
def close_mission(notfinished_mission_id):
    reason = request.form.get("closed_reason", "").strip() or None
    set_status_closed(session["user_id"], notfinished_mission_id, reason)
    return jsonify(success=True)


@notfinished_bp.route("/notfinished/<int:notfinished_mission_id>/reopen", methods=["POST"])
@login_required
def reopen_mission(notfinished_mission_id):
    reopen_notfinished(session["user_id"], notfinished_mission_id)
    return jsonify(success=True)


@notfinished_bp.route("/notfinished/<int:notfinished_mission_id>/convert-new", methods=["POST"])
@login_required
def convert_new(notfinished_mission_id):
    name = request.form.get("project_name", "").strip()
    if not name:
        return jsonify(success=False, message="長期任務名稱不能空白"), 400
    project_id, error = convert_to_new_project(session["user_id"], notfinished_mission_id, name, date.today())
    if error:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True, project_id=project_id)


@notfinished_bp.route("/notfinished/<int:notfinished_mission_id>/convert-existing", methods=["POST"])
@login_required
def convert_existing(notfinished_mission_id):
    raw_id = request.form.get("project_id", "")
    if not raw_id.isdigit():
        return jsonify(success=False, message="請選擇一個長期任務"), 400
    project_id, error = convert_to_existing_project(session["user_id"], notfinished_mission_id, int(raw_id), date.today())
    if error:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True, project_id=project_id)