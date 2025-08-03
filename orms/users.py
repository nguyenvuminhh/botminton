from mongoengine import (
    Document, StringField, BooleanField
)

class Users(Document):
    telegram_id = StringField(required=True, unique=True)
    telegram_user_name = StringField()
    is_admin = BooleanField(default=False)

    meta = {"collection": "users"}
