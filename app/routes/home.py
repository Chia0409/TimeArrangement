from datetime import date
from flask import Blueprint, render_template, redirect, url_for, session

from app.services.date_service import get_week_dates, get_day_status, get_month_weeks
from app.repositories.mission_repo import get_active_dates_in_range
from app.services.auth_service import login_required

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
@login_required
def index():
    user_id = session["user_id"]
    today = date.today()
    week_dates = get_week_dates(today)
    active_dates = get_active_dates_in_range(user_id, week_dates[0], week_dates[-1])

    week_rows = [
        {"date": d, "status": get_day_status(d, today), "has_data": d in active_dates}
        for d in week_dates
    ]
    return render_template("index.html", today=today, week_rows=week_rows)


@home_bp.route("/calendar")
@login_required
def calendar_view():
    today = date.today()
    return redirect(url_for("home.calendar_month", year=today.year, month=today.month))


@home_bp.route("/calendar/<int:year>/<int:month>")
@login_required
def calendar_month(year, month):
    user_id = session["user_id"]
    today = date.today()

    weeks = get_month_weeks(year, month)
    active_dates = get_active_dates_in_range(user_id, weeks[0][0], weeks[-1][-1])

    calendar_weeks = [
        [
            {
                "date": d,
                "is_current_month": d.month == month,
                "is_today": d == today,
                "has_data": d in active_dates,
                "status": get_day_status(d, today),
            }
            for d in week
        ]
        for week in weeks
    ]

    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    return render_template(
        "calendar.html", year=year, month=month, calendar_weeks=calendar_weeks,
        prev_year=prev_year, prev_month=prev_month,
        next_year=next_year, next_month=next_month,
    )