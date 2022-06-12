import sys

from PySide6.QtGui import QMouseEvent, QCloseEvent

from podap.model import Model, Watcher
from podap.view import QuickAccess
from podap.config import Config
from podap.view.tasks_view import TasksView

from PySide6.QtCore import QTimer, Qt, QPoint, QSettings
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget, QSizePolicy


class MainWindow(QMainWindow):
    UI_VERSION = 1

    def __init__(self, model: Model, **kwargs):
        super().__init__(**kwargs)

        self.model = model
        self.setContentsMargins(0, 0, 0, 0)

        self.quick_access = QuickAccess(self.model)
        self.quick_access.collape_tasks.connect(self.update_tasks_visibility)
        self.quick_access.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.quick_access.should_close.connect(self.handle_close)

        self.task_view = TasksView(model)
        self.task_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.task_view.error_message.clicked.connect(self.error_message_clicked)

        self.borderless = Config.INSTANCE.borderless
        self.dragging = False
        self.old_size = self.size()
        self.collapsed = False

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.quick_access)
        main_layout.addWidget(self.task_view)
        main_layout.setContentsMargins(2, 0, 2, 0)

        # Workaround main window already having a layout
        window = QWidget()
        window.setLayout(main_layout)
        self.setCentralWidget(window)

        self._restore_position()
        self._make_always_on_top()

        self.click_position = self.pos()

    def error_message_clicked(self):
        # We cannot shrink the window immediately because this function is called just after user clicked on the
        # error message, and at that point error message is still not hidden. So we have to let Qt handle all the
        # outstanding events before we try to resize
        # https://forum.qt.io/topic/4500/resize-top-level-window-to-fit-contents/4
        QTimer.singleShot(0, self.shrink_vertically)

    def shrink_vertically(self):
        self.resize(self.width(), self.minimumSizeHint().height())

    def shrink_horizontally(self):
        self.resize(self.minimumSizeHint().width(), self.height())

    def shrink_to_old_size(self):
        self.resize(self.old_size)

    def _make_always_on_top(self):
        flags = self.windowFlags()
        flags |= Qt.WindowStaysOnTopHint
        if self.borderless:
            flags |= Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.show()

    def mousePressEvent(self, ev: QMouseEvent):
        self.click_position = ev.globalPos()
        self.dragging = True

    def mouseReleaseEvent(self, _: QMouseEvent) -> None:
        self.dragging = False

    def mouseDoubleClickEvent(self, ev: QMouseEvent) -> None:
        flags = self.windowFlags()

        self.borderless = not self.borderless
        if self.borderless:
            flags = flags | Qt.FramelessWindowHint
        else:
            flags = flags & ~Qt.FramelessWindowHint

        self.dragging = False
        self.setWindowFlags(flags)
        self.show()

    def mouseMoveEvent(self, ev: QMouseEvent):
        if not self.dragging:
            return

        delta = QPoint(ev.globalPos() - self.click_position)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.click_position = ev.globalPos()

    def update_tasks_visibility(self, should_hide: bool):
        self.collapsed = should_hide
        if should_hide:
            self.old_size = self.size()
            shrink = self.shrink_horizontally
        else:
            shrink = self.shrink_to_old_size

        self.task_view.setVisible(not should_hide)

        # Note: see error_message_clicked for description
        QTimer.singleShot(0, shrink)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._save_position()

    def handle_close(self):
        self.close()

    @staticmethod
    def make_settings() -> QSettings:
        return QSettings('Dennis Sitelew', 'podap')

    def _save_position(self):
        settings = self.make_settings()
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('state', self.saveState(self.UI_VERSION))
        settings.setValue('collapsed', self.collapsed)
        settings.setValue('old_size', self.old_size)

    def _restore_position(self):
        settings = self.make_settings()
        self.restoreGeometry(settings.value('geometry'))
        self.restoreState(settings.value('state'), self.UI_VERSION)

        self.collapsed = settings.value('collapsed', False)
        self.quick_access.setup_hide_button(self.collapsed)
        if self.collapsed:
            self.update_tasks_visibility(True)

        self.old_size = settings.value('old_size', None)

    # def do_save_image(self):
    #     # NOTE: Reference for saving UI as an image
    #     self.grab().save('screen.png')


class PodapApp:

    @staticmethod
    def run():
        app = QApplication(sys.argv)

        model = Model()

        with Watcher(model=model):
            widget = MainWindow(model=model)
            widget.show()
            res = app.exec()

        sys.exit(res)
