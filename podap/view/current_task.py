from typing import List

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPalette, QColor

from datetime import datetime

from podap.view.scalable_label import ScalableLabel


class CurrentTask(ScalableLabel):
    """ Displays the current task and flashes with warning_colors at the given blink_minutes """

    def __init__(self, text: str, blink_minutes: List[int] = None, warning_colors: List[int] = None, *args, **kwargs):
        super().__init__(text, *args, **kwargs)

        if warning_colors is None:
            warning_colors = [QColor.fromRgb(255, 0, 0), QColor.fromRgb(255, 255, 0)]

        if blink_minutes is None:
            blink_minutes = [0, 45]

        self.warnings_colors = []
        for color in warning_colors:
            palette = QPalette()
            palette.setColor(QPalette.Window, color)
            self.warnings_colors.append(palette)

        self.blink_minutes = blink_minutes
        self.setAlignment(Qt.AlignCenter)

        self.setAutoFillBackground(True)
        self.default_palette = self.palette()

        self.setContentsMargins(0, 0, 0, 0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(500)

    def on_tick(self):
        # Check whether we have to change the background
        now = datetime.now()
        if now.minute in self.blink_minutes:
            palette = self.warnings_colors[now.second % len(self.warnings_colors)]
        else:
            palette = self.default_palette

        self.setPalette(palette)
