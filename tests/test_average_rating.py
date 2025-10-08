import pytest
from reports import average_rating

def test_generate_average_rating():
    data = [
        {"brand": "apple", "rating": "5"},
        {"brand": "apple", "rating": "3"},
        {"brand": "samsung", "rating": "4"},
    ]
    result = average_rating.generate(data)
    assert result[0][0] == "apple"
    assert pytest.approx(result[0][1], 0.01) == 4.0
    assert result[1][0] == "samsung"
    assert result[1][1] == 4.0

def test_generate_skips_invalid_rows():
    data = [
        {"brand": "apple", "rating": "4"},
        {"brand": "apple", "rating": "oops"},
        {"brand": None, "rating": "3"},
    ]
    result = average_rating.generate(data)
    assert result == [("apple", 4.0)]