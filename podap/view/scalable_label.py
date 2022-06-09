from PySide6.QtGui import QResizeEvent, Qt, QPaintEvent, QFontMetricsF
from PySide6.QtWidgets import QLabel


class ScalableLabel(QLabel):
    """ Label that changes its font size to accupy as much space as possible without overflowing """

    FONT_PRECISION = 0.5
    SCALING_FACTOR = 0.96  # Don't occupy all the available space so that window can still be resized

    def __init__(self, text, *args, **kwargs):
        super().__init__(text=text, *args, **kwargs)

        self.setIndent(0)
        self.setWordWrap(True)
        self.should_redraw = False
        self.bold = False
        self.italic = False
        self.starting_size = 10

    def set_starting_font_size(self, size: int):
        self.starting_size = size
        self.should_redraw = True

    def set_bold(self, bold: bool):
        self.bold = bold
        self.should_redraw = True

    def set_italic(self, italic: bool):
        self.italic = italic
        self.should_redraw = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.should_redraw = True

    def paintEvent(self, event: QPaintEvent) -> None:
        if self.should_redraw:
            new_font = self.font()
            font_size = self.get_maximum_font_size()
            new_font.setPointSizeF(font_size)
            new_font.setBold(self.bold)
            new_font.setItalic(self.italic)
            self.setFont(new_font)
            self.should_redraw = False

        QLabel.paintEvent(self, event)

    def get_maximum_font_size(self):
        text = self.text()

        widget_rect = self.contentsRect()
        widget_width = widget_rect.width() * self.SCALING_FACTOR
        widget_height = widget_rect.height() * self.SCALING_FACTOR

        font = self.font()
        current_size = self.starting_size

        step = current_size / 2.0

        if step <= self.FONT_PRECISION:
            step = self.FONT_PRECISION * 4.0

        last_tested_size = current_size

        current_height = 0.0
        current_width = 0.0

        if len(text) == 0:
            return current_size

        #  Only stop when step is small enough and new size is smaller than QWidget
        while step > self.FONT_PRECISION or current_height > widget_height or current_width > widget_width:
            last_tested_size = current_size

            font.setPointSizeF(current_size)
            fm = QFontMetricsF(font)

            new_font_size_rect = fm.boundingRect(widget_rect,
                                                 (Qt.TextWordWrap if self.wordWrap() else 0) | self.alignment(), text)

            current_height = new_font_size_rect.height()
            current_width = new_font_size_rect.width()

            # If new font size is too big, decrease it
            if (current_height > widget_height) or (current_width > widget_width):
                current_size -= step
                if step > self.FONT_PRECISION:
                    step /= 2.0

                if current_size <= 0:
                    break
            else:
                current_size += step

        return last_tested_size

    """
    def minimumSizeHint(self) -> QSize:
        # Do not give any size hint as it changes during paintEvent
        return QWidget.minimumSizeHint(self)

    def sizeHint(self) -> QSize:
        # Do not give any size hint as it changes during paintEvent
        return QWidget.sizeHint(self)
    """
