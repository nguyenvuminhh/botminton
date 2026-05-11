from mongoengine import CASCADE, Document, FloatField, QuerySet, ReferenceField

from schemas.additional_costs import AdditionalCosts
from schemas.users import Users


class AdditionalCostParticipants(Document):
    additional_cost = ReferenceField(AdditionalCosts, required=True, reverse_delete_rule=CASCADE)
    user = ReferenceField(Users, required=True, reverse_delete_rule=CASCADE)
    weight = FloatField(default=1.0)

    meta = {
        "collection": "additional_cost_participants",
        "indexes": [
            {"fields": ["additional_cost", "user"], "unique": True},
        ],
    }

    objects: QuerySet  # type: ignore[attr-defined]
