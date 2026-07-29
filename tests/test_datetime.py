from datetime import UTC, datetime

from ums.utils.datetime import format_iso, now_utc


def test_now_utc_returns_utc_datetime():
    result = now_utc()
    assert result.tzinfo is not None
    assert result.tzinfo.utcoffset(result) == UTC.utcoffset(result)


def test_format_iso_appends_z():
    dt = datetime(2026, 7, 29, 12, 0, 0, tzinfo=UTC)
    result = format_iso(dt)
    assert result.endswith("Z")
    assert result == "2026-07-29T12:00:00Z"
