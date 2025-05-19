import pytest

from app.exceptions import EmptyStringError
from app.utils.tools.helpers import prevent_blank_strings


def test_prevent_blank_strings():
    with pytest.raises(EmptyStringError):
        prevent_blank_strings("  ")
