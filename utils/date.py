from datetime import date, timedelta

def format_to_dd_mm(dt: date) -> str:
    """Format a date to 'dd/mm' (day/month) format."""
    return f"{dt.day:02d}/{dt.month:02d}"


def get_next_day(today: date, target_day_index: int) -> date:
    days_ahead = (target_day_index - today.weekday() + 7) % 7
    days_ahead = 7 if days_ahead == 0 else days_ahead  # skip today if same
    return today + timedelta(days=days_ahead)

if __name__ == "__main__":
    # Example usage
    today = date.today()
    next_monday = get_next_day(today, 0)  # 0 for Monday
    next_tuesday = get_next_day(today, 1)  # 1 for Tuesday
    next_wednesday = get_next_day(today, 2)  # 2 for Wednesday
    next_thursday = get_next_day(today, 3)   # 3 for Thursday
    next_friday = get_next_day(today, 4)     # 4 for Friday
    next_saturday = get_next_day(today, 5)   # 5 for Saturday
    next_sunday = get_next_day(today, 6)     # 6 for Sunday

    print("Today", format_to_dd_mm(today))

    print("Next Monday", format_to_dd_mm(next_monday))
    print("Next Tuesday", format_to_dd_mm(next_tuesday))
    print("Next Wednesday", format_to_dd_mm(next_wednesday))
    print("Next Thursday", format_to_dd_mm(next_thursday))
    print("Next Friday", format_to_dd_mm(next_friday))
    print("Next Saturday", format_to_dd_mm(next_saturday))
    print("Next Sunday", format_to_dd_mm(next_sunday))