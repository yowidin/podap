from typing import List, Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QWidget

from podap.model import DayEntry, Model
from podap.view.styles import DEFAULT_BOLD_STYLE, DEFAULT_STYLE

from datetime import datetime


class DayOverview(QWidget):
    UPDATE_INTERVAL_MS = 2000  # Update every 10 seconds

    def __init__(self, model: Model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = model
        self.current_day = None  # type: Optional[DayEntry]
        self.active_entry_idx = None  # type: Optional[int]
        self.bold_active_entry = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.active_color = QColor.fromRgb(0xCB4B16)
        self.active_palette = QPalette()
        self.active_palette.setColor(QPalette.Window, self.active_color)
        self.default_style = self.styleSheet()

        self.background_colors = [QColor.fromRgb(0xEEE8D5), QColor.fromRgb(0xFDF6E3)]
        self.background_palettes = []
        for x in self.background_colors:
            palette = QPalette()
            palette.setColor(QPalette.Window, x)
            self.background_palettes.append(palette)

        layout.setSpacing(0)

        self.left_half = QVBoxLayout()
        self.right_half = QVBoxLayout()

        self.hours = []  # type: List[QLabel]
        self.titles = []  # type: List[QLabel]

        layout.addLayout(self.left_half)
        layout.addLayout(self.right_half)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(DayOverview.UPDATE_INTERVAL_MS)

        self.model.subscribe_to_changes(self.on_model_change)

        self._update()

    def on_model_change(self, _):
        # TODO: This may be called from the watcher thread, but I'm to lazy to work this stuff around (signals etc)
        self.force_update()

    def force_update(self):
        """ Update the whole window (e.g.: in case of model change) """
        # TODO: Error handling is missing
        new_day = self.model.get_current_day()
        self._reset_for_day(new_day)
        self.current_day = new_day

        new_entry_idx = datetime.now().hour
        self._update_active_entry(new_entry_idx)
        self.active_entry_idx = new_entry_idx

    def _update(self):
        """ Update the current day and hour entry based on the current time """
        # TODO: Error handling is missing
        new_day = self.model.get_current_day()
        if self.current_day is None or self.current_day != new_day:
            self._reset_for_day(new_day)
            self.current_day = new_day

        new_entry_idx = datetime.now().hour
        if self.active_entry_idx is None or self.active_entry_idx != new_entry_idx:
            self._update_active_entry(new_entry_idx)
            self.active_entry_idx = new_entry_idx

    def _reset_for_day(self, day: DayEntry):
        """ Update all labels to show the current day """
        self._ensure_num_labels(len(day.entries))
        for i in range(len(day.entries)):
            entry = day.entries[i]
            self.hours[i].setText(f'{entry.start_hour:02}:00')
            self.titles[i].setText(f'{entry.title}')

    @staticmethod
    def _deactivate_label(label: QLabel, palette: QPalette):
        """ Mark a label as non-active (default color, not bold) """
        label.setStyleSheet(DEFAULT_STYLE)
        label.setPalette(palette)
        label.show()

    def _activate_label(self, label: QLabel):
        """ Mark a label as active (active color, bold) """
        if self.bold_active_entry:
            label.setStyleSheet(DEFAULT_BOLD_STYLE)

        label.setPalette(self.active_palette)
        label.show()

    def _update_active_entry(self, new_idx: int):
        """ Update the currently active entry """
        if self.active_entry_idx is not None:
            palette = self.background_palettes[self.active_entry_idx % len(self.background_palettes)]

            self._deactivate_label(self.hours[self.active_entry_idx], palette)
            self._deactivate_label(self.titles[self.active_entry_idx], palette)

        self._activate_label(self.hours[new_idx])
        self._activate_label(self.titles[new_idx])

    def _ensure_num_labels(self, count: int):
        """
        Make sure that this widget has at least count visible labels either by adding missing labels or by adjusting
        their visibility.

        :param count: Desired number of labels.
        :return: None
        """

        # First add missing labels
        extra_labels = len(self.hours) - count
        if extra_labels < 0:
            self._add_extra_labels(-extra_labels)

        # Adjust visibility
        for i in range(len(self.hours)):
            is_visible = True if i < count else False
            self.hours[i].setVisible(is_visible)
            self.titles[i].setVisible(is_visible)

    def _add_extra_labels(self, count: int):
        for i in range(count):
            palette = self.background_palettes[len(self.hours) % len(self.background_palettes)]

            def setup_label(label):
                label.setPalette(palette)
                label.setAutoFillBackground(True)
                label.setContentsMargins(16, 4, 16, 4)

            hour = QLabel(f'hour {len(self.hours)}')
            hour.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            setup_label(hour)

            title = QLabel(f'title {len(self.hours)}')
            title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            setup_label(title)

            self.left_half.addWidget(hour)
            self.right_half.addWidget(title)

            self.hours.append(hour)
            self.titles.append(title)
