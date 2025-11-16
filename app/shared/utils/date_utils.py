from datetime import datetime, timedelta
from typing import Optional


def parse_date(date_str: str) -> Optional[datetime]:
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def calculate_days_until(target_date: datetime) -> int:
    if not target_date:
        return 0

    now = datetime.now()
    delta = target_date - now
    return delta.days


def format_date(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
    if not dt:
        return ""
    return dt.strftime(format_str)
