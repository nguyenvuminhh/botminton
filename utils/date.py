from datetime import date, timedelta

def format_to_dd_mm(dt: date) -> str:
    """Format a date to 'dd/mm' (day/month) format."""
    return f"{dt.day:02d}/{dt.month:02d}"


def get_next_day(today: date, target_day_index: int) -> date:
    days_ahead = (target_day_index - today.weekday() + 7) % 7
    days_ahead = 7 if days_ahead == 0 else days_ahead  # skip today if same
    return today + timedelta(days=days_ahead)
