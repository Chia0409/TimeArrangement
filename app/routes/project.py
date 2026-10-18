from datetime import datetime
from flask import Blueprint, render_template, request, session, jsonify

from app.repositories.project_repo import (
    create_project_with_stages, get_projects_overview, get_project, get_project_stages,
    add_stage, resolve_stage, close_stage, resolve_project, close_project,
)
from app.repositories.stage_mission_repo import get_stage_missions, get_assignable_missions, assign_mission_to_stage
from app.services.auth_service import login_required


project_bp = Blueprint("project", __name__)


@project_bp.route("/projects")
@login_required
def projects_page():
    return render_template("projects.html", projects=get_projects_overview(session["user_id"]))


@project_bp.route("/projects/create", methods=["POST"])
@login_required
def create_project():
    user_id = session["user_id"]
    name = request.form.get("project_name", "").strip()
    category = request.form.get("category", "").strip() or None
    start_date_str = request.form.get("start_date", "")
    stage_names = request.form.getlist("stage_name")
    stage_days = request.form.getlist("stage_estimate_days")

    if not name or not start_date_str or not stage_names:
        return jsonify(success=False, message="專案名稱、開始日期、至少一個階段都必填"), 400

    stages = []
    for n, d in zip(stage_names, stage_days):
        n = n.strip()
        if not n or not d.strip():
            return jsonify(success=False, message="每個階段的名稱與預估天數都要填"), 400
        stages.append({"stage_name": n, "estimate_days": int(d)})

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    project_id = create_project_with_stages(user_id, name, category, start_date, stages)
    return jsonify(success=True, project_id=project_id)


@project_bp.route("/projects/<int:project_id>/stage/add", methods=["POST"])
@login_required
def add_stage_ajax(project_id):
    name = request.form.get("stage_name", "").strip()
    days = request.form.get("estimate_days", "").strip()
    if not name or not days:
        return jsonify(success=False, message="階段名稱與預估天數不能空白"), 400
    add_stage(session["user_id"], project_id, name, int(days))
    return jsonify(success=True)


@project_bp.route("/projects/<int:project_id>/stage/<int:stage_id>/resolve", methods=["POST"])
@login_required
def resolve_stage_ajax(project_id, stage_id):
    ok, error = resolve_stage(session["user_id"], project_id, stage_id, request.form.get("delay_reason", "").strip())
    if not ok:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True)


@project_bp.route("/projects/<int:project_id>/stage/<int:stage_id>/close", methods=["POST"])
@login_required
def close_stage_ajax(project_id, stage_id):
    ok, error = close_stage(session["user_id"], project_id, stage_id, request.form.get("closed_reason", "").strip())
    if not ok:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True)


@project_bp.route("/projects/<int:project_id>/resolve", methods=["POST"])
@login_required
def resolve_project_ajax(project_id):
    ok, error = resolve_project(session["user_id"], project_id, request.form.get("delay_reason", "").strip())
    if not ok:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True)


@project_bp.route("/projects/<int:project_id>/close", methods=["POST"])
@login_required
def close_project_ajax(project_id):
    ok, error = close_project(session["user_id"], project_id, request.form.get("closed_reason", "").strip())
    if not ok:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True)


@project_bp.route("/projects/stage/<int:stage_id>/missions")
@login_required
def stage_missions_api(stage_id):
    user_id = session["user_id"]
    items = get_stage_missions(user_id, stage_id)
    assignable = get_assignable_missions(user_id)
    return jsonify(
        items=[{
            "mission_id": m["mission_id"], "mission_name": m["mission_name"],
            "mission_start_date": m["mission_start_date"].strftime("%Y/%m/%d"),
            "mission_finish_date": m["mission_finish_date"].strftime("%Y/%m/%d") if m["mission_finish_date"] else "-",
            "status": m["status"],
        } for m in items],
        assignable=[{"mission_id": a["mission_id"], "mission_name": a["mission_name"]} for a in assignable],
    )


@project_bp.route("/projects/stage/<int:stage_id>/assign", methods=["POST"])
@login_required
def assign_mission_ajax(stage_id):
    mission_id = request.form.get("mission_id", "")
    if not mission_id.isdigit():
        return jsonify(success=False, message="請選擇一個任務"), 400
    if not assign_mission_to_stage(session["user_id"], stage_id, int(mission_id)):
        return jsonify(success=False, message="這個任務已經被歸類過了"), 400
    return jsonify(success=True)
@project_bp.route("/projects/<int:project_id>/stages")
@login_required
def project_stages_api(project_id):
    user_id = session["user_id"]
    stages = get_project_stages(user_id, project_id)
    return jsonify(items=[
        {
            "project_stage_id": s["project_stage_id"],
            "stage_no": s["stage_no"],
            "stage_name": s["stage_name"],
            "status": s["status"],
            "estimate_days": s["estimate_days"],
            "start_date": s["start_date"].strftime("%Y/%m/%d"),
            "estimated_finish_date": s["estimated_finish_date"].strftime("%Y/%m/%d") if s["estimated_finish_date"] else "-",
            "actual_finish_date": s["actual_finish_date"].strftime("%Y/%m/%d") if s["actual_finish_date"] else "-",
            # 這三個數字來自SQL的COUNT()/SUM()，PyMySQL讀回來常常是Decimal不是int，
            # jsonify沒辦法把Decimal轉成JSON，這裡先明確轉型，不然會直接500
            "mission_count": int(s["mission_count"]),
            "finished_count": int(s["finished_count"]),
            "unfinished_count": int(s["unfinished_count"]),
        }
        for s in stages
    ])

# # the added for not causing the ImportError
# def name_taken(user_id, project_name, exclude_id=None):
#     """這個人「進行中」的長期任務裡，有沒有同名的。
#     exclude_id用來排除自己：專案id從1開始，傳0(None時)就等於誰都不排除。"""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(
#             """SELECT 1 FROM project
#                WHERE user_id = %s AND project_name = %s AND is_finished = 0
#                  AND project_id <> %s
#                LIMIT 1""",
#             (user_id, project_name, exclude_id or 0),
#         )
#         return cur.fetchone() is not None