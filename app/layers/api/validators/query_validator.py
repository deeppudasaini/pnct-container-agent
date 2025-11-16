from app.shared.exceptions.api_exceptions import InvalidRequestError
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


def validate_query(query: str) -> bool:
    if not query or not query.strip():
        raise InvalidRequestError("Query cannot be empty")

    if len(query) > 500:
        raise InvalidRequestError("Query too long (max 500 characters)")

    suspicious_patterns = ["<script>", "javascript:", "onclick="]
    for pattern in suspicious_patterns:
        if pattern.lower() in query.lower():
            raise InvalidRequestError("Query contains invalid characters")

    return True