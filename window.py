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
    QMessageBox,
    QComboBox,
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget
)

Difficulty = [(8, 10), (16, 40), (24, 99)]


class Status(IntEnum):
    UPDATE = 0
    PLAYING = 1
    FAILED = 2
    WIN = 3

class Window0(QWidget):

    ended = False
    def __init__(self, controller_dif = None, controller_main = None):
        super().__init__()

        self.initUI(controller_dif, controller_main)


    def initUI(self, controller_dif, controller_main):
        self.difficulty_ind = 0
        self.controller_dif = controller_dif
        self.controller_main = controller_main

        self.setWindowTitle('Выберите уровень сложности')
        self.label = QLabel("Выберите уровень сложности:", self)

        self.difficulty_combo = QComboBox(self)
        self.difficulty_combo.addItem("Easy")
        self.difficulty_combo.addItem("Medium")
        self.difficulty_combo.addItem("Hard")

        self.confirm_button = QPushButton("Подтвердить", self)
        self.confirm_button.clicked.connect(lambda: self.controller_dif.confirm_selection(self))

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.difficulty_combo)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)


        self.setGeometry(800, 300, 300, 150)
        self.show()

    def get_dif(self):
        return self.difficulty_ind
    
    def create_main_window(self, controller):
        window_main = Window1(controller = self.controller_main, dif = self.difficulty_ind)
        self.close()
    def end_choice(self):
        self.ended = True
    
    def is_ended(self):
        return self.ended


class Window1(QMainWindow):
    init = pyqtSignal(object)
    reset = pyqtSignal(object)
    updstatus = pyqtSignal(object, Status)

    status = Status.UPDATE

    def __init__(self, controller=None, dif = 0):
        super().__init__()

        self.initUi(controller, dif)

    def initUi(self, controller, dif):
        self.controller = controller
        self.dif = dif

        
        self.size, self.n_mines = Difficulty[self.dif]

        w = QWidget()
        hb = QHBoxLayout()

        self.mines = QLabel()
        self.mines.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        self.clock = QLabel()
        self.clock.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        f = self.mines.font()
        f.setPointSize(24)
        f.setWeight(75)
        self.mines.setFont(f)
        self.clock.setFont(f)

        self._timer = QTimer()
        self._timer.timeout.connect(lambda: self.controller.update_timer(self))
        self._timer.start(1000)

        self.mines.setText("%03d" % self.n_mines)
        self.clock.setText("000")

        self.button = QPushButton()
        self.button.setFixedSize(QSize(32, 32))
        self.button.setIconSize(QSize(32, 32))
        self.button.setIcon(QIcon("./images/clock-select.png"))
        self.button.setFlat(True)

        self.button.pressed.connect(lambda: self.controller.button_clicked(self))

        label = QLabel()
        label.setPixmap(QPixmap.fromImage(QImage("./images/bomb.png")))
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        hb.addWidget(label)

        hb.addWidget(self.mines)
        hb.addWidget(self.button)
        hb.addWidget(self.clock)

        label = QLabel()
        label.setPixmap(QPixmap.fromImage(QImage("./images/clock-select.png")))
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hb.addWidget(label)

        vb = QVBoxLayout()
        vb.addLayout(hb)

        self.grid = QGridLayout()
        self.grid.setSpacing(5)

        vb.addLayout(self.grid)
        w.setLayout(vb)
        self.setCentralWidget(w)

        self.init.connect(self.controller.init_map)
        self.init.emit(self)

        self.updstatus.connect(self.controller.update_status)
        self.updstatus.emit(self, Status.UPDATE)

        self.reset.connect(self.controller.reset_map)
        self.reset.emit(self)

        self.updstatus.emit(self, Status.UPDATE)

        self.setWindowTitle("САПЁЁЁЁЁЁЁЁР!!!")

        self.show()