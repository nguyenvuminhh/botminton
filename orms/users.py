from mongoengine import Document, StringField, BooleanField, QuerySet

class Users(Document):
    telegram_id = StringField(required=True, unique=True)
    telegram_user_name = StringField()
    is_admin = BooleanField(default=False)

    meta = {"collection": "users"}

    objects: QuerySet  # type: ignore[attr-defined]
