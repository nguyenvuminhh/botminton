from mongoengine import CASCADE, Document, FloatField, QuerySet, ReferenceField, StringField

from schemas.periods import Periods


class AdditionalCosts(Document):
    period = ReferenceField(Periods, required=True, reverse_delete_rule=CASCADE)
    name = StringField(required=True)
    total_amount = FloatField(required=True)

    meta = {
        "collection": "additional_costs",
        "indexes": ["period"],
    }

    objects: QuerySet  # type: ignore[attr-defined]
