from datetime import datetime

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from podap.model import Model, DayOfWeek
from podap.view import ErrorMessage, CurrentTask, BIG_LABEL_STYLE, SMALL_LABEL_STYLE


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
        self.current_task.setStyleSheet(BIG_LABEL_STYLE)
        self.layout.addWidget(self.current_task)

        second_row = QHBoxLayout()
        second_row.addSpacing(45)

        self.next_task = QLabel('???')
        self.next_task.setStyleSheet(SMALL_LABEL_STYLE)
        second_row.addWidget(self.next_task)

        self.current_time = QLabel('???')
        self.current_time.setStyleSheet(SMALL_LABEL_STYLE)
        second_row.addWidget(self.current_time)

        second_row.addStretch()
        second_row.setContentsMargins(0, 0, 0, 0)

        self.layout.addLayout(second_row)

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
            day_number = DayOfWeek.from_date_time(date).value[0]

            self.current_task.setText(current_entry.title)
            self.next_task.setText(f'{day_number}Next: {next_entry.title}')

            self.current_time.setText(f'{date.hour:02}:{date.minute:02}:{date.second:02}')
        except ValueError as e:
            self.model_error.emit(str(e))
