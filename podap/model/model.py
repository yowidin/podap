import glob
import os

from typing import Dict, Callable, List
from datetime import datetime, timedelta

from podap.model import DayEntry, DayOfWeek, HourEntry
from podap.config import Config


class Model:

    class File:
        def __init__(self, absolute_path: str):
            self.absolute_path = absolute_path
            self.file_name = os.path.basename(self.absolute_path)

            error_message = f'bad file name {self.file_name}'

            # Try to detect which day of week it is
            name_parts = self.file_name.split('_')
            if len(name_parts) != 2:
                raise ValueError(error_message)

            try:
                self.day_number = int(name_parts[0])
            except ValueError:
                raise ValueError(error_message)

            # Load the file contents
            with open(self.absolute_path, 'r') as f:
                self.text = f.read().strip()

    def __init__(self):
        self.working_directory = Config.INSTANCE.working_directory
        self.days = {}  # type: Dict[DayOfWeek, DayEntry]
        self.file_search_pattern = os.path.join(self.working_directory, '*.txt')
        self.on_change_listeners = []  # type: List[Callable[[Model], None]]
        self.on_error_listeners = []  # type: List[Callable[[Model, str], None]]
        self.reload()

    def subscribe_to_changes(self, listener: Callable[['Model'], None]):
        self.on_change_listeners.append(listener)

    def unsubscribe_from_changes(self, listener: Callable[['Model'], None]):
        try:
            self.on_change_listeners.remove(listener)
        except ValueError as e:
            print(f'Error unsubscribing from model changes: {e}')

    def subscribe_to_errors(self, listener: Callable[['Model', str], None]):
        self.on_error_listeners.append(listener)

    def unsubscribe_from_errors(self, listener: Callable[['Model', str], None]):
        try:
            self.on_error_listeners.remove(listener)
        except ValueError as e:
            print(f'Error unsubscribing from model errors: {e}')

    def changed_from_outside(self):
        try:
            self.reload()
        except ValueError as e:
            for listener in self.on_error_listeners:
                listener(self, str(e))

    def reload(self):
        files = glob.glob(self.file_search_pattern)
        files = [Model.File(x) for x in files]

        if len(files) == 0:
            raise ValueError(f'Could not load the working directory: {self.working_directory}')

        # Adjust the day numbers to match the internal day numbering format
        min_day_number = None
        for file in files:
            if min_day_number is None or file.day_number < min_day_number:
                min_day_number = file.day_number

        if min_day_number == 1:
            for file in files:
                file.day_number -= 1
        elif min_day_number != 0:
            raise ValueError('day numbers should start with either 0 or 1')

        files.sort(key=lambda x: x.day_number)

        new_days = [DayEntry.parse(DayOfWeek.from_number(x.day_number), x.text, x.absolute_path) for x in files]
        new_days = {x.day_of_week: x for x in new_days}

        # We start with an emtpy map of days, so we have to handle it as well
        changed = len(self.days) == 0
        for key in new_days:
            if changed:
                break

            new_entry = new_days[key]
            old_entry = self.days[key]
            if str(new_entry) != str(old_entry):
                changed = True

        if not changed:
            return

        self.days = new_days

        # Issue an event
        for listener in self.on_change_listeners:
            listener(self)

    @staticmethod
    def _make_pause(hour: int):
        return HourEntry(start_hour=hour, title=Config.INSTANCE.pause_text)

    def get_for_day_and_time(self, day: DayOfWeek, hour: int, minute: int) -> HourEntry:
        if minute >= (60 - Config.INSTANCE.pause_duration):
            return Model._make_pause(hour)

        entry_day = self.days[day]
        task = None
        for entry in entry_day.entries:
            if entry.is_active(hour):
                task = entry
                break

        if task is None:
            raise ValueError(f'No entry found for {day.name} at {hour:02}:{minute:02}')

        return task

    def get_current_day(self):
        return self.days[DayOfWeek.today()]

    def get_for_date(self, date: datetime) -> HourEntry:
        return self.get_for_day_and_time(DayOfWeek.from_date_time(date), date.hour, date.minute)

    def get_current_task(self) -> HourEntry:
        now = datetime.now()
        day = DayOfWeek.today()
        return self.get_for_day_and_time(day, now.hour, now.minute)

    def get_pending_task(self) -> HourEntry:
        now = datetime.now()
        now += timedelta(hours=1)
        day = DayOfWeek.from_date_time(now)

        # Use fixed minute to make sure we don't land on a pause
        return self.get_for_day_and_time(day, now.hour, 5)
