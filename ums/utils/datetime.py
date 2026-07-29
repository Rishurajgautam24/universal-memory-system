from datetime import UTC, datetime


def now_utc() -> datetime:
    return datetime.now(UTC)


def format_iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")
