import re
from app.shared.utils.helpers import validate_container_id, normalize_container_id


class EntityExtractor:

    def extract_container_id(self, parsed_query: dict) -> str:
        container_id = parsed_query.get("container_id", "")

        if not container_id:
            return None

        normalized = normalize_container_id(container_id)

        return normalized
