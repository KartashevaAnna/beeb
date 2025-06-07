from app.utils.tools.helpers import get_max_days_in_month


def test_get_max_days_in_month_except_february():
    non_leap_year = 2025
    expected_values = {
        1: 31,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }
    for key in expected_values.keys():
        assert expected_values[key] == get_max_days_in_month(
            month=key, year=non_leap_year
        )


def test_get_max_days_in_month_february_leap_year():
    leap_year = 2024
    assert 29 == get_max_days_in_month(month=2, year=leap_year)


def test_get_max_days_in_month_february_non_leap_year():
    non_leap_year = 2025
    assert 28 == get_max_days_in_month(month=2, year=non_leap_year)
