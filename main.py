import random
import sys
import time
from enum import IntEnum
import PyQt5.QtWidgets
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
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from window import Window0
from handler import Main_Handler, Dif_Choice_Handler

class Controller():
    closeApp = pyqtSignal()
    def __init__(self, handler):
        super().__init__()
        self.handler = handler

    def init_map(self, window):
        self.handler.init_map_event(window)

    def button_clicked(self, window):
        self.handler.button_clicked_event(window)

    def trigger_start(self, window):
        self.handler.trigger_start_event(window)

    def expand_reveal(self, window, x, y):
        self.handler.expand_reveal_event(window, x, y)

    def game_over(self, window):
        self.handler.game_over_event(window)

    def update_timer(self, window):
        self.handler.update_timer_event(window)

    def reset_map(self, window):
        self.handler.reset_map_event(window)

    def update_status(self, window, status):
        self.handler.update_status_event(window, status)


class Controller_dif(QObject):

    def __init__(self, handler):
        super().__init__()
        self.handler = handler

    def confirm_selection(self, window):
        self.handler.confirm_selection_event(window)

if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication([])
    handler = Main_Handler()
    controller = Controller(handler)
    dif_handler = Dif_Choice_Handler()
    dif_controller = Controller_dif(dif_handler)
    dif_choice = Window0(controller_dif = dif_controller, controller_main = controller)
    app.exec_()