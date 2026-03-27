from mongoengine import (
    Document, IntField, ReferenceField, CASCADE, QuerySet
)

from schemas.sessions import Sessions
from schemas.users import Users

class SessionParticipants(Document):
    user = ReferenceField(Users, required=True, reverse_delete_rule=CASCADE)
    session = ReferenceField(Sessions, required=True, reverse_delete_rule=CASCADE)
    additional_participants = IntField(default=0)

    meta = {"collection": "session_participants"}

    objects: QuerySet  # type: ignore[attr-defined]