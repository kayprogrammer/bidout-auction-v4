from django.db.models import DateTimeField


class DateTimeWithoutTZField(DateTimeField):
    def db_type(self, connection):
        return "timestamp"
