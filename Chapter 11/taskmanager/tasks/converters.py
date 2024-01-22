from datetime import datetime


class DateConverter:
    regex = "[0-9]{4}-[0-9]{2}-[0-9]{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d")

    def to_url(self, object):
        return object.strftime("%Y-%m-%d")
