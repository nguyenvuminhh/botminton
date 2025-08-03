from datetime import date
from pydantic import BaseModel, model_validator

class PersonalPeriodMoney(BaseModel):
    person_id: str
    telegram_user_name: str
    period_money: float

    @model_validator(mode='after')
    def round_period_money(cls, model):
        model.period_money = round(model.period_money, 2)
        return model

class PeriodMoneyReport(BaseModel):
    period_start_date: date
    period_end_date: date
    period_id: str
    personal_period_money: list[PersonalPeriodMoney]
    total_period_money: float

    @model_validator(mode='after')
    def round_and_validate_total(cls, model):
        model.total_period_money = round(model.total_period_money, 2)
        total = sum(person.period_money for person in model.personal_period_money)
        if round(total, 2) != model.total_period_money:
            raise ValueError("total_period_money does not match sum of personal_period_money")
        return model

if __name__ == "__main__":
    # Example usage
    report = PeriodMoneyReport(
        period_start_date=date(2023, 1, 1),
        period_end_date=date(2023, 1, 31),
        period_id="1",
        personal_period_money=[
            PersonalPeriodMoney(person_id="1", telegram_user_name="user1", period_money=100.999),
            PersonalPeriodMoney(person_id="2", telegram_user_name="user2", period_money=200.0),
        ],
        total_period_money=300.999
    )
    print(report)
