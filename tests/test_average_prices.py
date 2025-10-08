import pytest
from reports import average_price

def test_generate_average_price():
    data = [
        {"brand": "apple", "price": "1000"},
        {"brand": "apple", "price": "500"},
        {"brand": "samsung", "price": "300"},
    ]
    result = average_price.generate(data)

    assert result[0][0] == "apple"
    assert pytest.approx(result[0][1], 0.01) == 750.0

    assert result[1][0] == "samsung"
    assert pytest.approx(result[1][1], 0.01) == 300.0


def test_generate_skips_invalid_rows():
    data = [
        {"brand": "apple", "price": "1000"},
        {"brand": "apple", "price": "oops"},
        {"brand": None, "price": "300"},
    ]
    result = average_price.generate(data)

    assert result == [("apple", 1000.0)]