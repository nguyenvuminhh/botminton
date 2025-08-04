from mongoengine import Document, StringField, IntField

class Metadata(Document):
    singleton_id = StringField(primary_key=True, default="singleton")

    default_location = StringField(default="Unisport")
    default_start_time = StringField(default="20:30")
    default_end_time = StringField(default="22:00")
    default_day_of_the_week_index = IntField(default=5)

    meta = {
        "collection": "metadata",
        "strict": False
    }

    @classmethod
    def get(cls) -> "Metadata":
        result = cls.objects(singleton_id="singleton").first()  # type: ignore
        if not result:
            raise ValueError("Metadata not found. Please create it first.")
        return result

    @classmethod
    def create(cls) -> "Metadata":
        if not cls.objects(singleton_id="singleton"): # type: ignore
            return cls().save()
        else:
            return cls.get()  # type: ignore