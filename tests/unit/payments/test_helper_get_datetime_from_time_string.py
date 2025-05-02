import datetime

from app.utils.tools.helpers import get_datetime_from_time_string


def test_get_datetime_from_time_string():
    now = datetime.datetime.now()
    year = str(now)[:4]
    month = str(now)[5:7]
    day = str(now)[8:10]
    date = f"{day}.{month}.{year}"
    res = get_datetime_from_time_string(date)
    res = str(res)[:-14]
    to_compare = str(now.astimezone())[:-14]
    assert res == to_compare
