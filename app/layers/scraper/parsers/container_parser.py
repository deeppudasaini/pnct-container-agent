from bs4 import BeautifulSoup
from typing import Dict, Any
from datetime import datetime

from app.shared.utils.logger import get_logger
from app.shared.exceptions.scraper_exceptions import DataExtractionError

logger = get_logger(__name__)


class ContainerParser:

    def parse(self, html_content: str, operation: str) -> Dict[str, Any]:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            if operation == "get_full_info":
                return self._extract_full_info(soup)
            elif operation == "check_availability":
                return self._extract_availability(soup)
            elif operation == "get_location":
                return self._extract_location(soup)
            elif operation == "check_holds":
                return self._extract_holds(soup)
            elif operation == "get_lfd":
                return self._extract_lfd(soup)
            else:
                return self._extract_full_info(soup)

        except Exception as e:
            logger.error(f"Data parsing failed: {str(e)}", exc_info=True)
            raise DataExtractionError(f"Failed to parse container data: {str(e)}")

    def _extract_full_info(self, soup: BeautifulSoup) -> Dict[str, Any]:

        return {
            "container_number": soup.find('span', class_='container-number').text.strip(),
            "status": soup.find('span', class_='status').text.strip(),
            "location": soup.find('span', class_='location').text.strip(),
            "availability": soup.find('span', class_='availability').text.strip(),
            "holds": [],
            "last_free_day": soup.find('span', class_='lfd').text.strip(),
            "size": "40HC",
            "type": "General Purpose",
            "last_updated": datetime.utcnow().isoformat()
        }

    def _extract_availability(self, soup: BeautifulSoup) -> Dict[str, Any]:
        return {
            "container_number": soup.find('span', class_='container-number').text.strip(),
            "status": soup.find('span', class_='status').text.strip(),
            "available_for_pickup": True,
            "availability": "Ready for pickup"
        }

    def _extract_location(self, soup: BeautifulSoup) -> Dict[str, Any]:
        return {
            "container_number": soup.find('span', class_='container-number').text.strip(),
            "status": soup.find('span', class_='status').text.strip(),
            "location": soup.find('span', class_='location').text.strip(),
            "yard": "Yard A",
            "row": "12",
            "position": "5"
        }

    def _extract_holds(self, soup: BeautifulSoup) -> Dict[str, Any]:
        return {
            "container_number": soup.find('span', class_='container-number').text.strip(),
            "status": soup.find('span', class_='status').text.strip(),
            "holds": [],
            "has_holds": False
        }

    def _extract_lfd(self, soup: BeautifulSoup) -> Dict[str, Any]:
        return {
            "container_number": soup.find('span', class_='container-number').text.strip(),
            "status": soup.find('span', class_='status').text.strip(),
            "last_free_day": soup.find('span', class_='lfd').text.strip(),
            "days_remaining": 5
        }
