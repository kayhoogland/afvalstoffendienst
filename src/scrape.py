from datetime import datetime, timedelta
from functools import cached_property
from typing import Dict, List

import requests


BASE_URL = "https://afvalstoffendienst.nl"
LOOKUP_URL = f"{BASE_URL}/adressen/{{postal_code}}:{{number}}"
AFVALSTROMEN_URL = f"{BASE_URL}/rest/adressen/{{bagid}}/afvalstromen"
CALENDAR_URL = f"{BASE_URL}/rest/adressen/{{bagid}}/kalender/{{year}}"

# Waste type ID to category name mapping
# Based on analysis of waste types at address 5233AL:124
WASTE_TYPE_MAPPING = {
    4: "gft",        # groente,-fruit-en-tuinafval-en-etensresten (28/year)
    1: "pd",         # plastic,-blik-en-drinkpakken (19/year)
    2: "restafval",  # restafval (18/year)
    7: "papier",     # papier-en-karton (13/year)
    # Rare types like kerstbomen (ID 17, 1/year) are excluded
}


def current_year():
    return datetime.now().year


class Scrape:
    def __init__(self, postal_code: str, number: int):
        self.postal_code = postal_code
        self.number = number

    @cached_property
    def address_id(self) -> str:
        """Get the bagid (address ID) from postal code and house number."""
        url = LOOKUP_URL.format(postal_code=self.postal_code, number=self.number)
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        if not data or len(data) == 0:
            raise ValueError(f"No address found for {self.postal_code}:{self.number}")

        return data[0]["bagid"]

    @cached_property
    def waste_types(self) -> Dict[int, str]:
        """Get configured waste types.

        Returns only the waste types defined in WASTE_TYPE_MAPPING.
        """
        return WASTE_TYPE_MAPPING

    @cached_property
    def calendar_data(self) -> List[Dict]:
        """Get calendar data for current and next year."""
        current = current_year()
        years = [current, current + 1]

        all_data = []
        for year in years:
            url = CALENDAR_URL.format(bagid=self.address_id, year=year)
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data)

        return all_data

    @cached_property
    def reminder_dates_for_all_kinds(self) -> Dict[str, List[str]]:
        """Get reminder dates for all waste types."""
        return {
            waste_type_name: self.reminder_dates_for_kind(waste_type_id)
            for waste_type_id, waste_type_name in self.waste_types.items()
        }

    def reminder_dates_for_kind(self, waste_type_id: int) -> List[str]:
        """Get reminder dates for a specific waste type ID."""
        # Filter calendar data for this waste type
        reminder_dates = []
        for entry in self.calendar_data:
            if entry["afvalstroom_id"] == waste_type_id:
                # Parse the pickup date and subtract one day
                pickup_date = datetime.fromisoformat(entry["ophaaldatum"])
                reminder_date = pickup_date - timedelta(days=1)
                reminder_dates.append(reminder_date.strftime("%Y-%m-%d"))

        return sorted(reminder_dates)
