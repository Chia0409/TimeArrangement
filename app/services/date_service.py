from datetime import date, timedelta, datetime
import calendar

def get_day_status(target_date, today=None):
    """比較目標日期跟今天：回傳 'past' / 'today' / 'future'。"""
    if today is None:
        today = date.today()
    if target_date < today:
        return "past"
    elif target_date == today:
        return "today"
    else:
        return "future"


def get_week_dates(target_date):
    """回傳 target_date 那一週的7天日期(週日排到週六)，對應你Excel表格的排法。"""
    days_since_sunday = (target_date.weekday() + 1) % 7   # weekday(): 週一=0...週日=6，換算成「離週日幾天」
    week_start = target_date - timedelta(days=days_since_sunday)
    return [week_start + timedelta(days=i) for i in range(7)]


# def calc_actual_hours(start_time_str, end_time_str):
#     """輸入 'HH:MM' 字串，算出結束-開始的時數，交給Python算(你上次選的方案)，不靠資料庫。"""
#     fmt = "%H:%M"
#     start = datetime.strptime(start_time_str, fmt)
#     end = datetime.strptime(end_time_str, fmt)
#     delta = end - start
#     return round(delta.total_seconds() / 3600, 2)

def calc_actual_hours(start_time_str, end_time_str):
    """輸入 'HH:MM' 或 'HH:MM:SS' 字串都可以，算出結束-開始的時數。
    不同瀏覽器的 <input type="time"> 傳回來的格式不太一樣（Safari有時會多帶秒數），
    所以改成手動拆字串取「時、分」，不依賴strptime的固定格式，比較保險。"""
    def to_minutes(t):
        parts = t.split(":")
        hour, minute = int(parts[0]), int(parts[1])   # 只取前兩段，第三段(秒)有沒有都不影響
        return hour * 60 + minute

    diff_minutes = to_minutes(end_time_str) - to_minutes(start_time_str)
    return round(diff_minutes / 60, 2)

def get_month_weeks(year, month):
    """回傳該月份的完整月曆網格：一個list，每個元素是一週(7個date物件)。
    會自動補上前一個月末尾、下一個月開頭的日期湊滿整週(對照你截圖裡灰色的30日、10月1日)，
    firstweekday=SUNDAY讓每週從週日開始，對齊Google/Mac日曆的排法。"""
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    all_dates = list(cal.itermonthdates(year, month))
    return [all_dates[i:i + 7] for i in range(0, len(all_dates), 7)]