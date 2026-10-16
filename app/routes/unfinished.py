from datetime import date
from flask import Blueprint, render_template, request, session, jsonify

from app.repositories.unfinished_repo import get_open_unfinished_list, close_unfinished
from app.services.auth_service import login_required

unfinished_bp = Blueprint("unfinished", __name__)


@unfinished_bp.route("/unfinished")
@login_required
def unfinished_page():
    return render_template("unfinished.html", items=get_open_unfinished_list(session["user_id"]))


@unfinished_bp.route("/unfinished/<int:mission_id>/close", methods=["POST"])
@login_required
def close_mission(mission_id):
    closed_reason = request.form.get("closed_reason", "").strip()
    ok, error = close_unfinished(session["user_id"], mission_id, date.today(), closed_reason)
    if not ok:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True)