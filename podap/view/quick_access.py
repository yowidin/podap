from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget, QVBoxLayout

from podap.view import DayOverview


class QuickAccess(QWidget):
    collape_tasks = Signal(bool)
    should_close = Signal()

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addStretch()

        self.button_layout.setSpacing(7)
        self.model = model

        self.info = DayOverview(model)

        def make_button(text: str):
            btn = QPushButton(text)
            btn.setStyleSheet('font-size: 10pt')
            btn.setContentsMargins(0, 0, 0, 0)
            return btn

        exit_btn = make_button('x')
        exit_btn.clicked.connect(self.on_exit_click)
        self.button_layout.addWidget(exit_btn)

        info_btn = make_button('i')
        info_btn.clicked.connect(self.on_info_click)
        self.button_layout.addWidget(info_btn)

        self.hidden = False

        self.hide_button = make_button('<')
        self.hide_button.clicked.connect(self.on_hide_click)
        self.button_layout.addWidget(self.hide_button)

    def on_info_click(self):
        if not self.info.isVisible():
            self.info.show()
        else:
            self.info.close()

    def setup_hide_button(self, is_hidden: bool):
        self.hidden = is_hidden
        self.hide_button.setText('>' if self.hidden else '<')

    def on_hide_click(self):
        self.setup_hide_button(not self.hidden)
        self.collape_tasks.emit(self.hidden)

    def on_exit_click(self):
        self.info.close()
        self.should_close.emit()
