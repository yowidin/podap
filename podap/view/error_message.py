from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor

from podap.view.scalable_label import ScalableLabel


class ErrorMessage(ScalableLabel):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.palette = QPalette()
        self.palette.setColor(QPalette.Window, QColor.fromRgb(255, 0, 0))
        self.setPalette(self.palette)
        self.setAlignment(Qt.AlignCenter)
        self.setAutoFillBackground(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setVisible(False)

        self.clicked.connect(self.hide_error)

    def mousePressEvent(self, ev):
        self.clicked.emit()

    def show_error(self, text: str):
        self.setText(text)
        self.setVisible(True)

    def hide_error(self):
        self.setVisible(False)
