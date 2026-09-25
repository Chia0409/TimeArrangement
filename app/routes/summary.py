from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort, flash

from app.services.date_service import get_day_status, calc_actual_hours
from app.repositories.mission_repo import (
    get_missions_by_date, get_next_mission_no, insert_mission,
    update_mission_summary, delete_mission,
)

summary_bp = Blueprint("summary", __name__)


def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


@summary_bp.route("/summary/<date_str>")
def summary(date_str):
    mission_date = _parse_date(date_str)
    status = get_day_status(mission_date)

    if status == "future":
        # 對照流程圖：大於當天 → 任務總結不開放進入
        return render_template(
            "summary.html", mission_date=mission_date, status=status,
            block1=[], block2=[], can_edit_block1=False, can_edit_block2=False,
        )

    all_missions = get_missions_by_date(mission_date)
    block1 = [m for m in all_missions if not m["is_added"]]
    block2 = [m for m in all_missions if m["is_added"]]

    return render_template(
        "summary.html",
        mission_date=mission_date, status=status,
        block1=block1, block2=block2,
        can_edit_block1=(status == "today"),          # 過去：區塊一唯讀
        can_edit_block2=(status in ("today", "past")), # 過去：僅區塊二可編修
    )


@summary_bp.route("/summary/<date_str>/update/<int:mission_id>", methods=["POST"])
def update_block1(date_str, mission_id):
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) != "today":
        abort(403)  # 後端再擋一次：只有今天能改區塊一，不管前端表單有沒有被藏起來

    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    is_finished = 1 if request.form.get("is_finished") else 0
    actual_hours = calc_actual_hours(start_time, end_time)

    # update_mission_summary(mission_id, start_time, end_time, actual_hours, is_finished)
    # return redirect(url_for("summary.summary", date_str=date_str))
    update_mission_summary(mission_id, start_time, end_time, actual_hours, is_finished)
    flash("已儲存！")
    return redirect(url_for("summary.summary", date_str=date_str))


@summary_bp.route("/summary/<date_str>/add", methods=["POST"])
def add_block2(date_str):
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) not in ("today", "past"):
        abort(403)

    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    insert_mission({
        "mission_date": mission_date,
        "mission_no": get_next_mission_no(mission_date),
        "segment_no": 1,
        "mission_name": request.form["mission_name"],
        "estimated_hours": 0,
        "start_time": start_time,
        "end_time": end_time,
        "actual_hours": calc_actual_hours(start_time, end_time),
        "is_finished": 1,
        "is_long_term": 0,
        "is_added": 1,          # 這裡就是「區塊二」的關鍵標記
        "project_id": None,
        "notfinished_mission_id": None,
    })
    # add_block2 裡，insert_mission(...) 下面
    flash("已新增追加任務！")
    return redirect(url_for("summary.summary", date_str=date_str))



@summary_bp.route("/summary/<date_str>/delete/<int:mission_id>", methods=["POST"])
def delete_block2(date_str, mission_id):
    mission_date = _parse_date(date_str)
    if get_day_status(mission_date) not in ("today", "past"):
        abort(403)

    delete_mission(mission_id)
    # delete_block2 裡，delete_mission(...) 下面
    flash("已刪除！")
    return redirect(url_for("summary.summary", date_str=date_str))