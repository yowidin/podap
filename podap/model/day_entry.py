from enum import Enum
from typing import List
from io import StringIO

from datetime import datetime

from podap.model import HourEntry


class DayOfWeek(Enum):
    Monday = (0, 'Mo')
    Tuesday = (1, 'Tu')
    Wednesday = (2, 'We')
    Thursday = (3, 'Th')
    Friday = (4, 'Fr')
    Saturday = (5, 'Sa')
    Sunday = (6, 'Su')

    def __str__(self):
        return f'{self.value[1]}'

    def __repr__(self):
        return f'<DayOfWeek({self.value[0]!r})>'

    @staticmethod
    def from_number(number: int):
        for kv in DayOfWeek:
            if kv.value[0] == number:
                return kv

        raise ValueError(f'unexpected day of week number: {number}')

    @staticmethod
    def today():
        return DayOfWeek.from_date_time(datetime.now())

    @staticmethod
    def from_date_time(date: datetime):
        return DayOfWeek.from_number(date.weekday())


class DayEntry:
    ENTRY_SEPARATOR = '\n\n'

    def __init__(self, day_of_week: DayOfWeek, entries: List[HourEntry], path: str):
        self.day_of_week = day_of_week
        self.entries = entries
        self.path = path

    @staticmethod
    def parse(day_of_week: DayOfWeek, text: str, path: str):
        text_entries = text.split(DayEntry.ENTRY_SEPARATOR)

        hour_entries = []
        for entry in text_entries:
            try:
                hour_entries.append(HourEntry.parse(entry))
            except ValueError as ex:
                raise ValueError(f'bad DayEntry for {day_of_week.name}: {ex}') from ex

        return DayEntry(day_of_week=day_of_week, entries=hour_entries, path=path)

    def __str__(self):
        f = StringIO()
        is_first = True
        for entry in self.entries:
            if not is_first:
                print(DayEntry.ENTRY_SEPARATOR, end='', file=f)

            print(str(entry), end='', file=f)
            is_first = False

        return f.getvalue()

    def __repr__(self):
        return f'<DayEntry(day_of_week={self.day_of_week!r},entries={self.entries!r})>'
