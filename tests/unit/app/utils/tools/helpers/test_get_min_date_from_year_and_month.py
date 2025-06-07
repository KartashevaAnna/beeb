import datetime
from app.utils.tools.helpers import (
    get_min_date_from_year_and_month_datetime_format,
)


def test_get_max_date_from_year_and_month():
    year = 2025
    month = 6
    date = "2025-06-01 00:00:00.000001"
    expected_result = datetime.datetime.strptime(
        date, "%Y-%m-%d %H:%M:%S.%f"
    ).astimezone()
    obtained_result = get_min_date_from_year_and_month_datetime_format(
        year=year, month=month
    )
    assert expected_result == obtained_result
