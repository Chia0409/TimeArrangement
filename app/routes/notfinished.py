from datetime import date
from flask import Blueprint, render_template, request, session, jsonify

from app.repositories.notfinished_repo import (
    get_open_notfinished_list, resolve_notfinished, close_notfinished, convert_to_long_term,
)
from app.services.auth_service import login_required

notfinished_bp = Blueprint("notfinished", __name__)


@notfinished_bp.route("/notfinished")
@login_required
def notfinished_page():
    return render_template("notfinished.html", items=get_open_notfinished_list(session["user_id"]))


@notfinished_bp.route("/notfinished/<int:notfinished_mission_id>/resolve", methods=["POST"])
@login_required
def resolve_mission(notfinished_mission_id):
    delayed_reason = request.form.get("delayed_reason", "").strip() or None
    resolve_notfinished(session["user_id"], notfinished_mission_id, delayed_reason)
    return jsonify(success=True)


@notfinished_bp.route("/notfinished/<int:notfinished_mission_id>/close", methods=["POST"])
@login_required
def close_mission(notfinished_mission_id):
    closed_reason = request.form.get("closed_reason", "").strip() or None
    close_notfinished(session["user_id"], notfinished_mission_id, closed_reason)
    return jsonify(success=True)


@notfinished_bp.route("/notfinished/<int:notfinished_mission_id>/convert", methods=["POST"])
@login_required
def convert_mission(notfinished_mission_id):
    project_name = request.form.get("project_name", "").strip()
    if not project_name:
        return jsonify(success=False, message="長期任務名稱不能空白"), 400

    project_id, error = convert_to_long_term(session["user_id"], notfinished_mission_id, project_name, date.today())
    if error:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True, project_id=project_id)