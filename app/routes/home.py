from datetime import date
from flask import Blueprint, render_template

from app.services.date_service import get_week_dates, get_day_status
from app.repositories.mission_repo import get_missions_in_range

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    today = date.today()
    week_dates = get_week_dates(today)
    missions = get_missions_in_range(week_dates[0], week_dates[-1])

    # 把撈出來的任務依日期分組，方便樣板逐天判斷「有沒有資料」
    missions_by_date = {}
    for m in missions:
        missions_by_date.setdefault(m["mission_date"], []).append(m)

    week_rows = [
        {
            "date": d,
            "status": get_day_status(d, today),
            "has_data": d in missions_by_date,
        }
        for d in week_dates
    ]

    return render_template("index.html", today=today, week_rows=week_rows)