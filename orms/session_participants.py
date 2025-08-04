from mongoengine import (
    Document, IntField, BooleanField, ReferenceField, CASCADE, QuerySet
)

from orms.sessions import Sessions
from orms.users import Users

class SessionParticipants(Document):
    user = ReferenceField(Users, required=True, reverse_delete_rule=CASCADE)
    session = ReferenceField(Sessions, required=True, reverse_delete_rule=CASCADE)
    additional_participants = IntField(default=0)
    has_paid = BooleanField(default=False)

    meta = {"collection": "session_participants"}

    objects: QuerySet  # type: ignore[attr-defined]