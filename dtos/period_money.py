from datetime import date
from pydantic import BaseModel, field_validator

# Example model using BaseModel
class PersonalPeriodMoney(BaseModel):
    person_id: int
    telegram_user_name: str
    period_money: float

    @field_validator('period_money')
    def round_period_money(cls, v):
        return round(v, 2)
    
class PeriodMoneyReport(BaseModel):
    period_start_date: date
    period_end_date: date
    period_id: int
    personal_period_money: list[PersonalPeriodMoney]
    total_period_money: float

    @field_validator('total_period_money')
    def round_total_period_money(cls, v):
        return round(v, 2)
    
    @field_validator('total_period_money', mode='before')
    def validate_and_recalculate_total(cls, v, values):
        personal_list = values.get('personal_period_money')
        total = sum(person.period_money for person in personal_list)
        if round(total, 2) != round(v, 2):
            raise ValueError("total_period_money does not match sum of personal_period_money")
        return round(v, 2)