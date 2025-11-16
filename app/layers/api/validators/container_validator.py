from app.shared.exceptions.api_exceptions import InvalidRequestError
from app.shared.utils.helpers import normalize_container_id


def validate_container_number(container_number: str) -> str:
    if not container_number:
        raise InvalidRequestError("Container number is required")

    normalized = normalize_container_id(container_number)

    if not normalized:
        raise InvalidRequestError(
            "Invalid container number format. "
            "Expected format: 4 letters + 7 digits (e.g., MSDU1234567)"
        )

    return normalized
