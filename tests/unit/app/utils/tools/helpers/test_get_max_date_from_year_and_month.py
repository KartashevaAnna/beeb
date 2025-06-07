from app.utils.tools.helpers import get_max_date_from_year_and_month


def test_get_max_date_from_year_and_month():
    year = 2025
    month = 6
    expected_result = "2025-06-30 23:59:59.999999"
    obtained_result = get_max_date_from_year_and_month(year=year, month=month)
    assert expected_result == obtained_result
