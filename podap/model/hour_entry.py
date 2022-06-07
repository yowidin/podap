class HourEntry:

    def __init__(self, start_hour: int, title: str, duration: int = 1):
        # TODO: Use datetime.time for starting time and datetime.timedelta for duration
        self.start_hour = start_hour
        self.duration = duration
        self.end_hour = self.start_hour + self.duration
        self.title = title

    @staticmethod
    def parse(text: str):
        error_msg = f'bad HourEntry: "{text}"'

        parts = text.split('\n')
        if len(parts) != 2:
            raise ValueError(error_msg)

        text = parts[0]
        time = parts[1].split(':')

        if len(time) != 2:
            raise ValueError(error_msg)

        try:
            time = int(time[0])
        except ValueError:
            raise ValueError(error_msg)

        return HourEntry(start_hour=time, title=text)

    def is_active(self, hour: int) -> bool:
        return self.start_hour <= hour < self.end_hour

    def __str__(self):
        return f'{self.title}\n{self.start_hour:02}:00'

    def __repr__(self):
        return f'<HourEntry(start_hour={self.start_hour!r},title={self.title!r})>'
