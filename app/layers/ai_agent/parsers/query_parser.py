from typing import Dict, Any
import re


class QueryParser:

    def normalize(self, query: str) -> str:
        query = " ".join(query.split())

        query = re.sub(r'[^\w\s-]', '', query)

        return query.strip()

    def extract_keywords(self, query: str) -> list[str]:
        keywords = ["container", "info", "status", "location", "holds", "available", "pickup"]

        found_keywords = []
        query_lower = query.lower()

        for keyword in keywords:
            if keyword in query_lower:
                found_keywords.append(keyword)

        return found_keywords
