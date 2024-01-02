from datetime import datetime
from functools import cached_property

import pandas as pd
from gazpacho import Soup, get

import re

URL = "https://afvalstoffendienstkalender.nl/nl/{postal_code}/{number}"
MONTHS = [
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
]
DATE_REGEX = "(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag) \\d{1,2} (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)"


MONTH_MAP = {m: str(i).rjust(2, "0") for m, i in zip(MONTHS, range(1, len(MONTHS) + 1))}
ALLOWED_KINDS = ["papier", "gft", "restafval", "pd"]


def current_year():
    return datetime.now().year


class Scrape:
    def __init__(self, postal_code: str, number: int):
        self.postal_code = postal_code
        self.number = number

    @cached_property
    def soup(self):
        html = get(URL.format(postal_code=self.postal_code, number=self.number))
        return Soup(html)

    @cached_property
    def reminder_dates_for_all_kinds(self):
        return {k: self.reminder_dates_for_kind(k) for k in ALLOWED_KINDS}

    def dates_for_kind(self, kind: str):
        return set(
            p.text
            for p in self.soup.find("p", {"class": kind}, partial=False)
            if p.text not in [kind, "vandaag"]
        )

    def reminder_dates_for_kind(self, kind: str):
        dates = [re.search(DATE_REGEX, d) for d in self.dates_for_kind(kind)]
        print(dates)
        return sorted([self.build_reminder_date(d.string) for d in dates if d])

    @staticmethod
    def build_reminder_date(date: str):
        weekday, day, month = date.split(" ")
        month_number = MONTH_MAP[month]
        date = pd.to_datetime((f"{current_year()}-{month_number}-{day.rjust(2, '0')}"))
        day_before = (date - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        return day_before
