import pytest
from app import validate_title, validate_category, validate_priority, parse_deadline
from datetime import date, timedelta

def test_validate_title_ok():
    assert validate_title("Hello World") is None

def test_validate_title_short():
    v = validate_title("ab")
    assert v[0] == "title"

def test_validate_category_chars():
    assert validate_category("abc-123") is None
    v = validate_category("bad#char")
    assert v[1] == "INVALID_FORMAT"

def test_priority_range():
    assert validate_priority(3) is None
    v = validate_priority(10)
    assert v[1] == "OUT_OF_RANGE"

def test_deadline_future_and_past():
    d_future = (date.today() + timedelta(days=2)).isoformat()
    dl, err = parse_deadline(d_future)
    assert err is None
    d_past = (date.today() - timedelta(days=1)).isoformat()
    dl, err = parse_deadline(d_past)
    assert err is not None
