from datetime import date
from models.period_money import PeriodMoneyReport
from utils.date import format_to_dd_mm, get_next_day

def get_day_of_the_week_name(day_index: int) -> str:
    """Get the name of the day of the week based on its index (0=Monday, 6=Sunday)."""
    days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    return days[day_index]

def get_money_message(period_money_report: PeriodMoneyReport) -> str:
    period_start_date_str = format_to_dd_mm(period_money_report.period_start_date)
    period_end_date_str = format_to_dd_mm(period_money_report.period_end_date)
    message = f"Em gửi tiền sân từ {period_start_date_str} đến {period_end_date_str} ạ\n\n"

    for person in period_money_report.personal_period_money:
        display_name = person.full_name or person.telegram_user_name
        message += f"{display_name} {person.period_money}\n"
    return message

def get_react_after_sending_money_message() -> str:
    return "Ai gửi rồi thì react tin nhắn này giúp em ạ"

def get_poll_title(start_time: str, end_time: str, location: str, day_of_the_week_index: int) -> str:
    target_day = format_to_dd_mm(get_next_day(date.today(), day_of_the_week_index))
    day_of_the_week_name = get_day_of_the_week_name(day_of_the_week_index)

    return f"{day_of_the_week_name} {target_day} {start_time} - {end_time} @ {location}"

if __name__ == "__main__":
    # Example usage
    today = date.today()
    print(get_poll_title("18:00", "20:00", "Unisport", 0))  # Example for Monday
