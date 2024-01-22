from datetime import datetime

import pytest
from tasks.converters import DateConverter


@pytest.fixture
def date_converter():
    return DateConverter()


def test_to_python(date_converter):
    # Test conversion from string to datetime
    assert date_converter.to_python("2023-10-05") == datetime(2023, 10, 5)


def test_to_python_invalid_format(date_converter):
    # Test with an invalid date format
    with pytest.raises(ValueError):
        date_converter.to_python("2023/10/05")


def test_to_url(date_converter):
    # Test conversion from datetime to string
    date_obj = datetime(2023, 10, 5)
    assert date_converter.to_url(date_obj) == "2023-10-05"


def test_to_url_invalid_object(date_converter):
    # Test with an invalid type (not a datetime object)
    with pytest.raises(AttributeError):
        date_converter.to_url("2023-10-05")
