from mongoengine import (
    Document, StringField, IntField, BooleanField,
    FloatField, DateField, ReferenceField, CASCADE
)
from datetime import datetime

class SessionParticipants(Document):
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    session = ReferenceField(Session, required=True, reverse_delete_rule=CASCADE)
    additional_participants = IntField(default=0)
    has_paid = BooleanField(default=False)

    meta = {"collection": "session_participants"}
