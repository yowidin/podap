
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from podap.model import Model, DayEntry


class Watcher:

    class EventHandler(FileSystemEventHandler):
        def __init__(self, model):
            self.model = model

        def on_modified(self, event):
            if not isinstance(event, FileModifiedEvent):
                # Assume that each directory change is a model change
                self.model.changed_from_outside()
                return

            is_part_of_model = False
            path = event.src_path
            for day_of_week in self.model.days:
                day = self.model.days[day_of_week]  # type: DayEntry
                if path == day.path:
                    is_part_of_model = True
                    break

            if is_part_of_model:
                self.model.changed_from_outside()

    def __init__(self, model: Model):
        self.model = model
        self.handler = Watcher.EventHandler(self.model)
        self.observer = Observer()
        self.observer.schedule(self.handler, path=self.model.working_directory)

    def __enter__(self):
        self.observer.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.observer.stop()
        self.observer.join()
