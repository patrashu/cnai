from PySide6.QtCore import Slot
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import (
    QPushButton, QFrame, QLabel, QFrame, QVBoxLayout, QHBoxLayout
)

from ..signals import all_signals
from .camthread import CamThread


SAMPLE_COUNT = 10000
RESOLUTION = 4


class StreamingCam(QFrame):
    def __init__(self) -> None:
        super().__init__()

        self.setStyleSheet("background-color: #1e1e1e;") 
        self.device = None
        self.config = None
        self.color_control = None
        self.base_path = None

        self.main_layout = QVBoxLayout()
        self.frame = QLabel("Streaming Cam1")
        self.frame.setStyleSheet("""
            border-color: white;        
        """)
        self.frame.setAlignment(Qt.AlignCenter)
        self.frame.setFixedHeight(950)
        
        self.layout_btn = QHBoxLayout()
        self.layout_btn.setAlignment(Qt.AlignCenter)
        self.btn_open = QPushButton("Run")
        self.btn_stop = QPushButton("Stop")
        self.btn_open.setFixedSize(200, 40)
        self.btn_stop.setFixedSize(200, 40)

        self.btn_open.clicked.connect(self.openCam)
        self.btn_stop.clicked.connect(self.closeCam)
        self.btn_open.setStyleSheet("""
            QPushButton:hover {
                border-color: "white";
            }
        """)
        self.btn_stop.setStyleSheet("""
            QPushButton:hover {
                border-color: "white";
            }
        """)
        self.layout_btn.addWidget(self.btn_open)
        self.layout_btn.addWidget(self.btn_stop)

        self.main_layout.addWidget(self.frame)
        self.main_layout.addLayout(self.layout_btn)
        all_signals.streaming_cam.connect(self.setFirstCam)

        self.setLayout(self.main_layout)

    def openCam(self):
        self.th1 = CamThread()
        self.th1.is_run = True
        self.th1.start()

    def closeCam(self):
        self.th1.is_run = False
        self.th1.quit()

    @Slot()
    def setFirstCam(self, value):
        self.frame.setPixmap(QPixmap.fromImage(value))