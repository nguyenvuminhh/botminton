from models.period_money import PeriodMoneyReport
from utils.date import format_to_dd_mm


def get_money_message(period_money_report: PeriodMoneyReport) -> str:
    period_start_date_str = format_to_dd_mm(period_money_report.period_start_date)
    period_end_date_str = format_to_dd_mm(period_money_report.period_end_date)
    message = f"Em gửi tiền sân từ {period_start_date_str} đến {period_end_date_str} ạ\n\n"

    for person in period_money_report.personal_period_money:
        message += f"{person.telegram_user_name} {person.period_money}\n"
    return message

def get_react_after_sending_money_message() -> str:
    return "Ai gửi rồi thì react tin nhắn này giúp em ạ"