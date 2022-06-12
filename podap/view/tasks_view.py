from datetime import datetime

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout

from podap.model import Model, DayOfWeek
from podap.view import ErrorMessage, CurrentTask
from podap.view.scalable_label import ScalableLabel


class TasksView(QWidget):
    model_changed = Signal()
    model_error = Signal(str)

    def __init__(self, model: Model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = model

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.error_message = ErrorMessage('Oh no, an error!')
        self.layout.addWidget(self.error_message)

        self.current_task = CurrentTask('???')
        self.current_task.set_bold(True)
        self.layout.addWidget(self.current_task)

        self.next_task = ScalableLabel('???')
        self.layout.addWidget(self.next_task)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_tasks)
        self.timer.start(500)

        self.model.subscribe_to_changes(self.on_model_change)
        self.model.subscribe_to_errors(self.on_model_error)

        self.model_error.connect(self.show_model_error)
        self.model_changed.connect(self.update_changed_model)

        # Immediately update UI this way we won't see ??? before the first timer tick
        self.update_tasks()

    def show_model_error(self, message: str):
        self.error_message.show_error(message)

    def update_changed_model(self):
        self.update_tasks()

    def on_model_error(self, _, message):
        # May be called from watcher thread
        self.model_error.emit(message)

    def on_model_change(self, _):
        # May be called from watcher thread
        self.model_changed.emit()

    def update_tasks(self):
        try:
            current_entry = self.model.get_current_task()
            next_entry = self.model.get_pending_task()

            date = datetime.now()
            # day_number = DayOfWeek.from_date_time(date).value[0]

            self.current_task.setText(current_entry.title)

            task = f'Next: {next_entry.title}'
            time = f'{date.hour:02}:{date.minute:02}:{date.second:02}'
            self.next_task.setText(f'{task} {time}')
        except ValueError as e:
            self.model_error.emit(str(e))
