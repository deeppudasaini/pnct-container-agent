import re
from typing import Optional
from datetime import datetime, timezone
from app.shared.config.constants.scraper_constants import CONTAINER_ID_PATTERN


def validate_container_id(container_id: str) -> bool:
    if not container_id:
        return False
    return bool(re.match(CONTAINER_ID_PATTERN, container_id.upper()))


def normalize_container_id(container_id: str) -> Optional[str]:
    if not container_id:
        return None

    normalized = container_id.replace(" ", "").upper()

    if validate_container_id(normalized):
        return normalized

    return None


def get_current_timestamp() -> datetime:
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime) -> str:
    return dt.isoformat()
