from datetime import date
from flask import Blueprint, render_template, request, session, jsonify
from app.repositories.notfinished_repo import report_overdue_mission
from app.repositories.project_repo import (
    get_projects_with_stats, get_project, name_taken, create_project,
    rename_project, set_project_finished, count_project_missions, delete_project,
    get_project_missions
)
from app.services.auth_service import login_required


project_bp = Blueprint("project", __name__)


@project_bp.route("/projects")
@login_required
def projects_page():
    return render_template("projects.html", projects=get_projects_with_stats(session["user_id"]))
def _fmt_time(t):
    """跟summary.py裡那個同名函式做一樣的事：MySQL的TIME被PyMySQL讀成timedelta，
    轉成HH:MM給前端用。這裡重複寫一份而不是去改summary.py共用，
    是不想為了這個小功能去動到已經測試過、正常運作的既有程式碼。"""
    if t is None:
        return ""
    minutes = int(t.total_seconds() // 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

@project_bp.route("/projects/<int:project_id>/missions")
@login_required
def project_missions_api(project_id):
    user_id = session["user_id"]
    if get_project(user_id, project_id) is None:
        return jsonify(items=[]), 404

    items = []
    for m in get_project_missions(user_id, project_id):
        if m["is_finished"] is None:
            status_label, adjust_mode = "尚未回報", "pending"
        elif m["is_finished"] == 1:
            status_label, adjust_mode = "完成", None
        elif m["tracking_status"] == "closed":
            status_label, adjust_mode = "強制結束", None
        else:
            status_label = "忘記回報" if m["is_auto_closed"] else "沒做完"
            adjust_mode = "open"

        items.append({
            "mission_id": m["mission_id"],
            "notfinished_mission_id": m["notfinished_mission_id"],
            "mission_name": m["mission_name"],
            "mission_date": m["mission_date"].strftime("%Y/%m/%d"),
            "start_time": _fmt_time(m["start_time"]),
            "end_time": _fmt_time(m["end_time"]),
            "actual_hours": m["actual_hours"] if m["actual_hours"] is not None else "-",
            "status_label": status_label,
            "adjust_mode": adjust_mode,
            "is_auto_closed": bool(m["is_auto_closed"]),
        })
    return jsonify(items=items)


@project_bp.route("/projects/mission/<int:mission_id>/report", methods=["POST"])
@login_required
def report_mission(mission_id):
    final_status = request.form.get("final_status")
    if final_status not in ("resolved", "closed"):
        return jsonify(success=False, message="狀態錯誤"), 400
    reason = request.form.get("reason", "").strip() or None

    ok, error = report_overdue_mission(session["user_id"], mission_id, final_status, reason)
    if not ok:
        return jsonify(success=False, message=error), 400
    return jsonify(success=True)

@project_bp.route("/projects/add", methods=["POST"])
@login_required
def add_project():
    user_id = session["user_id"]
    name = request.form.get("project_name", "").strip()
    if not name:
        return jsonify(success=False, message="長期任務名稱不能空白"), 400
    if name_taken(user_id, name):
        return jsonify(success=False, message="已經有同名的進行中長期任務了"), 400

    today = date.today()
    new_id = create_project(user_id, name, today)
    return jsonify(success=True, project_id=new_id, start_date=today.strftime("%Y/%m/%d"))


@project_bp.route("/projects/<int:project_id>/update", methods=["POST"])
@login_required
def update_project(project_id):
    user_id = session["user_id"]
    name = request.form.get("project_name", "").strip()
    if not name:
        return jsonify(success=False, message="長期任務名稱不能空白"), 400
    if get_project(user_id, project_id) is None:
        return jsonify(success=False, message="找不到這個長期任務"), 404
    if name_taken(user_id, name, exclude_id=project_id):
        return jsonify(success=False, message="已經有同名的進行中長期任務了"), 400

    rename_project(user_id, project_id, name)
    return jsonify(success=True)


@project_bp.route("/projects/<int:project_id>/toggle", methods=["POST"])
@login_required
def toggle_project(project_id):
    user_id = session["user_id"]
    project = get_project(user_id, project_id)
    if project is None:
        return jsonify(success=False, message="找不到這個長期任務"), 404

    finish = request.form.get("finish") == "1"
    # 重新開啟時，若已有同名的進行中專案，就會撞名，要擋下來
    if not finish and name_taken(user_id, project["project_name"], exclude_id=project_id):
        return jsonify(success=False, message="已有同名的進行中長期任務，請先改名再重新開啟"), 400

    set_project_finished(user_id, project_id, finish, date.today())
    return jsonify(success=True, is_finished=1 if finish else 0)


@project_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def remove_project(project_id):
    user_id = session["user_id"]
    used = count_project_missions(user_id, project_id)
    if used > 0:
        return jsonify(success=False,
                       message=f"已有 {used} 筆任務記錄使用這個長期任務，無法刪除，請改用「標記完成」"), 400

    delete_project(user_id, project_id)
    return jsonify(success=True)