from mongoengine import (
    Document, FloatField, ReferenceField, BooleanField, CASCADE
)

from orms.periods import Periods
from orms.users import Users

class PeriodMoneys(Document):
    period = ReferenceField(Periods, required=True, reverse_delete_rule=CASCADE)
    user = ReferenceField(Users, required=True, reverse_delete_rule=CASCADE)
    amount = FloatField(required=True)
    has_paid = BooleanField(default=False)

    meta = {"collection": "period_moneys"}
