from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
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

    def _parse_table_row(self, row) -> Optional[Dict[str, Any]]:
        """Parse a single table row into a dictionary"""
        try:
            cells = row.find_all('td')

            if len(cells) < 18:
                logger.warning(f"Row has insufficient cells: {len(cells)}")
                return None

            return {
                "container_number": cells[0].text.strip(),
                "available": cells[1].text.strip(),
                "location": cells[2].text.strip(),
                "trucker": cells[3].text.strip(),
                "customs_status": cells[4].text.strip(),
                "freight_status": cells[5].text.strip(),
                "misc_holds": cells[6].text.strip(),
                "terminal_demurrage_amount": cells[7].text.strip(),
                "last_free_day": cells[8].text.strip(),
                "last_guar_day": cells[9].text.strip(),
                "pay_through_date": cells[10].text.strip(),
                "non_demurrage_amount": cells[11].text.strip(),
                "ssco": cells[12].text.strip(),
                "type": cells[13].text.strip(),
                "length": cells[14].text.strip(),
                "height": cells[15].text.strip(),
                "hazardous": cells[16].text.strip(),
                "genset_required": cells[17].text.strip(),
            }
        except Exception as e:
            logger.error(f"Error parsing table row: {str(e)}")
            return None

    def _find_container_data(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Find and parse the first container data row from the table"""
        try:
            # Find the table
            table = soup.find('table', class_='table')

            if not table:
                logger.warning("Container table not found")
                return None

            # Find tbody
            tbody = table.find('tbody')

            if not tbody:
                logger.warning("Table tbody not found")
                return None

            # Find the first data row
            rows = tbody.find_all('tr')

            if not rows:
                logger.warning("No data rows found in table")
                return None

            # Parse the first row
            return self._parse_table_row(rows[0])

        except Exception as e:
            logger.error(f"Error finding container data: {str(e)}")
            return None

    def _find_all_containers(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find and parse all container data rows from the table"""
        try:
            containers = []

            # Find the table
            table = soup.find('table', class_='table')

            if not table:
                logger.warning("Container table not found")
                return containers

            # Find tbody
            tbody = table.find('tbody')

            if not tbody:
                logger.warning("Table tbody not found")
                return containers

            # Find all data rows
            rows = tbody.find_all('tr')

            for row in rows:
                container_data = self._parse_table_row(row)
                if container_data:
                    containers.append(container_data)

            return containers

        except Exception as e:
            logger.error(f"Error finding containers: {str(e)}")
            return []

    def _extract_full_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract complete container information"""
        container_data = self._find_container_data(soup)

        if not container_data:
            raise DataExtractionError("No container data found in response")

        # Parse holds
        holds = []
        misc_holds = container_data.get("misc_holds", "").strip().upper()
        if misc_holds and misc_holds != "NONE" and misc_holds != "":
            holds = [h.strip() for h in misc_holds.split(',') if h.strip()]

        # Check if customs is released
        customs_released = container_data.get("customs_status", "").strip().upper() == "RELEASED"

        # Check if freight is released
        freight_released = container_data.get("freight_status", "").strip().upper() in ["EMPTY", "RELEASED"]

        return {
            "container_number": container_data.get("container_number", ""),
            "status": "Available" if container_data.get("available", "").upper() == "YES" else "Not Available",
            "available": container_data.get("available", "").upper() == "YES",
            "location": container_data.get("location", ""),
            "trucker": container_data.get("trucker", ""),
            "customs_status": container_data.get("customs_status", ""),
            "customs_released": customs_released,
            "freight_status": container_data.get("freight_status", ""),
            "freight_released": freight_released,
            "holds": holds,
            "has_holds": len(holds) > 0,
            "terminal_demurrage_amount": container_data.get("terminal_demurrage_amount", ""),
            "last_free_day": container_data.get("last_free_day", ""),
            "last_guar_day": container_data.get("last_guar_day", ""),
            "pay_through_date": container_data.get("pay_through_date", ""),
            "non_demurrage_amount": container_data.get("non_demurrage_amount", ""),
            "ssco": container_data.get("ssco", ""),
            "size": container_data.get("length", ""),
            "type": container_data.get("type", ""),
            "height": container_data.get("height", ""),
            "hazardous": container_data.get("hazardous", "").upper() == "YES",
            "genset_required": container_data.get("genset_required", "").upper() == "YES",
            "last_updated": datetime.utcnow().isoformat()
        }

    def _extract_availability(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract availability information"""
        container_data = self._find_container_data(soup)

        if not container_data:
            raise DataExtractionError("No container data found in response")

        available = container_data.get("available", "").upper() == "YES"

        # Check for any holds
        holds = []
        misc_holds = container_data.get("misc_holds", "").strip().upper()
        if misc_holds and misc_holds != "NONE" and misc_holds != "":
            holds = [h.strip() for h in misc_holds.split(',') if h.strip()]

        # Check customs and freight status
        customs_ok = container_data.get("customs_status", "").strip().upper() == "RELEASED"
        freight_ok = container_data.get("freight_status", "").strip().upper() in ["EMPTY", "RELEASED"]

        ready_for_pickup = available and customs_ok and freight_ok and len(holds) == 0

        return {
            "container_number": container_data.get("container_number", ""),
            "available": available,
            "status": "Available" if available else "Not Available",
            "available_for_pickup": ready_for_pickup,
            "availability": "Ready for pickup" if ready_for_pickup else "Not ready - check holds/status",
            "customs_released": customs_ok,
            "freight_released": freight_ok,
            "has_holds": len(holds) > 0
        }

    def _extract_location(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract location information"""
        container_data = self._find_container_data(soup)

        if not container_data:
            raise DataExtractionError("No container data found in response")

        location = container_data.get("location", "")

        # Try to parse location format like "YARD-A-123"
        location_parts = location.split('-')
        yard = location_parts[0] if len(location_parts) > 0 else ""
        row = location_parts[1] if len(location_parts) > 1 else ""
        position = location_parts[2] if len(location_parts) > 2 else ""

        return {
            "container_number": container_data.get("container_number", ""),
            "status": "Available" if container_data.get("available", "").upper() == "YES" else "Not Available",
            "location": location,
            "yard": yard,
            "row": row,
            "position": position,
            "trucker": container_data.get("trucker", "")
        }

    def _extract_holds(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract holds information"""
        container_data = self._find_container_data(soup)

        if not container_data:
            raise DataExtractionError("No container data found in response")

        # Parse holds from misc_holds field
        holds = []
        misc_holds = container_data.get("misc_holds", "").strip().upper()
        if misc_holds and misc_holds != "NONE" and misc_holds != "":
            holds = [h.strip() for h in misc_holds.split(',') if h.strip()]

        # Add customs hold if not released
        customs_status = container_data.get("customs_status", "").strip().upper()
        if customs_status != "RELEASED":
            holds.append(f"CUSTOMS: {customs_status}")

        # Add freight hold if not released
        freight_status = container_data.get("freight_status", "").strip().upper()
        if freight_status not in ["EMPTY", "RELEASED"]:
            holds.append(f"FREIGHT: {freight_status}")

        return {
            "container_number": container_data.get("container_number", ""),
            "status": "Available" if container_data.get("available", "").upper() == "YES" else "Not Available",
            "holds": holds,
            "has_holds": len(holds) > 0,
            "customs_status": container_data.get("customs_status", ""),
            "freight_status": container_data.get("freight_status", ""),
            "misc_holds": container_data.get("misc_holds", "")
        }

    def _extract_lfd(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract Last Free Day information"""
        container_data = self._find_container_data(soup)

        if not container_data:
            raise DataExtractionError("No container data found in response")

        last_free_day = container_data.get("last_free_day", "")

        # Calculate days remaining if LFD is in a valid date format
        days_remaining = None
        try:
            if last_free_day:
                lfd_date = datetime.strptime(last_free_day, "%m/%d/%Y")
                today = datetime.now()
                days_remaining = (lfd_date - today).days
        except Exception as e:
            logger.warning(f"Could not parse LFD date: {last_free_day}, error: {str(e)}")

        return {
            "container_number": container_data.get("container_number", ""),
            "status": "Available" if container_data.get("available", "").upper() == "YES" else "Not Available",
            "last_free_day": last_free_day,
            "last_guar_day": container_data.get("last_guar_day", ""),
            "pay_through_date": container_data.get("pay_through_date", ""),
            "days_remaining": days_remaining,
            "terminal_demurrage_amount": container_data.get("terminal_demurrage_amount", ""),
            "non_demurrage_amount": container_data.get("non_demurrage_amount", "")
        }

    def parse_all_containers(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse all containers from the table (useful if multiple containers are returned)"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            containers = self._find_all_containers(soup)

            result = []
            for container_data in containers:
                # Parse holds
                holds = []
                misc_holds = container_data.get("misc_holds", "").strip().upper()
                if misc_holds and misc_holds != "NONE" and misc_holds != "":
                    holds = [h.strip() for h in misc_holds.split(',') if h.strip()]

                result.append({
                    "container_number": container_data.get("container_number", ""),
                    "available": container_data.get("available", "").upper() == "YES",
                    "location": container_data.get("location", ""),
                    "customs_status": container_data.get("customs_status", ""),
                    "freight_status": container_data.get("freight_status", ""),
                    "holds": holds,
                    "last_free_day": container_data.get("last_free_day", ""),
                    "ssco": container_data.get("ssco", ""),
                    "size": container_data.get("length", ""),
                    "type": container_data.get("type", ""),
                })

            return result

        except Exception as e:
            logger.error(f"Error parsing all containers: {str(e)}", exc_info=True)
            raise DataExtractionError(f"Failed to parse containers: {str(e)}")