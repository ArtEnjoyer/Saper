import time
import random
from enum import IntEnum
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (
    QColor,
    QImage,
)
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import (
    QIcon,
    QPixmap,
    QBrush,
    QPainter,
    QPalette,
    QPen
)
from PyQt5.QtWidgets import (
    QComboBox,
    QMessageBox,
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget
)
#from window import Status, STATUS_ICONS, NUM_COLORS

class Status(IntEnum):
    UPDATE = 0
    PLAYING = 1
    FAILED = 2
    WIN = 3

STATUS_ICONS = {
    Status.UPDATE: "./images/refresh.png",
    Status.PLAYING: "./images/refresh.png",
    Status.FAILED: "./images/refresh.png",
    Status.WIN: "./images/smiley-lol.png",
}

IMG_BOMB = QImage("./images/bomb.png")
IMG_FLAG = QImage("./images/flag.png")
IMG_CLOCK = QImage("./images/clock-select.png")

#стандартные цвета сапёра:
NUM_COLORS = {
    1: QColor("#f44336"),
    2: QColor("#9C27B0"),
    3: QColor("#3F51B5"),
    4: QColor("#03A9F4"),
    5: QColor("#00BCD4"),
    6: QColor("#4CAF50"),
    7: QColor("#E91E63"),
    8: QColor("#FF9800"),
}

class PositionSquare(QWidget):
    expandable = pyqtSignal(int, int)
    clicked = pyqtSignal()
    exploded = pyqtSignal()

    def __init__(self, x, y):
        super().__init__()

        self.setFixedSize(QSize(20, 20))

        self.x = x
        self.y = y

    def reset(self):
        self.is_start = False
        self.is_mine = False
        self.nearby_mines_n = 0

        self.is_revealed = False
        self.is_flagged = False

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)

        r = event.rect()

        if self.is_revealed:
            color = self.palette().color(QPalette.ColorRole.Window)
            outer, inner = color, color
        else:
            outer, inner = Qt.GlobalColor.gray, Qt.GlobalColor.lightGray

        p.fillRect(r, QBrush(inner))
        pen = QPen(outer)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(r)

        if self.is_revealed:
            if self.is_mine:
                p.drawPixmap(r, QPixmap(IMG_BOMB))

            elif self.nearby_mines_n > 0:
                pen = QPen(NUM_COLORS[self.nearby_mines_n])
                p.setPen(pen)
                f = p.font()
                f.setBold(True)
                p.setFont(f)
                p.drawText(
                    r,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                    str(self.nearby_mines_n),
                )

        elif self.is_flagged:
            p.drawPixmap(r, QPixmap(IMG_FLAG))

    def flag(self):
        self.is_flagged = True
        self.update()

        self.clicked.emit()

    def reveal(self):
        self.is_revealed = True
        self.update()

    def click(self):
        if not self.is_revealed:
            self.reveal()
            if self.nearby_mines_n == 0:
                self.expandable.emit(self.x, self.y)

        self.clicked.emit()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton and not self.is_revealed:
            self.flag()

        elif e.button() == Qt.MouseButton.LeftButton:
            self.click()

            if self.is_mine:
                self.exploded.emit()


class Main_Handler(QObject):

    def __init__(self):
        super().__init__()

    def init_map_event(self, window):
        for x in range(0, window.size):
            for y in range(0, window.size):
                pos = PositionSquare(x, y)
                window.grid.addWidget(pos, y, x)
                pos.clicked.connect(lambda: self.trigger_start_event(window))
                pos.expandable.connect(lambda: self.expand_reveal_event(window, x, y))
                pos.exploded.connect(lambda: self.game_over_event(window, Status.FAILED))

    def reveal_map(self, window):
        for x in range(0, window.size):
            for y in range(0, window.size):
                pos = window.grid.itemAtPosition(y, x).widget()
                pos.reveal()

    def update_timer_event(self, window):
        if window.status == Status.PLAYING:
            n_secs = int(time.time()) - window._timer_start_nsecs
            window.clock.setText("%03d" % n_secs)

    def button_clicked_event(self, window):
        #print("UPDATE...")
        self.update_status_event(window, Status.UPDATE)
        self.reset_map_event(window)

    def trigger_start_event(self, window):
        #if window.status != Status.PLAYING and window.status != Status.:
        if window.status == Status.UPDATE:
            self.update_status_event(window, Status.PLAYING)
            window._timer_start_nsecs = int(time.time())
    
    def expand_reveal_event(self, window, x, y):
        for xi in range(max(0, x - 1), min(x + 2, window.size)):
            for yi in range(max(0, y - 1), min(y + 2, window.size)):
                pos = window.grid.itemAtPosition(yi, xi).widget()
                if not pos.is_mine:
                    pos.click()
    
    def game_over_event(self, window, status):
        self.update_status_event(window, status)
        self.reveal_map(window)

    def reset_map_event(self, window):
        #print('RESET...')
        for x in range(0, window.size):
            for y in range(0, window.size):
                pos = window.grid.itemAtPosition(y, x).widget()
                pos.reset()

        positions = []
        while len(positions) < window.n_mines:
            x, y = (random.randint(0, window.size - 1), random.randint(0, window.size - 1),)
            if (x, y) not in positions:
                pos = window.grid.itemAtPosition(y, x).widget()
                pos.is_mine = True
                positions.append((x, y))

        def get_neighbour_mines(x, y):
            positions = self.get_surrounding(window, x, y)
            n_mines = sum(1 if w.is_mine else 0 for w in positions)

            return n_mines

        for x in range(0, window.size):
            for y in range(0, window.size):
                pos = window.grid.itemAtPosition(y, x).widget()
                pos.nearby_mines_n = get_neighbour_mines(x, y)

    def update_status_event(self, window, status):
        window.status = status
        window.button.setIcon(QIcon(STATUS_ICONS[window.status]))

    def get_surrounding(self, window, x, y):
        positions = []

        for xi in range(max(0, x - 1), min(x + 2, window.size)):
            for yi in range(max(0, y - 1), min(y + 2, window.size)):
                positions.append(window.grid.itemAtPosition(yi, xi).widget())

        return positions

class Dif_Choice_Handler(QObject):

    dif_closed = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def confirm_selection_event(self, window):
        selected_difficulty = window.difficulty_combo.currentText()
        QMessageBox.information(window, "Выбор сложности", f"Вы выбрали: {selected_difficulty}")
        window.difficulty_ind = window.difficulty_combo.currentIndex()
        #print('Selected difficulty index: ', window.difficulty_ind)
        window.end_choice()
        self.dif_closed.connect(window.create_main_window)
        self.dif_closed.emit(window.controller_main)